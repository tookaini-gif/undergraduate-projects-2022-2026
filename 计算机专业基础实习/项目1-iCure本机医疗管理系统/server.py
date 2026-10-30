"""iCure Windows: Python standard library only, loopback HTTP server."""
import argparse
import base64
import contextlib
import io
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import threading
import time
import traceback
import webbrowser
from datetime import datetime, timedelta
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import agent
import database as db

SESSIONS = {}
FAILED_LOGINS = {}
LOCK = threading.RLock()
STATIC = db.ROOT / 'dist'
SLOTS = [f'{h:02d}:00' for h in range(9,17)]


class APIError(Exception):
    def __init__(self,message,status=400): self.message,self.status=message,status


def require(condition,message,status=400):
    if not condition: raise APIError(message,status)


def text(data,key,limit=200,required=False):
    v=data.get(key,'')
    require(isinstance(v,str),'字段格式错误：'+key)
    v=v.strip()
    require(len(v)<=limit,'内容过长：'+key)
    require(not required or bool(v),'请填写：'+key)
    return v


def number(data,key,low,high,optional=False):
    v=data.get(key)
    if optional and (v is None or v==''): return None
    try: v=float(v)
    except (ValueError,TypeError): raise APIError('请输入有效数值：'+key)
    require(low<=v<=high,'数值超出范围：'+key)
    return v


def appointment_rows(c,user):
    clause='a.doctor_id=?' if user['role']=='doctor' else 'a.patient_id=?'
    return db.rows(c,f'''SELECT a.*,d.name doctor_name,d.department FROM appointments a
        JOIN doctors d ON a.doctor_id=d.id WHERE {clause} ORDER BY COALESCE(a.date,'0000') DESC,a.time DESC''',(user['entity_id'],))


def doctor_patients(c,user):
    require(user['role']=='doctor','仅医生可以访问患者管理。',403)
    return db.rows(c,'''SELECT r.*,p.name,p.age,p.gender,p.telephone,p.avatar FROM relations r
        JOIN patients p ON r.patient_id=p.id WHERE r.doctor_id=? ORDER BY p.name''',(user['entity_id'],))


class Handler(BaseHTTPRequestHandler):
    server_version='iCure/1.0'

    def log_message(self,fmt,*args):
        # Do not log request bodies, keys, passwords, or conversation content.
        if self.path.split('?')[0] not in ('/api/messages','/api/healthcheck'):
            print(f'[{datetime.now(db.TZ).strftime("%H:%M:%S")}] {self.command} {self.path.split("?")[0]} {args[1] if len(args)>1 else ""}',flush=True)

    def headers_common(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','same-origin')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data: blob:; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")

    def send_bytes(self,data,content_type='application/json; charset=utf-8',status=200,cookie=None,filename=None):
        self.send_response(status)
        self.headers_common()
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(data)))
        if cookie: self.send_header('Set-Cookie',cookie)
        if filename: self.send_header('Content-Disposition','attachment; filename="'+filename+'"')
        self.end_headers()
        self.wfile.write(data)

    def json(self,value,status=200,cookie=None):
        self.send_bytes(json.dumps(value,ensure_ascii=False).encode('utf-8'),status=status,cookie=cookie)

    def session(self,required=True):
        jar=cookies.SimpleCookie()
        try: jar.load(self.headers.get('Cookie',''))
        except cookies.CookieError: pass
        token=jar.get('icure_session')
        token=token.value if token else ''
        with LOCK:
            s=SESSIONS.get(token)
            if s and s['expires']<time.time():
                SESSIONS.pop(token,None);s=None
        if required: require(s is not None,'请先登录。',401)
        return token,s

    def read_json(self):
        require(self.headers.get('Content-Type','').split(';')[0]=='application/json','请求必须使用 JSON。',415)
        try: length=int(self.headers.get('Content-Length','0'))
        except ValueError: raise APIError('请求长度无效。')
        require(0<length<=8*1024*1024,'请求内容为空或超过 8 MB。',413)
        try: data=json.loads(self.rfile.read(length))
        except (ValueError,UnicodeDecodeError): raise APIError('JSON 格式错误。')
        require(isinstance(data,dict),'请求格式错误。')
        return data

    def check_host(self):
        require(self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'),'只允许通过本机地址访问。',403)
        origin=self.headers.get('Origin')
        if origin:
            require(origin in (f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'),'不允许跨站请求。',403)

    def do_GET(self): self.handle_request(False)
    def do_POST(self): self.handle_request(True)

    def handle_request(self,post):
        try:
            self.check_host()
            path=urlparse(self.path).path
            query=parse_qs(urlparse(self.path).query)
            if not path.startswith('/api/'):
                require(not post,'不支持此操作。',405)
                relative='index.html' if path=='/' else path.lstrip('/')
                target=(STATIC/relative).resolve()
                require(target.is_relative_to(STATIC.resolve()) and target.is_file(),'找不到页面。',404)
                mime=mimetypes.guess_type(target)[0] or 'application/octet-stream'
                return self.send_bytes(target.read_bytes(),mime+('; charset=utf-8' if mime.startswith('text/') or mime=='application/javascript' else ''))
            if not post and path=='/api/healthcheck': return self.json({'app':'iCure-Windows','version':'1.0','status':'ok'})
            data=self.read_json() if post else {}
            if post and path in ('/api/login','/api/register'):
                return self.authenticate(path,data)
            token,s=self.session()
            if post: require(secrets.compare_digest(self.headers.get('X-CSRF-Token',''),s['csrf']),'页面已失效，请刷新后重试。',403)
            with db.connect() as c:
                user=c.execute('SELECT * FROM users WHERE id=?',(s['uid'],)).fetchone()
                require(user is not None,'账号不存在。',401)
                if post: result=self.post_api(c,user,s,path,data)
                else: result=self.get_api(c,user,s,path,query)
            if path=='/api/logout':
                with LOCK: SESSIONS.pop(token,None)
                return self.json({'ok':True},cookie='icure_session=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict')
            if isinstance(result,tuple) and result[0]=='file':
                return self.send_bytes(result[1],'application/octet-stream',filename=result[2])
            self.json(result)
        except APIError as e: self.json({'error':e.message},e.status)
        except sqlite3.IntegrityError: self.json({'error':'数据冲突：用户名可能已存在，或该号源刚被预约。请刷新后重试。'},409)
        except (BrokenPipeError,ConnectionResetError): pass
        except Exception:
            traceback.print_exc()
            self.json({'error':'操作失败，请查看运行窗口中的错误信息。'},500)

    def authenticate(self,path,data):
        username=text(data,'username',80,True)
        password=text(data,'password',256,True)
        bucket=(self.client_address[0],username)
        with LOCK:
            attempts=[t for t in FAILED_LOGINS.get(bucket,[]) if time.time()-t<300]
            require(len(attempts)<12,'尝试次数过多，请 5 分钟后重试。',429)
        with db.connect() as c:
            if path=='/api/register':
                require(len(password)>=6,'新密码至少 6 位。')
                role=text(data,'role')
                require(role in ('doctor','patient'),'请选择身份。')
                name=text(data,'name',80,True)
                age=number(data,'age',0,120,True)
                require(age is None or age.is_integer(),'年龄必须是整数。')
                gender=text(data,'gender',30)
                telephone=text(data,'telephone',40)
                if role=='doctor':
                    department=text(data,'department',80,True)
                    entity=c.execute('INSERT INTO doctors(name,department,age,gender,telephone) VALUES(?,?,?,?,?)',(name,department,age,gender,telephone)).lastrowid
                else:
                    entity=c.execute('INSERT INTO patients(name,age,gender,telephone) VALUES(?,?,?,?)',(name,age,gender,telephone)).lastrowid
                uid=c.execute('INSERT INTO users(username,password,role,entity_id) VALUES(?,?,?,?)',(username,db.password_hash(password),role,entity)).lastrowid
                db.audit(c,uid,'register')
                user=c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
            else:
                user=c.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
                if not user or not db.password_ok(password,user['password']):
                    with LOCK: FAILED_LOGINS[bucket]=attempts+[time.time()]
                    raise APIError('用户名或密码不正确。',401)
                with LOCK: FAILED_LOGINS.pop(bucket,None)
                db.audit(c,user['id'],'login')
            public=db.public_user(c,user)
        token=secrets.token_urlsafe(32)
        csrf=secrets.token_urlsafe(24)
        with LOCK:
            for stale in [k for k,v in SESSIONS.items() if v['expires']<time.time()]: SESSIONS.pop(stale,None)
            SESSIONS[token]={'uid':public['id'],'csrf':csrf,'expires':time.time()+12*3600,'provider':None}
        self.json({'user':public,'csrf':csrf},cookie=f'icure_session={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=43200')

    def get_api(self,c,user,s,path,q):
        uid=user['id'];eid=user['entity_id']
        if path=='/api/me':
            return {'user':db.public_user(c,user),'csrf':s['csrf'],'online_configured':bool(s['provider'])}
        if path=='/api/dashboard':
            appointments=appointment_rows(c,user)
            relations=doctor_patients(c,user) if user['role']=='doctor' else db.rows(c,'''SELECT r.*,d.name doctor_name FROM relations r JOIN doctors d ON r.doctor_id=d.id WHERE patient_id=?''',(eid,))
            return {'appointments':appointments,'relations':relations,'today':datetime.now(db.TZ).date().isoformat(),'health':db.rows(c,'SELECT * FROM health WHERE patient_id=? ORDER BY id DESC LIMIT 7',(eid,)) if user['role']=='patient' else [],'departments':agent.DEPARTMENTS}
        if path=='/api/doctors':
            return db.rows(c,'SELECT id,name,department,avatar FROM doctors ORDER BY department,name')
        if path=='/api/slots':
            try: did=int(q.get('doctor_id',['0'])[0]);day=datetime.strptime(q.get('date',[''])[0],'%Y-%m-%d').date()
            except ValueError: raise APIError('请选择医生和日期。')
            require(c.execute('SELECT 1 FROM doctors WHERE id=?',(did,)).fetchone(),'医生不存在。',404)
            busy={r['time'] for r in c.execute("SELECT time FROM appointments WHERE doctor_id=? AND date=? AND status='booked'",(did,day.isoformat()))}
            current=datetime.now(db.TZ)
            return [{'time':slot,'available':slot not in busy and datetime.fromisoformat(day.isoformat()+'T'+slot).replace(tzinfo=db.TZ)>current} for slot in SLOTS]
        if path=='/api/appointments': return appointment_rows(c,user)
        if path=='/api/patients': return doctor_patients(c,user)
        if path=='/api/contacts':
            opposite='patient' if user['role']=='doctor' else 'doctor'
            table='patients' if opposite=='patient' else 'doctors'
            return db.rows(c,f'''SELECT u.id,u.username,u.role,p.name,p.avatar,
                (SELECT COUNT(*) FROM messages m WHERE (m.sender=u.id AND m.receiver=?) OR (m.receiver=u.id AND m.sender=?)) message_count
                FROM users u JOIN {table} p ON u.entity_id=p.id WHERE u.role=? ORDER BY p.name''',(uid,uid,opposite))
        if path=='/api/messages':
            try: peer=int(q.get('peer',['0'])[0])
            except ValueError: raise APIError('请选择联系人。')
            return db.rows(c,'''SELECT id,sender,receiver,text,filename,attachment IS NOT NULL has_attachment,created FROM messages
                WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id DESC LIMIT 200''',(uid,peer,peer,uid))[::-1]
        if path.startswith('/api/attachment/'):
            try: mid=int(path.rsplit('/',1)[1])
            except ValueError: raise APIError('文件不存在。',404)
            m=c.execute('SELECT * FROM messages WHERE id=? AND (sender=? OR receiver=?)',(mid,uid,uid)).fetchone()
            require(m is not None and m['attachment'],'无权读取此文件。',404)
            return ('file',(db.DATA/'uploads'/m['attachment']).read_bytes(),'attachment'+Path(m['filename']).suffix)
        if path=='/api/health':
            require(user['role']=='patient','仅患者可以访问自己的健康记录。',403)
            return db.rows(c,'SELECT * FROM health WHERE patient_id=? ORDER BY id DESC LIMIT 100',(eid,))
        if path=='/api/agent/history':
            records=db.rows(c,'SELECT id,role,text,payload,created FROM agent_messages WHERE user_id=? ORDER BY id DESC LIMIT 40',(uid,))[::-1]
            for r in records:
                if r['payload']: r['payload']=json.loads(r['payload'])
            return records
        if path=='/api/stats':
            require(user['role']=='doctor','仅医生可以访问统计。',403)
            return {'status':db.rows(c,'SELECT COALESCE(status,\'未填写\') label,COUNT(*) count FROM relations WHERE doctor_id=? GROUP BY status',(eid,)),
                'symptoms':db.rows(c,'SELECT COALESCE(NULLIF(symptoms,\'\'),\'未填写\') label,COUNT(*) count FROM relations WHERE doctor_id=? GROUP BY symptoms ORDER BY count DESC LIMIT 10',(eid,)),
                'appointments':db.rows(c,"SELECT COALESCE(date,'日期待核实') label,COUNT(*) count FROM appointments WHERE doctor_id=? AND status='booked' GROUP BY date ORDER BY date DESC LIMIT 10",(eid,))}
        if path=='/api/migration': return json.loads(c.execute("SELECT value FROM meta WHERE key='migration'").fetchone()[0])
        raise APIError('接口不存在。',404)

    def post_api(self,c,user,s,path,data):
        uid=user['id'];eid=user['entity_id']
        if path=='/api/logout': return {'ok':True}
        if path=='/api/profile':
            name=text(data,'name',80,True)
            username=text(data,'username',80,True)
            age=number(data,'age',0,120,True)
            require(age is None or age.is_integer(),'年龄必须是整数。')
            table='doctors' if user['role']=='doctor' else 'patients'
            values=[name,age,text(data,'gender',30),text(data,'telephone',40),text(data,'address',300)]
            sql=f'UPDATE {table} SET name=?,age=?,gender=?,telephone=?,address=?'
            if table=='doctors': sql+=',department=?';values.append(text(data,'department',80,True))
            c.execute(sql+' WHERE id=?',values+[eid])
            newpw=text(data,'new_password',256)
            if newpw:
                require(db.password_ok(text(data,'old_password',256,True),user['password']),'当前密码不正确。')
                require(len(newpw)>=6,'新密码至少 6 位。')
                c.execute('UPDATE users SET password=? WHERE id=?',(db.password_hash(newpw),uid))
                with LOCK:
                    for token in [k for k,v in SESSIONS.items() if v['uid']==uid and v is not s]: SESSIONS.pop(token,None)
            c.execute('UPDATE users SET username=? WHERE id=?',(username,uid))
            db.audit(c,uid,'update_profile')
            return db.public_user(c,c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone())
        if path=='/api/avatar':
            raw=self.decode_file(data,2*1024*1024)
            if raw.startswith(b'\x89PNG\r\n\x1a\n'): ext='.png'
            elif raw.startswith(b'\xff\xd8\xff'): ext='.jpg'
            elif raw.startswith((b'GIF87a',b'GIF89a')): ext='.gif'
            else: raise APIError('头像只支持 PNG、JPEG、GIF。')
            filename='avatar_'+secrets.token_hex(16)+ext
            # Avatars are served as images from static assets; they contain no executable markup.
            (STATIC/'assets'/'uploads').mkdir(exist_ok=True)
            (STATIC/'assets'/'uploads'/filename).write_bytes(raw)
            avatar='/assets/uploads/'+filename
            table='doctors' if user['role']=='doctor' else 'patients'
            c.execute(f'UPDATE {table} SET avatar=? WHERE id=?',(avatar,eid))
            return {'avatar':avatar}
        if path=='/api/appointments/book':
            require(user['role']=='patient','请用患者账号预约。',403)
            try: did=int(data.get('doctor_id',0));day=datetime.strptime(text(data,'date'),'%Y-%m-%d').date()
            except (ValueError,TypeError): raise APIError('请选择有效的医生和日期。')
            slot=text(data,'time')
            require(slot in SLOTS,'请选择有效时刻。')
            current=datetime.now(db.TZ)
            require(current.date()<=day<=current.date()+timedelta(days=90),'只能预约未来 90 天内的号源。')
            require(datetime.combine(day,datetime.strptime(slot,'%H:%M').time(),db.TZ)>current,'此时刻已过，请选择未来号源。')
            doctor=c.execute('SELECT * FROM doctors WHERE id=?',(did,)).fetchone()
            require(doctor is not None,'医生不存在。',404)
            patient=c.execute('SELECT * FROM patients WHERE id=?',(eid,)).fetchone()
            cur=c.execute('INSERT INTO appointments(doctor_id,patient_id,patient_name,telephone,date,time,created) VALUES(?,?,?,?,?,?,?)',(did,eid,patient['name'],patient['telephone'],day.isoformat(),slot,db.now()))
            summary=text(data,'summary',6000)
            c.execute("INSERT INTO relations(doctor_id,patient_id,department,symptoms,status,updated) SELECT ?,?,?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM relations WHERE doctor_id=? AND patient_id=?)",(did,eid,doctor['department'],summary,'待就诊',db.now(),did,eid))
            db.audit(c,uid,'book',str(cur.lastrowid))
            return {'ok':True,'id':cur.lastrowid}
        if path=='/api/appointments/cancel':
            aid=number(data,'id',1,10**10)
            clause='doctor_id=?' if user['role']=='doctor' else 'patient_id=?'
            a=c.execute(f'SELECT * FROM appointments WHERE id=? AND {clause}',(aid,eid)).fetchone()
            require(a is not None,'无权修改此预约。',403)
            require(a['status']=='booked','此预约已取消。')
            c.execute("UPDATE appointments SET status='cancelled' WHERE id=?",(aid,))
            db.audit(c,uid,'cancel',str(aid))
            return {'ok':True}
        if path=='/api/patients/update':
            require(user['role']=='doctor','仅医生可以编辑诊疗记录。',403)
            rid=number(data,'id',1,10**10)
            require(c.execute('SELECT 1 FROM relations WHERE id=? AND doctor_id=?',(rid,eid)).fetchone(),'无权编辑此患者。',403)
            status=text(data,'status',50,True)
            require(status in ('待就诊','治疗中','已完成','已康复','Ongoing','Completed','Recovered'),'请选择有效状态。')
            c.execute('UPDATE relations SET symptoms=?,advice=?,prescription=?,status=?,updated=? WHERE id=?',(text(data,'symptoms',6000),text(data,'advice',6000),text(data,'prescription',6000),status,db.now(),rid))
            db.audit(c,uid,'update_record',str(rid))
            return {'ok':True}
        if path=='/api/messages/send':
            peer=number(data,'receiver',1,10**10)
            target=c.execute('SELECT * FROM users WHERE id=?',(peer,)).fetchone()
            require(target and target['role']!=user['role'],'请选择另一身份的联系人。')
            message=text(data,'text',6000)
            attachment=None;filename=None
            require(message or data.get('file'),'消息不能为空。')
            if data.get('file'):
                raw=self.decode_file(data,5*1024*1024)
                filename=text(data,'filename',180,True).replace('\\','/').rsplit('/',1)[-1]
                attachment=secrets.token_hex(24)
                (db.DATA/'uploads'/attachment).write_bytes(raw)
            cur=c.execute('INSERT INTO messages(sender,receiver,text,attachment,filename,created) VALUES(?,?,?,?,?,?)',(uid,peer,message,attachment,filename,db.now()))
            return {'ok':True,'id':cur.lastrowid}
        if path=='/api/health/save':
            require(user['role']=='patient','请使用患者账号。',403)
            height=number(data,'height',50,250);weight=number(data,'weight',2,500)
            hr=number(data,'heart_rate',20,250,True);fat=number(data,'body_fat',1,75,True);vision=number(data,'vision',0,100,True)
            bmi=round(weight/(height/100)**2,2)
            c.execute('INSERT INTO health(patient_id,height,weight,bmi,heart_rate,body_fat,vision,created) VALUES(?,?,?,?,?,?,?,?)',(eid,height,weight,bmi,hr,fat,vision,db.now()))
            return {'bmi':bmi,'note':'BMI 是体重与身高的计算值，不能独立诊断健康状况。儿童、孕期及高肌肉量人群需由专业人员评估。','sources':agent.SOURCE_LINKS[2:]}
        if path=='/api/agent/config':
            if data.get('clear'):
                s['provider']=None
                return {'ok':True,'configured':False}
            endpoint=text(data,'endpoint',500,True)
            model=text(data,'model',150,True)
            key=text(data,'key',1000)
            require('\n' not in key and '\r' not in key,'密钥格式错误。')
            # Validate URL now as well as immediately before sending.
            u=urlparse(endpoint)
            require(not u.username and not u.password and not u.query and not u.fragment,'API 地址格式不正确。')
            require(u.scheme=='https' and bool(u.hostname) or u.scheme=='http' and u.hostname in ('127.0.0.1','localhost','::1'),'远程 API 使用 HTTPS；本地模型可使用 HTTP。')
            s['provider']={'endpoint':endpoint,'model':model,'key':key}
            return {'ok':True,'configured':True}
        if path=='/api/agent/clear':
            c.execute('DELETE FROM agent_messages WHERE user_id=?',(uid,))
            return {'ok':True}
        if path=='/api/agent/chat':
            message=text(data,'message',3000,True)
            require(isinstance(data.get('online',False),bool) and isinstance(data.get('use_profile',False),bool),'助手选项格式错误。')
            history=db.rows(c,'SELECT role,text FROM agent_messages WHERE user_id=? ORDER BY id DESC LIMIT 10',(uid,))[::-1]
            result=agent.offline(c,user,message,history,data.get('use_profile',False))
            if data.get('online'):
                require(s.get('provider') is not None,'请先配置在线模型，或关闭在线发送。')
                try: result=agent.online(result,message,history,s['provider'])
                except Exception as error:
                    # Error class only: provider bodies/URLs could contain secrets.
                    result['trace'].append({'tool':'在线模型整理','status':'未完成','detail':'在线服务不可用或返回格式不符，已使用离线结果。错误类型：'+type(error).__name__})
                    result['online_error']=True
            c.execute('INSERT INTO agent_messages(user_id,role,text,created) VALUES(?,?,?,?)',(uid,'user',message,db.now()))
            c.execute('INSERT INTO agent_messages(user_id,role,text,payload,created) VALUES(?,?,?,?,?)',(uid,'assistant',result['message'],json.dumps(result,ensure_ascii=False),db.now()))
            return result
        if path=='/api/backup':
            backup_dir=db.DATA/'backups';backup_dir.mkdir(exist_ok=True)
            filename='icure-'+datetime.now(db.TZ).strftime('%Y%m%d-%H%M%S')+'-'+secrets.token_hex(3)+'.sqlite'
            # Export only the current user's records, never another user's database.
            profile=db.public_user(c,user)
            export={'user':profile,'appointments':appointment_rows(c,user),'exported_at':db.now()}
            if user['role']=='doctor': export['patients']=doctor_patients(c,user)
            else:
                export['health']=db.rows(c,'SELECT * FROM health WHERE patient_id=?',(eid,))
                export['records']=db.rows(c,'SELECT * FROM relations WHERE patient_id=?',(eid,))
            export['messages']=db.rows(c,'SELECT * FROM messages WHERE sender=? OR receiver=?',(uid,uid))
            export['agent']=db.rows(c,'SELECT role,text,payload,created FROM agent_messages WHERE user_id=?',(uid,))
            payload=json.dumps(export,ensure_ascii=False,indent=2).encode('utf-8')
            filename=filename.replace('.sqlite','.json')
            (backup_dir/filename).write_bytes(payload)
            return {'filename':filename,'data':export}
        raise APIError('接口不存在。',404)

    @staticmethod
    def decode_file(data,limit):
        value=data.get('file','')
        require(isinstance(value,str),'文件格式无效。')
        try: raw=base64.b64decode(value,validate=True)
        except (ValueError,TypeError): raise APIError('文件编码错误。')
        require(0<len(raw)<=limit,f'文件必须小于 {limit//1024//1024} MB。',413)
        return raw


def make_server(port): return ThreadingHTTPServer(('127.0.0.1',port),Handler)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    db.init()
    server=None
    for port in range(args.port,args.port+20):
        try: server=make_server(port);break
        except OSError: continue
    if not server: raise SystemExit('No free local port. Please close another iCure window and retry.')
    url=f'http://127.0.0.1:{server.server_port}'
    print('\niCure Windows is running: '+url+'\nKeep this window open. Press Ctrl+C to stop.\n',flush=True)
    if not args.no_browser: threading.Timer(0.7,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print('\niCure stopped.',flush=True)
    finally: server.server_close()


if __name__=='__main__': main()
