from pathlib import Path
import json,subprocess,tempfile,shutil,math,sys
O=Path(__file__).resolve().parents[1]
_temp=tempfile.TemporaryDirectory(prefix='portfolio-native-');build=Path(_temp.name)
java=next(p for p in O.glob('Java*/*') if p.is_dir());out=build/'java';out.mkdir(exist_ok=True)
r=subprocess.run(['javac','-encoding','UTF-8','-d',str(out),*[str(p.relative_to(java)) for p in (java/'src').glob('*.java')]],cwd=java,capture_output=True,text=True)
if r.returncode:raise RuntimeError(r.stderr)
cases=[('Delete','hello\n','hello'),('Delete','working\n','work'),('Delete','er\n','er'),('Delete','quickly\n','quick'),('Score','3 -5 Alice -2 Bob -2 Carol\n','Bob'),('Score','1 0 Alice\n','Alice'),('Twopowern','100\n',str(2**100)),('root3','1000000000000000000000000000\n','1000000000'),('root3','-28\n','-3'),('root3','0\n','0'),('root3','26\n','2'),('strcmp','hello lo\n','true'),('strcmp','abc bcde\n','false'),('fxn','2 2\n','0.75'),('m','1 2 3\n','0.200')]
for cls,data,expected in cases:
 r=subprocess.run(['java','-cp',str(out),cls],input=data,capture_output=True,text=True)
 if r.returncode or r.stdout.strip()!=expected:raise AssertionError((cls,data,r.stdout,r.stderr,expected))
for cls,data in [('Score','0\n'),('Twopowern','-1\n'),('m','0 0 0\n')]:
 r=subprocess.run(['java','-cp',str(out),cls],input=data,capture_output=True,text=True)
 assert r.returncode!=0,(cls,r.stdout)
print('Java:',len(cases)+3,'behavior cases passed')
b=next(p for p in O.glob('并行*/*') if p.is_dir());exe=build/('kmeans_cpu.exe' if sys.platform=='win32' else 'kmeans_cpu')
shutil.copy2(b/'src/kmeans_cpu.cpp',build/'kmeans_cpu.cpp')
r=subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','kmeans_cpu.cpp','-o',exe.name],cwd=build,capture_output=True,text=True)
if r.returncode:raise RuntimeError(r.stderr)
result=json.loads(subprocess.check_output([str(exe),'data/texture100.txt','3'],cwd=b,text=True))
assert result['rows']==100 and result['dimensions']==20 and len(result['membership'])==100
assert math.isfinite(result['inertia'])
for content,k,expected in [('1 0 0\n2 0 0\n3 0 0\n',3,True),('1 0 0\n2 10 10\n3 11 11\n',2,True),('1 2 3\n2 3\n',2,False),('',1,False),('1 2 3\n',2,False),('1 2 bad\n',1,False)]:
 f=build/'points.txt';f.write_text(content,encoding='utf-8')
 r=subprocess.run([str(exe),f.name,str(k)],cwd=build,capture_output=True,text=True)
 assert (r.returncode==0)==expected,(content,r.stdout,r.stderr)
 if expected:assert math.isfinite(json.loads(r.stdout)['inertia'])

print('KMeans CPU: dataset and six input/empty-cluster cases passed')
