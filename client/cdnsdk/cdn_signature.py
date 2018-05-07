#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import base64
import urllib
import httplib
import hashlib
import time

"""
os = 'xp'
eth0_ip = '192.168.1.1'

params = urllib.urlencode({"os": os, "eth0_ip": eth0_ip})
auth = base64.b64encode('cleartext username'+ ':'+ 'cleartext passwords')
headers = {"Authorization": "Basic "+ auth}
conn = httplib.HTTPConnection("10.10.10.10")
conn.request("POST","/v3/api/distribution", params, headers)
response = conn.getresponse()
#print response.status
print response.read().strip()
"""


class Signature:

	def __init__(self):
		# self.method = method
		# self.url = url
		# self.body = body
		pass

"""
	def get_signature(self, method, url, body):



		access_key = '1234567890abcdef'
		# credential = "f9bfc5dd7f24ea560d1593093b118c3d/20160726155000/dnioncloud"
		time_now = time.strftime("%Y%m%d%M%H%S", time.localtime())
		print time_now
		credential = "f9bfc5dd7f24ea560d1593093b118c3d" + "/" + time_now + "/" + "dnioncloud"
		print credential
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
		print authorization
"""


if "__name__" == "__main__":

	body_standard = """
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

	print body_standard
	print "test begin!!"
	# Signature().get_signature("POST", "/v3/api/distribution", body_standard)

