"""Local SQLite storage. Original database is opened read-only during import."""
import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('ICURE_DATA_DIR', ROOT / 'data')).resolve()
DB = DATA / 'icure.sqlite'
TZ = timezone(timedelta(hours=8))


def now():
    return datetime.now(TZ).isoformat(timespec='seconds')


def password_hash(password):
    salt = os.urandom(16).hex()
    value = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 180000).hex()
    return f'pbkdf2$180000${salt}${value}'


def password_ok(password, stored):
    try:
        _, iterations, salt, expected = stored.split('$')
        value = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), int(iterations)).hex()
        return hmac.compare_digest(value, expected)
    except (ValueError, TypeError):
        return False


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, tb):
        try:
            return super().__exit__(exc_type, exc_value, tb)
        finally:
            self.close()


def connect():
    c = sqlite3.connect(DB, timeout=15, factory=ClosingConnection)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c


def rows(c, sql, args=()):
    return [dict(r) for r in c.execute(sql, args)]


def init():
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / 'uploads').mkdir(exist_ok=True)
    with connect() as c:
        c.execute('PRAGMA journal_mode=WAL')
        c.executescript('''
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE IF NOT EXISTS doctors(id INTEGER PRIMARY KEY,name TEXT NOT NULL,department TEXT NOT NULL,age INTEGER,gender TEXT,telephone TEXT,address TEXT,avatar TEXT);
        CREATE TABLE IF NOT EXISTS patients(id INTEGER PRIMARY KEY,name TEXT NOT NULL,age INTEGER,gender TEXT,telephone TEXT,address TEXT,avatar TEXT);
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,legacy_id INTEGER,username TEXT NOT NULL UNIQUE,password TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('doctor','patient')),entity_id INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS relations(id INTEGER PRIMARY KEY AUTOINCREMENT,doctor_id INTEGER NOT NULL REFERENCES doctors(id),patient_id INTEGER NOT NULL REFERENCES patients(id),department TEXT,symptoms TEXT,advice TEXT,prescription TEXT,status TEXT,updated TEXT);
        CREATE TABLE IF NOT EXISTS appointments(id INTEGER PRIMARY KEY AUTOINCREMENT,doctor_id INTEGER NOT NULL REFERENCES doctors(id),patient_id INTEGER REFERENCES patients(id),patient_name TEXT,telephone TEXT,date TEXT,time TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'booked',legacy_id INTEGER,created TEXT NOT NULL);
        CREATE UNIQUE INDEX IF NOT EXISTS slot_unique ON appointments(doctor_id,date,time) WHERE status='booked' AND date IS NOT NULL;
        CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,sender INTEGER NOT NULL REFERENCES users(id),receiver INTEGER NOT NULL REFERENCES users(id),text TEXT NOT NULL,attachment TEXT,filename TEXT,created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS health(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER NOT NULL REFERENCES patients(id),height REAL NOT NULL,weight REAL NOT NULL,bmi REAL NOT NULL,heart_rate INTEGER,body_fat REAL,vision REAL,created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS agent_messages(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL REFERENCES users(id),role TEXT NOT NULL,text TEXT NOT NULL,payload TEXT,created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,action TEXT,detail TEXT,created TEXT NOT NULL);
        ''')
        if c.execute("SELECT 1 FROM meta WHERE key='initialized'").fetchone():
            return
        report = {'doctors': 0, 'patients': 0, 'accounts': 0, 'relations': 0, 'appointments': 0, 'notes': []}
        source = DATA / 'legacy.sqlite'
        if source.exists():
            old = sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)
            old.row_factory = sqlite3.Row
            for table, target, key, name, extra in [('Doc_Info','doctors','doc_id','doc_name',True),('Pat_Info','patients','pat_id','pat_name',False)]:
                for r in old.execute(f'SELECT * FROM {table}'):
                    if extra:
                        c.execute('INSERT INTO doctors VALUES(?,?,?,?,?,?,?,?)', (r[key],r[name],r['doc_class'],r['age'],r['gender'],r['telephone'],r['address'],None))
                    else:
                        c.execute('INSERT INTO patients VALUES(?,?,?,?,?,?,?)',(r[key],r[name],r['age'],r['gender'],r['telephone'],r['address'],None))
                    report[target] += 1
            for r in old.execute('SELECT * FROM loginTable'):
                table = 'doctors' if r['identity'] == 'doctor' else 'patients'
                entity = c.execute(f'SELECT id FROM {table} WHERE id=?',(r['id'],)).fetchone()
                if not entity:
                    entity = c.execute(f'SELECT id FROM {table} WHERE name=?',(r['username'],)).fetchone()
                    if entity:
                        report['notes'].append(f"旧账号 {r['username']} 的档案编号 {r['id']} 已按同名档案关联到 {entity['id']}。")
                if not entity:
                    report['notes'].append(f"账号 {r['username']} 没有可对应的档案，已创建空档案保留账号。")
                    cur = c.execute(f"INSERT INTO {table}(name{',department' if table=='doctors' else ''}) VALUES(?{',?' if table=='doctors' else ''})",(r['username'],'未分类') if table=='doctors' else (r['username'],))
                    entity = {'id':cur.lastrowid}
                c.execute('INSERT INTO users(legacy_id,username,password,role,entity_id) VALUES(?,?,?,?,?)',(r['id'],r['username'],password_hash(r['password']),r['identity'],entity['id']))
                report['accounts'] += 1
            for r in old.execute('SELECT * FROM DocPat_Relation'):
                c.execute('INSERT INTO relations(doctor_id,patient_id,department,symptoms,advice,prescription,status,updated) VALUES(?,?,?,?,?,?,?,?)',(r['doc_id'],r['pat_id'],r['doc_class'],r['symptoms'],r['advice'],r['prescription'],r['treatment_status'],now()))
                report['relations'] += 1
            for r in old.execute('SELECT * FROM appointment'):
                matches = c.execute('SELECT id FROM patients WHERE name=? AND COALESCE(telephone,\'\')=COALESCE(?,\'\')',(r['pat_name'],r['pat_telephone'])).fetchall()
                if len(matches) != 1:
                    matches = c.execute('SELECT id FROM patients WHERE name=?',(r['pat_name'],)).fetchall()
                pid = matches[0]['id'] if len(matches)==1 else None
                c.execute('INSERT INTO appointments(doctor_id,patient_id,patient_name,telephone,date,time,legacy_id,created) VALUES(?,?,?,?,NULL,?,?,?)',(r['doc_id'],pid,r['pat_name'],r['pat_telephone'],r['apt_time'],r['id'],now()))
                report['appointments'] += 1
            old.close()
            report['notes'].append('旧预约只有时刻，没有日期。已作为“日期待核实”的历史预约保留，不占用新日期的号源。')
            report['notes'].append('原数据库保留在 legacy.sqlite；新库口令采用 PBKDF2 哈希，原头像绝对路径不再使用，可在个人资料重新上传。')
        # Fictional accounts make the migrated app immediately reviewable.
        demo_doc=c.execute("INSERT INTO doctors(name,department,age,gender) VALUES('演示医生（虚构）','ENT',35,'未填写')").lastrowid
        demo_pat=c.execute("INSERT INTO patients(name,age,gender) VALUES('演示患者（虚构）',25,'未填写')").lastrowid
        for username,role,entity in [('demo_doctor','doctor',demo_doc),('demo_patient','patient',demo_pat)]:
            if not c.execute('SELECT 1 FROM users WHERE username=?',(username,)).fetchone():
                c.execute('INSERT INTO users(username,password,role,entity_id) VALUES(?,?,?,?)',(username,password_hash('icure2026'),role,entity))
        c.execute("INSERT INTO relations(doctor_id,patient_id,department,symptoms,status,updated) VALUES(?,?,?,'演示记录，可自由编辑','待就诊',?)",(demo_doc,demo_pat,'ENT',now()))
        report['notes'].append('额外新增两个虚构演示账号 demo_patient / demo_doctor，密码均为 icure2026，不属于原始数据。')
        c.execute("INSERT INTO meta VALUES('initialized',?)",(now(),))
        c.execute("INSERT INTO meta VALUES('migration',?)",(json.dumps(report,ensure_ascii=False),))
        (DATA / '迁移报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')


def public_user(c, user):
    table = 'doctors' if user['role']=='doctor' else 'patients'
    profile = dict(c.execute(f'SELECT * FROM {table} WHERE id=?',(user['entity_id'],)).fetchone())
    return {'id':user['id'],'username':user['username'],'role':user['role'],'entity_id':user['entity_id'],'profile':profile}


def audit(c, uid, action, detail=''):
    c.execute('INSERT INTO audit(user_id,action,detail,created) VALUES(?,?,?,?)',(uid,action,detail,now()))
