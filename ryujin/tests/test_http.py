import io,json,socket,subprocess,sys,tempfile,time,unittest,urllib.error,urllib.request
from pathlib import Path
from PIL import Image
class HttpBoundaryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();base=Path(cls.tmp.name)
  (base/'capture.js').write_text('export {x as toBlob}')
  (base/'Card-test.js').write_text('Ve=ze===je||ze===Me')
  (base/'settings.json').write_text(json.dumps({'auth':{'token':'unused'},'devices':{'nexusControlEnabled':['asus-ryujin-lcd']}}))
  (base/'key').write_text('test-key')
  with socket.socket() as sock:sock.bind(('127.0.0.1',0));cls.port=sock.getsockname()[1]
  cls.proc=subprocess.Popen([sys.executable,str(Path(__file__).parents[1]/'bridge.py'),'--socket',str(base/'missing.sock'),'--panel','test','--settings',str(base/'settings.json'),'--key-file',str(base/'key'),'--port',str(cls.port),'--assets',str(base)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for _ in range(100):
   try:
    with socket.create_connection(('127.0.0.1',cls.port),timeout=.1):break
   except OSError:time.sleep(.02)
  else:raise RuntimeError('Test server failed to start')
 @classmethod
 def tearDownClass(cls):cls.proc.terminate();cls.proc.wait(timeout=5);cls.tmp.cleanup()
 def request(self,path,headers=None,data=None):
  try:
   with urllib.request.urlopen(urllib.request.Request(f'http://localhost:{self.port}'+path,headers=headers or {},data=data),timeout=3) as r:return r.status,r.read()
  except urllib.error.HTTPError as e:
   with e:return e.code,e.read()
 def test_missing_cookie_rejected(self):self.assertEqual(self.request('/_bridge/status')[0],403)
 def test_foreign_origin_rejected(self):self.assertEqual(self.request('/_bridge/status',{'Cookie':'ryujin_bridge=test-key','Origin':'https://example.com'})[0],403)
 def test_wrong_host_rejected(self):self.assertEqual(self.request('/_bridge/status',{'Cookie':'ryujin_bridge=test-key','Host':'example.com'})[0],403)
 def test_wrong_size_never_connects_usb(self):
  b=io.BytesIO();Image.new('RGB',(1,1)).save(b,format='PNG')
  self.assertEqual(self.request('/_bridge/frame',{'Cookie':'ryujin_bridge=test-key'},b.getvalue())[0],400)
  status=json.loads(self.request('/_bridge/status',{'Cookie':'ryujin_bridge=test-key'})[1]);self.assertEqual(status['frames'],0);self.assertIsNone(status['error'])
if __name__=='__main__':unittest.main()
