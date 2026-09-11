#!/usr/bin/env python3
"""Loopback-only Nexus renderer proxy; USB work is isolated in usb_worker.py."""
import argparse, subprocess, signal, http.server, http.client, io, json, os, secrets, select, socket, struct, threading, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

def main():
 p=argparse.ArgumentParser();p.add_argument('--socket',required=True);p.add_argument('--panel',required=True);p.add_argument('--settings',required=True);p.add_argument('--port',type=int,default=9412);p.add_argument('--key-file',required=True);p.add_argument('--browser');p.add_argument('--profile');p.add_argument('--assets',default='/opt/nexus/wwwroot/assets');a=p.parse_args()
 key=Path(a.key_file).read_text() if Path(a.key_file).exists() else secrets.token_urlsafe(32)
 kp=Path(a.key_file);fd=os.open(kp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
 with os.fdopen(fd,'w') as f:f.write(key)
 started=time.time()
 lock=threading.Lock(); usb=None;stats={'frames':0,'last_frame':None,'error':None}
 assets=Path(a.assets)
 modules=[x.name for x in assets.glob('*.js') if x.stat().st_size<100000 and ' as toBlob}' in x.read_text(errors='ignore')]
 if len(modules)!=1:raise SystemExit('Unsupported Nexus capture module; run bridge repair after checking the update')
 if not any(b'Ve=ze===je||ze===Me' in x.read_bytes() for x in assets.glob('Card-*.js')):raise SystemExit('Unsupported Nexus connection module; bridge update required')
 capture=(Path(__file__).with_name('bridge_capture.js')).read_text().replace('__CAPTURE_MODULE__','/assets/'+modules[0])
 def token():return json.loads(Path(a.settings).read_text())['auth']['token']
 class Handler(http.server.BaseHTTPRequestHandler):
  protocol_version='HTTP/1.1'
  def log_message(self,*args):pass
  def reply(self,status,body=b'',kind='text/plain'):
   self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  def do_POST(self):self.do_GET()
  def do_PUT(self):self.do_GET()
  def do_DELETE(self):self.do_GET()
  def do_OPTIONS(self):self.do_GET()
  def do_GET(self):
   nonlocal usb
   if self.headers.get('Host')!=f'localhost:{a.port}':return self.reply(403)
   parsed=urllib.parse.urlsplit(self.path)
   if parsed.scheme or parsed.netloc:return self.reply(400)
   if parsed.path=='/_bridge/start' and secrets.compare_digest(urllib.parse.parse_qs(parsed.query).get('key',[''])[0],key):
    self.send_response(303);self.send_header('Set-Cookie',f'ryujin_bridge={key}; HttpOnly; SameSite=Strict; Path=/');self.send_header('Location','/_bridge/view');self.send_header('Content-Length','0');self.end_headers();return
   from http.cookies import SimpleCookie
   cookies=SimpleCookie(self.headers.get('Cookie',''))
   supplied=cookies.get('ryujin_bridge')
   if not supplied or not secrets.compare_digest(supplied.value,key):return self.reply(403)
   origin=self.headers.get('Origin')
   if origin and origin!=f'http://localhost:{a.port}':return self.reply(403)
   if parsed.path=='/_bridge/view':return self.reply(200,('<!doctype html><title>Nexus Ryujin bridge</title><style>body{margin:0;background:#111}iframe{border:0;width:320px;height:240px}</style><iframe src="/panel/'+a.panel+'"></iframe>').encode(),'text/html')
   if parsed.path=='/_bridge/status':return self.reply(200,json.dumps(stats).encode(),'application/json')
   try:
    size=int(self.headers.get('Content-Length','0'))
    if size<0 or size>16*1024*1024:return self.reply(413)
    body=self.rfile.read(size) if size else None
    if parsed.path=='/_bridge/frame':
     if self.command!='POST' or size>1024*1024:return self.reply(400)
     with Image.open(io.BytesIO(body or b'')) as im:
      if im.size!=(320,240):return self.reply(400)
      frame=im.convert('RGB').tobytes('raw','BGR')
     stats['last_capture']=time.time()
     with lock:
      devices=json.loads(Path(a.settings).read_text()).get('devices',{})
      enabled='asus-ryujin-lcd' in devices.get('nexusControlEnabled',[]) and 'asus-ryujin-lcd' not in devices.get('nexusControlDisabled',[])
      stats['control_enabled']=enabled
      if not enabled:
       if usb:usb.close();usb=None
       return self.reply(204)
      try:
       if usb is None:
        usb=socket.socket(socket.AF_UNIX);usb.settimeout(5);usb.connect(a.socket)
       usb.sendall(struct.pack('!I',len(frame))+frame)
       if usb.recv(2)!=b'OK':raise RuntimeError('Missing USB acknowledgement')
       stats.update(frames=stats['frames']+1,last_frame=time.time(),error=None)
      except Exception as e:
       if usb:usb.close();usb=None
       stats['error']=type(e).__name__;return self.reply(503)
     return self.reply(204)
    if parsed.path=='/sw.js':return self.reply(200,b'self.addEventListener("install",()=>self.skipWaiting());self.addEventListener("activate",()=>self.clients.claim());','application/javascript')
    if parsed.path.startswith('/_bridge/'):return self.reply(404)
    headers={k:v for k,v in self.headers.items() if k.lower() not in {'host','cookie','connection','accept-encoding','authorization','origin','referer','content-length','if-none-match','if-modified-since'}}
    headers['Authorization']='Bearer '+token();headers['Host']='localhost:9400'
    if origin:headers['Origin']='http://localhost:9400'
    if self.headers.get('Upgrade','').lower()=='websocket':
     upstream=socket.create_connection(('127.0.0.1',9400),timeout=5)
     try:
      headers['Connection']='Upgrade'
      request=f'GET {self.path} HTTP/1.1\r\n'+''.join(f'{k}: {v}\r\n' for k,v in headers.items())+'\r\n'
      upstream.sendall(request.encode())
      first=upstream.recv(65536);stats['websocket_status']=first.split(b'\r\n',1)[0].decode(errors='replace');self.connection.sendall(first)
      self.connection.setblocking(False);upstream.setblocking(False)
      while True:
       ready,_,_=select.select([self.connection,upstream],[],[],30)
       if not ready:continue
       for src in ready:
        data=src.recv(65536)
        if not data:return
        dst=upstream if src is self.connection else self.connection
        dst.setblocking(True);dst.sendall(data);dst.setblocking(False)
     finally:upstream.close();self.close_connection=True
     return
    conn=http.client.HTTPConnection('127.0.0.1',9400,timeout=15)
    try:
     conn.request(self.command,self.path,body,headers);r=conn.getresponse();data=r.read();kind=r.getheader('Content-Type','application/octet-stream')
     if parsed.path.startswith('/assets/Card-') and parsed.path.endswith('.js'):
      data=data.replace(b'Ve=ze===je||ze===Me',f'Ve=ze===je||ze===Me||ze===`{a.port}`'.encode())
     if parsed.path=='/panel/'+a.panel and 'text/html' in kind:
      data=data.replace(b'</body>',('<script>'+capture+'</script></body>').encode())
     self.send_response(r.status)
     for k,v in r.getheaders():
      if k.lower() not in {'transfer-encoding','connection','content-length','content-security-policy','set-cookie','etag','last-modified'}:self.send_header(k,v)
     self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    finally:conn.close()
   except (BrokenPipeError,ConnectionResetError):pass
   except Exception as e:stats['error']=type(e).__name__;self.reply(502)
 server=http.server.ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
 print('Ryujin renderer proxy ready on loopback port',a.port,flush=True)
 browser=None
 def stop(*_):raise KeyboardInterrupt
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 if a.browser:
  if not a.profile:raise SystemExit('--profile is required with --browser')
  browser=subprocess.Popen([a.browser,'--headless','--ozone-platform=headless','--no-first-run','--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows','--window-size=320,240','--user-data-dir='+a.profile,f'http://localhost:{a.port}/_bridge/start?key={key}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 def monitor_browser():
  if browser:
   browser.wait();server.shutdown()
 def watch_capture():
  # Retry a failed initial page load (e.g. Nexus still starting at login).
  while browser and browser.poll() is None:
   time.sleep(15)
   if time.time()-stats.get('last_capture',started)>60:
    print('Renderer stopped producing captures; restarting companion',flush=True)
    server.shutdown();return
 if browser:
  threading.Thread(target=monitor_browser,daemon=True).start()
  threading.Thread(target=watch_capture,daemon=True).start()
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:
  server.server_close()
  if browser:
   browser.terminate()
   try:browser.wait(timeout=5)
   except subprocess.TimeoutExpired:browser.kill();browser.wait()
  if usb:usb.close()

if __name__=='__main__':main()
