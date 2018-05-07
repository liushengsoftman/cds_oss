# -*- coding: utf-8 -*-

import unittest

from pprint import pprint
from cdsoss.client.cdnsdk import Distribution
import time
import logging
logging.basicConfig(filename='test.log', level=logging.DEBUG)


class TestCdn_Api(unittest.TestCase):

	def test_cdn_acl_api(self):
		dict_acl = {
			# "AclBehaviorsTop":{
				"DefaultAclBehavior":
				{
					"IsOpen": "True",
					# "WhiteList":"www.baidu.com",
					"BlackList":"www.sina.com.cn",
				},
				"AclBehaviors":
				{
					"AclBehavior": [{"IsOpen": "True","AllowNullReferer":"True",
									"PathPattern":"/.*txt",
									"BlackList":"www.sohu.com"},
									{"IsOpen": "True","AllowNullReferer":"False",
									"PathPattern":"/.*txt",
									"BlackList":"www.yun-idc.com"}]
				}
			# }
		}
		response_body = Distribution().modify_acl_policy(dict_acl, "bcb7536581ce17a71afa89b6e52e62b4")
		self.assertEquals(response_body.status, "201")
		self.assertEquals(response_body.reason, "Updated")

	def test_cdn_cache_api(self):
		dict_cache = {
				"CacheBehaviors":
					{"CacheBehavior":
						[
							{"PathPattern": "/*\.jpg", "NeverCache": "False", "CacheControl": "Ignore",
								"ForwardedValues": {"QueryString":"False"}, "CacheTime": "300"},

							{"PathPattern": "/*\.txt", "NeverCache": "False", "CacheControl": "Ignore",
								"ForwardedValues": {"QueryString":"False"}, "CacheTime": "600"},
						]
					}
		}
		response_body = Distribution().modify_cache_policy(dict_cache, "bcb7536581ce17a71afa89b6e52e62b4")
		self.assertEquals(response_body.status, "201")
		self.assertEquals(response_body.reason, "Updated")