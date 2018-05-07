# -*- coding: utf-8 -*-

import unittest

from pprint import pprint

from cdsoss.db.sqlalchemy import api as dbapi
import time
import logging
logging.basicConfig(filename='test.log', level=logging.DEBUG)

            
class TestRegion_01_dbapi(unittest.TestCase):
    def setUp(self):
        region = {
            'name': 'beijing',
            'mgmt_ip': 'testtenants.hcp-dev.capitalonline.net',
            'mgmt_port': 443L,
            'mgmt_user': 'admin',
            'mgmt_passwd': 'P@ssw0rd!!',
        }
        update_region = {
            'name': 'beijing1',
            'mgmt_ip': 'testtenants.hcp-dev.capitalonline.net1',
            'mgmt_port': 4431L,
            'mgmt_user': 'admin1',
            'mgmt_passwd': 'P@ssw0rd!!1',
            'enable': False
        }
        self.record = region
        self.update_record = update_region
        self.test_id = []
    
    def tearDown(self):
        pprint('====---====')
        pprint(self.test_id)
    
    def test_1_10_create_region_good(self):
        r = dbapi.region_create(self.record)
        self.test_id.append(r['id'])
        self.assertTrue(type(r) == dict)
        self.assertTrue(len(r) == 11)
    
    def test_1_20_update_region_good(self):
        r = dbapi.region_create(self.record)
        self.test_id.append(r['id'])
        dbapi.region_update(r['id'], self.update_record)
        ur = dbapi.region_get(r['id'])
        pprint(ur)
        for k in self.update_record.keys():
            pprint(self.update_record[k])
            self.assertEquals(ur[k], self.update_record[k])
            #self.assertTrue(ur[k] == self.update_record[k])
        
    def test_1_30_delete_region_good(self):
        r = dbapi.region_create(self.record)
        dbapi.region_delete(r['id'])
        dr = dbapi.region_get(r['id'], force_show_deleted=True)
        pprint(dr)
        self.assertTrue(dr['deleted'] == True)
        self.assertTrue(dr['deleted_at'] != None)
        
    def test_1_40_list_region_good(self):
        rl = dbapi.region_list()
            

if __name__ == '__main__':
    unittest.main()