#!/usr/bin/env python
# coding: utf-8
# author: liusheng

from xmltodict import parse, unparse, ParsingInterrupted
from json import loads, dumps
import base64
import urllib
import httplib
import hashlib
import time


class Httpclient:
	def __init__(self):
		self.uri = "dcloud.dnion.com"

	def http_post(self, url, body, authorization):
		headers = {"Authorization": authorization, "Content-type": "application/xml"}
		conn = httplib.HTTPConnection(self.uri)
		conn.request(method="POST", url=url, headers=headers, body=body)
		response = conn.getresponse()
		# print response.status, response.reason
		# print response.read().strip()
		return response

	def http_get(self, url, params, auth):
		headers = {"Authorization": auth, "Content-type": "application/xml"}
		conn = httplib.HTTPConnection(self.uri)
		conn.request(method="GET", url=url, headers=headers)
		response = conn.getresponse()
		# print response.status, response.reason
		# print response.read().strip()
		return response

	def http_put(self, url, body, auth):
		headers = {"Authorization": auth, "Content-type": "application/xml"}
		conn = httplib.HTTPConnection(self.uri)
		try:
			conn.request(method="PUT", url=url, headers=headers, body=body)
			response_body = conn.getresponse()
			print response_body
		except Exception as e:
			print e
		# print response.status, response.reason
		# print response.read().strip()
		return response_body

	def http_delete(self, url, params, auth):
		headers = {"Authorization": auth, "Content-type": "application/xml"}
		conn = httplib.HTTPConnection(self.uri)
		conn.request(method="DELETE", url=url, headers=headers)
		response = conn.getresponse()
		# print response.status, response.reason
		# print response.read().strip()
		return response

	def get_signature(self, method, url, body=None):
		"""
		:param method: GET POST PUT DELETE
		:param url: api path,maybe include some params in GET request
		:param body: the body in POST or PUT request,format is XML
		:return: authorization str
		"""
		access_key = '1234567890abcdef'
		# credential = "f9bfc5dd7f24ea560d1593093b118c3d/20160726155000/dnioncloud"
		time_now = time.strftime("%Y%m%d%H%M%S", time.localtime())
		#print time_now
		credential = "f9bfc5dd7f24ea560d1593093b118c3d" + "/" + time_now + "/" + "dnioncloud"
		#print credential
		m1 = hashlib.md5()
		m1.update(body)

		data_list = []
		data_list.append(method + '\n')
		data_list.append(access_key + '\n')
		data_list.append(url + '\n')
		data_list.append(m1.hexdigest() + '\n')
		data_list.append(credential)
		m2 = hashlib.md5()
		for item in data_list:
			m2.update(item)
		signature = m2.hexdigest()
		authorization = "Algorithm=md5,Credential=" + credential + ",Signature=" + signature
		#print authorization
		return authorization


class Distribution(Httpclient):

	def __init__(self):
		self.http_client = Httpclient()

	def test_standard_xml(self):

		xml_standard = """
			<Distribution>
				<Customer>
					<Id>436bd8ed</Id>
				</Customer>
				<Platform>
					<Type>WEB</Type>
				</Platform>
				<DistributionConfig>
					<Comment>test captical net</Comment>
					<NotUse>False</NotUse>
					<Domains>
						<Domain>
							<Aliases>abcdef.s3.captical.net</Aliases>
							<TestUrls>http://abcdef.s3.captical.net</TestUrls>
							<TestCodes>403</TestCodes>
							<Origin>
								<OriginProtocol>http</OriginProtocol>
								<OriginRewrite>www.renren.com</OriginRewrite>
								<OriginSource>www.renren.com</OriginSource>
							</Origin>
						</Domain>
					</Domains>

					<Logging>
						<Analytics>True</Analytics>
						<Format>Original</Format>
						<SplitTime>1h</SplitTime>
					</Logging>
				</DistributionConfig>

			</Distribution>
			"""
		dict = parse(xml_standard)
		print dict
		json_data = json.dumps(dict, sort_keys=True, indent=4)

		print type(json_data)
		print json_data

	def create_distribution_xml(self, dict):
		"""
		dict = {"domain":"test.dafasd.com",
				"source":"test.hpcyunidc.com",
				"type":"WEB",
				"comment":"test the CDN domain accelerate"}
		"""

		dict_domain = {
		"Distribution": {
			"Customer": {
				"Id": "436bd8ed"
			},
			"Platform": {
				"Type": dict.get("type")
			},
			"DistributionConfig": {
				"Comment": dict.get("comment"),
				"NotUse": "False",
				"Domains": {
					"Domain": {
						"Aliases": dict.get("domain"),
						"TestUrls": "http://" + dict.get("domain"),
						"TestCodes": "403",
						"Origin": {
							"OriginProtocol": "http",
							"OriginRewrite": dict.get("source"),
							"OriginSource": dict.get("source")
						}
					}
				},
				"Logging": {
					"Analytics": "True",
					"Format": "Original",
					"SplitTime": "1h"
				}
			}
		}
	}
		print type(dict_domain)
		print dict_domain

		xml = unparse(dict_domain, full_document=False)
		print xml
		return xml

	def create_distribution(self, dis_para):

		body_xml = Distribution().create_distribution_xml(dis_para)
		authorization = self.http_client.get_signature("POST", "/v3/api/distribution", body_xml)
		response = self.http_client.http_post(url="/v3/api/distribution", body=body_xml, authorization=authorization)
		distribution_id = ""

		if response.status == 201:
			response_xml = response.read().strip()
			response_dict = parse(response_xml)
			print response_dict["Distribution"]
			distribution_id = response_dict["Distribution"].get("Id", None)
			if distribution_id:
				print ("the distribution id is %s "%(distribution_id))
		else:
			print "failed to create the distribution!"
			# raise except !!!
		return distribution_id

	def modify_cache_policy(self, cache_policy, domain_id):
		try:
			domain_config = Distribution().get_distribution(domain_id)
		except Exception as e:
			print "get the domain config failed!!"
			return
		else:
			domain_config["Distribution"]["DistributionConfig"]["CacheBehaviorTop"] = cache_policy
			# delete the extra config, the key is not needed when modify CDN domain
			del domain_config["Distribution"]["Id"]
			del domain_config["Distribution"]["Status"]
			del domain_config["Distribution"]["LastModifiedTime"]

			cache_xml = unparse(domain_config, full_document=False)
			authorization = self.http_client.get_signature("PUT", "/v3/api/distribution/"+domain_id, cache_xml)
			print("authorization in modify_cache_policy %s"%authorization)
			print("cache_xml in modify_cache_policy %s"%cache_xml)
			response = self.http_client.http_put(url="/v3/api/distribution/"+domain_id, body=cache_xml, auth=authorization)
			print response

	def modify_acl_policy(self, acl_policy, domain_id):
		try:
			domain_config = Distribution().get_distribution(domain_id)
		except Exception as e:
			print "get the domain config failed!!"
			return
		else:
			domain_config["Distribution"]["DistributionConfig"]["AclBehaviorsTop"] = acl_policy
			# delete the extra config, the key is not needed when modify CDN domain
			del domain_config["Distribution"]["Id"]
			del domain_config["Distribution"]["Status"]
			del domain_config["Distribution"]["LastModifiedTime"]

			acl_xml = unparse(domain_config, full_document=False)
			authorization = self.http_client.get_signature("PUT", "/v3/api/distribution/"+domain_id, acl_xml)
			print("authorization in modify_acl_policy %s"%authorization)
			print("acl_xml in modify_acl_policy %s"%acl_xml)
			response = self.http_client.http_put(url="/v3/api/distribution/"+domain_id, body=acl_xml, auth=authorization)
			return response

	def delete_distribution_xml(self, dis_id):
		authorization = self.http_client.get_signature(method="DELETE", url="/v3/api/distribution/" + dis_id, body="")
		response = self.http_client.http_delete(url="/v3/api/distribution/" + dis_id, params=None, auth=authorization)
		print response.status, response.reason

		if response.status == 200:
			response_xml = response.read().strip()
			response_dict = parse(response_xml)
			print response_dict
			# return response
		else:
			print ("failed to get the distribution %s"%dis_id)

	def enable_distribution_xml(self, dis_id):
		authorization = self.http_client.get_signature(method="PUT", url="/v3/api/distribution/" + dis_id + "/enable", body="")
		response = self.http_client.http_put(url="/v3/api/distribution/" + dis_id + "/enable", body="", auth=authorization)
		print response.status, response.reason

		if response.status == 200:
			response_xml = response.read().strip()
			response_dict = parse(response_xml)
			print response_dict
			# return response
		else:
			print ("failed to enable the distribution %s"%dis_id)

	def disable_distribution_xml(self, dis_id):
		authorization = self.http_client.get_signature(method="PUT", url="/v3/api/distribution/" + dis_id + "/disable", body="")
		response = self.http_client.http_put(url="/v3/api/distribution/" + dis_id + "/disable", body="", auth=authorization)
		print response.status, response.reason
		ret = {}

		if response.status == 200:
			# if response.getheader("content-type", None) == "application/xml":
			response_body = response.read().strip()
			#response_dict = parse(response_body)
			print response_body
		else:
			print ("failed to enable the distribution %s"%dis_id)

	def get_distribution(self, dis_id):
		authorization = self.http_client.get_signature(method="GET", url="/v3/api/distribution/" + dis_id, body="")
		response = self.http_client.http_get(url="/v3/api/distribution/" + dis_id, params=None, auth=authorization)
		print response.status, response.reason

		dis_status = {"domain_id": dis_id, "status": ""}
		if response.status == 200:
			response_xml = response.read().strip()
			response_dict = parse(response_xml)
			dis_status["status"] = response_dict["Distribution"]['Status']
			# print response_dict["Distribution"]["DistributionConfig"]
			# print "/r/n"
			print dis_status
			# common_dict = loads(dumps(response_dict))

			# return response
		else:
			print ("failed to get the distribution %s"%dis_id)
		return response_dict

	def convert_list_to_str(self,url_list):
		for url in url_list:
			url_list[i]= str(url+'\n')
			i=i+1
		url_list_str = "".join(url_list)
		return url_list_str

	def distribution_flush_cache(self, url_list):
		# url_list: format is a python List
		authorization = self.http_client.get_signature(method="POST", url="/v3/api/push", body=url_list)
		response_body = self.http_client.http_post(url="/v3/api/push", body=url_list, authorization=authorization)
		print response_body.status, response_body.reason

	def setup_cache_dict(self, cache_dict):
		# 该接口的具体实现要和前端一致，暂不实现
		pass

	def setup_acl_dict(self, acl_dict):
		# acl：分为IP地址和ip地址段2种形式，都可以设置为黑名单和白名单
		# DefaultAclBehavior:（默认的策略,包括ACL和防盗链），包括了IP地址和refer2种形式，暂时不支持同时配置
		# AclBehaviors：（具体的防盗链策略),只有refer形式的，除了黑名单和白名单，还可以设置通配符
		dict_acl = {
			"AclBehaviorsTop":{
				"DefaultAclBehavior":
				{
					"IsOpen": "True",
					"WhiteList":"www.baidu.com",
					"BlackList":"www.sina.com.cn",

					"DenyIpList":"1.1.12.1",
					"DenyIpPeriods":{"DenyIpPeriod": [{"DenyIpStart":"122.1.1.1","DenyIpEnd": "122.255.255.255"},
													 {"DenyIpStart":"123.1.1.1","DenyIpEnd": "123.255.255.255"}]},

					"AllowIpList":"2.1.12.1",
					"AllowIpPeriods": {"AllowIpPeriod": [{"AllowIpStart":"125.1.1.1","AllowIpEnd":"124.255.255.255"},
													    {"AllowIpStart":"125.1.1.1","AllowIpEnd":"125.255.255.255"}]},
				},
				"AclBehaviors":
				{
					"AclBehavior": [{"IsOpen": "True","AllowNullReferer":"True",
									"PathPattern":"/.*txt","WhiteList":"www.renren.com",
									"BlackList":"www.sohu.com"},
									{"IsOpen": "True","AllowNullReferer":"False",
									"PathPattern":"/.*txt","WhiteList":"www.vip.com",
									"BlackList":"www.yun-idc.com"}]
				}
			}
		}

		setup_dict = {}
		if acl_dict["DefaultAclBehavior"]:
			default_dict = {}
			default_dict_refer = {}

			whitelist = acl_dict["DefaultAclBehavior"].get("WhiteList")
			blacklist = acl_dict["DefaultAclBehavior"].get("BlackList")
			"""
			if whitelist:
				default_dict_refer = dict("WhiteList",whitelist)

			default_dict_refer = dict("BlackList","") if acl_dict["DefaultAclBehavior"].get("BlackList")
			"""
			default_dict = {
				"DefaultAclBehavior":
				{
					"IsOpen": "True",
					"WhiteList":"www.baidu.com",
					"BlackList":"www.sina.com.cn",

					"DenyIpList":"1.1.12.1",
					"DenyIpPeriods":{"DenyIpPeriod": [{"DenyIpStart":"122.1.1.1","DenyIpEnd": "122.255.255.255"},
													 {"DenyIpStart":"123.1.1.1","DenyIpEnd": "123.255.255.255"}]},

					"AllowIpList":"2.1.12.1",
					"AllowIpPeriods": {"AllowIpPeriod": [{"AllowIpStart":"125.1.1.1","AllowIpEnd":"124.255.255.255"},
													    {"AllowIpStart":"125.1.1.1","AllowIpEnd":"125.255.255.255"}]},
				}
			}



if __name__ == '__main__':

	dict = {"domain": "test.capticalonlinecode7.com",
		"source": "test.testtenants.hcp-dev.capitalonline.net",
		"type": "WEB",
		"comment": "test the CDN domain accelerate"}
	"""
	body_xml = Distribution().create_distribution_xml(dict)
	authorization = Httpclient().get_signature("POST", "/v3/api/distribution", body_xml)
	response = Httpclient().http_post(url="/v3/api/distribution", body=body_xml, authorization=authorization)
	if response.status == 201:
		response_xml = response.read().strip()
		response_dict = parse(response_xml)
		print response_dict["Distribution"]
		distribution_id = response_dict["Distribution"].get("Id", None)
		if distribution_id:
			print ("the distribution id is %s "%(distribution_id))
	else:
		print "failed to create the distribution!"
		# raise except !!!
	"""

	"""
	domain_config = Distribution().get_distribution("bcb7536581ce17a71afa89b6e52e62b4")
	print domain_config["Distribution"]["DistributionConfig"]["CacheBehaviorTop"]
	domain_config["Distribution"]["DistributionConfig"]["CacheBehaviorTop"] = dict_cache
	print domain_config["Distribution"]["DistributionConfig"]

	common_dict = loads(dumps(domain_config))
	print common_dict

	xml = unparse(domain_config, full_document=False)
	print xml
	"""

	# response_body = Distribution().modify_cache_policy(dict_cache, "bcb7536581ce17a71afa89b6e52e62b4")
	response_body = Distribution().modify_acl_policy(dict_acl, "bcb7536581ce17a71afa89b6e52e62b4")
	# response = Distribution().get_distribution("bcb7536581ce17a71afa89b6e52e62b4")
	# print response.status, response.reason
	# response_xml = response.read().strip()
	print response_body.status, response_body.reason
	# Distribution().enable_distribution_xml("9dbd78330dd5f6ee1b3e78d20a3995ba")
	# Distribution().disable_distribution_xml("9dbd78330dd5f6ee1b3e78d20a3995ba")
	# Distribution().delete_distribution_xml("9dbd78330dd5f6ee1b3e78d20a3995ba")




