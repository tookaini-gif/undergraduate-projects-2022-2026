"""End-to-end HTTP tests on an isolated database; no external services."""
import base64
import http.cookiejar
import importlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


class Client:
    def __init__(self,url):
        self.url=url
        self.csrf=''
        self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(self,path,data=None,headers=None):
        hdr={'Content-Type':'application/json','X-CSRF-Token':self.csrf}
        if headers: hdr.update(headers)
        req=urllib.request.Request(self.url+path,data=json.dumps(data).encode() if data is not None else None,headers=hdr)
        try:
            with self.opener.open(req,timeout=10) as r:
                raw=r.read()
                return r.status,json.loads(raw) if 'application/json' in r.headers.get('Content-Type','') else raw
        except urllib.error.HTTPError as r:
            return r.code,json.loads(r.read())

    def login(self,name,password='icure2026'):
        code,result=self.request('/api/login',{'username':name,'password':password})
        if code==200: self.csrf=result['csrf']
        return code,result


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='icure-tests-')
        cls.old_env=os.environ.get('ICURE_DATA_DIR')
        os.environ['ICURE_DATA_DIR']=cls.temp.name
        import database
        import agent
        import server
        cls.db,cls.agent,cls.server=database,agent,server
        cls.db.init()
        cls.http=server.make_server(0)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.http.server_port}'
        cls.p=Client(cls.url);cls.d=Client(cls.url)
        assert cls.p.login('demo_patient')[0]==200
        assert cls.d.login('demo_doctor')[0]==200

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close();cls.thread.join(timeout=5)
        if cls.old_env is None: os.environ.pop('ICURE_DATA_DIR',None)
        else: os.environ['ICURE_DATA_DIR']=cls.old_env
        cls.temp.cleanup()

    def test_01_demo_initialization_and_passwords(self):
        with self.db.connect() as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM users').fetchone()[0], 2)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM appointments').fetchone()[0], 0)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM relations').fetchone()[0], 1)
            for row in c.execute('SELECT password FROM users'):
                self.assertTrue(row['password'].startswith('pbkdf2$'))
            self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.db.init()
        with self.db.connect() as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM users').fetchone()[0], 2)

    def test_02_auth_and_host_protection(self):
        c=Client(self.url)
        self.assertEqual(c.request('/api/me')[0],401)
        self.assertEqual(c.login('demo_patient','wrong')[0],401)
        self.assertEqual(c.login("' OR 1=1 --",'wrong')[0],401)
        self.assertEqual(self.p.request('/api/me')[0],200)
        self.assertEqual(self.p.request('/api/profile',{},headers={'X-CSRF-Token':''})[0],403)
        self.assertEqual(self.p.request('/api/healthcheck',headers={'Host':'evil.example'})[0],403)
        self.assertEqual(c.request('/api/login',{'username':'demo_patient','password':'icure2026'},headers={'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.p.request('/data/legacy.sqlite')[0],404)
        self.assertEqual(self.p.request('/api/patients')[0],403)
        self.assertEqual(self.d.request('/api/health')[0],403)
        self.assertEqual(self.p.request('/api/stats')[0],403)

    def test_03_registration_profile_transaction(self):
        c=Client(self.url)
        payload={'username':'new_patient','password':'abcdef12','name':'新患者','role':'patient','age':22}
        code,result=c.request('/api/register',payload)
        self.assertEqual(code,200);c.csrf=result['csrf']
        self.assertEqual(c.request('/api/register',payload)[0],409)
        profile={'name':'更新姓名','username':'new_patient','age':23,'gender':'女','telephone':'123','address':'本机测试','new_password':'newpass123','old_password':'wrong'}
        self.assertEqual(c.request('/api/profile',profile)[0],400)
        self.assertEqual(c.request('/api/me')[1]['user']['profile']['name'],'新患者')
        profile['old_password']='abcdef12'
        self.assertEqual(c.request('/api/profile',profile)[0],200)
        self.assertEqual(c.login('new_patient','newpass123')[0],200)
        self.assertEqual(c.request('/api/logout',{})[0],200)
        self.assertEqual(c.request('/api/me')[0],401)

    def test_04_booking_conflict_cancel_and_acl(self):
        me=self.d.request('/api/me')[1]['user'];did=me['entity_id']
        date=(datetime.now(self.db.TZ).date()+timedelta(days=3)).isoformat()
        booking={'doctor_id':did,'date':date,'time':'09:00','summary':'喉咙不适，待医生核实'}
        code,result=self.p.request('/api/appointments/book',booking)
        self.assertEqual(code,200);aid=result['id']
        self.assertEqual(self.p.request('/api/appointments/book',booking)[0],409)
        self.assertEqual(self.d.request('/api/appointments/book',booking)[0],403)
        slots=self.p.request(f'/api/slots?doctor_id={did}&date={date}')[1]
        self.assertFalse(next(s for s in slots if s['time']=='09:00')['available'])
        self.assertTrue(any(a['id']==aid for a in self.d.request('/api/appointments')[1]))
        stranger=Client(self.url);stranger.login('new_patient','newpass123')
        self.assertEqual(stranger.request('/api/appointments/cancel',{'id':aid})[0],403)
        self.assertEqual(self.p.request('/api/appointments/cancel',{'id':aid})[0],200)
        self.assertTrue(next(s for s in self.p.request(f'/api/slots?doctor_id={did}&date={date}')[1] if s['time']=='09:00')['available'])
        self.assertEqual(self.p.request('/api/appointments/book',{**booking,'date':'2020-01-01'})[0],400)
        self.assertEqual(self.p.request('/api/appointments/book',{**booking,'time':'99:99'})[0],400)

    def test_05_patient_record_permissions(self):
        records=self.d.request('/api/patients')[1]
        record=records[0]
        payload={'id':record['id'],'symptoms':'问诊症状','advice':'复诊建议','prescription':'医生记录','status':'治疗中'}
        self.assertEqual(self.p.request('/api/patients/update',payload)[0],403)
        self.assertEqual(self.d.request('/api/patients/update',payload)[0],200)
        self.assertEqual(self.d.request('/api/patients/update',{**payload,'id':999999})[0],403)
        own=self.p.request('/api/dashboard')[1]['relations']
        self.assertTrue(any(r['advice']=='复诊建议' for r in own))
        self.assertEqual(self.d.request('/api/stats')[0],200)

    def test_06_messages_and_private_attachments(self):
        did=self.d.request('/api/me')[1]['user']['id']
        message={'receiver':did,'text':'<script>alert(1)</script>','file':base64.b64encode(b'private test attachment').decode(),'filename':'病例.txt'}
        code,result=self.p.request('/api/messages/send',message)
        self.assertEqual(code,200);mid=result['id']
        self.assertEqual(self.d.request('/api/attachment/'+str(mid))[1],b'private test attachment')
        stranger=Client(self.url);stranger.login('new_patient','newpass123')
        self.assertEqual(stranger.request('/api/attachment/'+str(mid))[0],404)
        pid=self.p.request('/api/me')[1]['user']['id']
        received=self.d.request('/api/messages?peer='+str(pid))[1]
        self.assertEqual(received[-1]['text'],message['text'])
        self.assertEqual(self.p.request('/api/messages/send',{'receiver':pid,'text':'bad'})[0],400)

    def test_07_health_validation_history(self):
        code,result=self.p.request('/api/health/save',{'height':170,'weight':65,'heart_rate':70,'body_fat':20,'vision':90})
        self.assertEqual(code,200);self.assertAlmostEqual(result['bmi'],22.49)
        self.assertEqual(len(self.p.request('/api/health')[1]),1)
        for height in (0,-5,'bad','NaN'):
            self.assertEqual(self.p.request('/api/health/save',{'height':height,'weight':65})[0],400)

    def test_08_agent_offline_actions_require_confirmation(self):
        self.p.request('/api/agent/clear',{})
        before=len(self.p.request('/api/appointments')[1])
        code,r=self.p.request('/api/agent/chat',{'message':'喉咙不舒服两天了，想预约明天的耳鼻喉科','use_profile':True})
        self.assertEqual(code,200);self.assertEqual(r['mode'],'offline');self.assertEqual(r['department'],'ENT')
        self.assertTrue(r['doctors']);self.assertFalse(r['urgent']);self.assertTrue(r['trace'])
        self.assertEqual(len(self.p.request('/api/appointments')[1]),before)
        self.assertIn('本人档案',r['summary'])
        self.assertEqual(self.p.request('/api/agent/chat',{'message':'我胸痛并且呼吸困难'})[1]['urgent'],True)
        urgent=self.p.request('/api/agent/chat',{'message':'帮我预约明天'})[1]
        self.assertTrue(urgent['urgent']);self.assertFalse(urgent['doctors'])
        self.p.request('/api/agent/clear',{})
        negative=self.p.request('/api/agent/chat',{'message':'没有胸痛，没有呼吸困难，喉咙不舒服'})[1]
        self.assertFalse(negative['urgent'])
        self.assertEqual(len(self.d.request('/api/agent/history')[1]),0)

    def test_09_online_opt_in_fallback_and_secrets(self):
        self.assertEqual(self.p.request('/api/agent/chat',{'message':'准备就诊','online':True})[0],400)
        self.assertEqual(self.p.request('/api/agent/config',{'endpoint':'http://evil.example/v1','model':'test','key':'secret'})[0],400)
        self.assertEqual(self.p.request('/api/agent/config',{'endpoint':'http://127.0.0.1:1/v1','model':'test','key':'secret'})[0],200)
        self.assertNotIn('secret',json.dumps(self.p.request('/api/me')[1]))
        with patch.object(self.agent,'online',side_effect=ValueError('private provider body')) as call:
            code,result=self.p.request('/api/agent/chat',{'message':'准备就诊','online':False})
            self.assertFalse(call.called)
            code,result=self.p.request('/api/agent/chat',{'message':'准备就诊','online':True})
            self.assertTrue(call.called);self.assertTrue(result['online_error']);self.assertEqual(result['mode'],'offline')
            self.assertNotIn('private provider body',json.dumps(result))
        self.assertEqual(self.p.request('/api/agent/config',{'clear':True})[0],200)

    def test_10_online_parser_does_not_override_urgent(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self,n): return json.dumps({'choices':[{'message':{'content':json.dumps({'message':'伪造正常回复','summary':'summary','questions':['q']})}}]}).encode()
        class FakeOpener:
            def open(self,req,timeout):
                self_test.assertEqual(req.full_url,'https://provider.example/v1/chat/completions')
                return FakeResponse()
        self_test=self
        with self.db.connect() as c:
            user=c.execute("SELECT * FROM users WHERE username='demo_patient'").fetchone()
            base=self.agent.offline(c,user,'我胸痛',[],False)
        with patch('urllib.request.build_opener',return_value=FakeOpener()):
            result=self.agent.online(base,'我胸痛',[],{'endpoint':'https://provider.example/v1','model':'test','key':'secret'})
        self.assertTrue(result['urgent']);self.assertIn('120',result['message']);self.assertNotIn('伪造',result['message'])

    def test_11_export_and_static_pages(self):
        code,export=self.p.request('/api/backup',{})
        self.assertEqual(code,200);self.assertNotIn('password',export['data']['user'])
        self.assertEqual(export['data']['user']['role'],'patient')
        for p in ('/','/app.js','/styles.css','/assets/hospital.jpg','/assets/eyetest.jpg'):
            self.assertEqual(self.p.request(p)[0],200)
        self.assertEqual(self.p.request('/../server.py')[0],404)


if __name__=='__main__': unittest.main(verbosity=2)
