#!/usr/bin/env python3
"""Run as the desktop user. Keep credentials in memory and reuse existing panels."""
import argparse, json, os, shutil, subprocess, sys, time, urllib.request, uuid
from pathlib import Path
NAME='Ryujin III — local bridge'
def api(settings,path,body=None):
 token=json.loads(settings.read_text())['auth']['token']
 request=urllib.request.Request('http://localhost:9400'+path,data=json.dumps(body).encode() if body is not None else None,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
 with urllib.request.urlopen(request,timeout=10) as r:return json.load(r)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['install','repair','uninstall','doctor']);p.add_argument('--panel-id',help='Reuse a specific existing 320×240 panel');a=p.parse_args()
 if os.geteuid()==0:raise SystemExit('Run as your normal desktop user; the installer requests administrator access when needed.')
 settings=Path.home()/'.config/Nexus/settings.json';source=Path(__file__).resolve().parent
 if a.command=='doctor':
  ok=True
  for args in [('systemctl','is-active','nexus-ryujin-usb.service'),('systemctl','--user','is-active','nexus-ryujin-renderer.service')]:
   result=subprocess.run(args);ok=ok and result.returncode==0
  try:
   key=(Path(os.environ.get('XDG_RUNTIME_DIR',f'/run/user/{os.getuid()}'))/'nexus-ryujin-bridge.key').read_text()
   request=urllib.request.Request('http://localhost:9412/_bridge/status',headers={'Cookie':'ryujin_bridge='+key})
   status=json.load(urllib.request.urlopen(request,timeout=5))
   age=time.time()-status['last_frame'] if status.get('last_frame') else None
   print('Frames:',status['frames'],'Last frame age:',round(age,1) if age is not None else 'none','Control:',status.get('control_enabled'),'Error:',status.get('error'))
   ok=ok and (status.get('control_enabled') is False or (age is not None and age<10 and status.get('error') is None))
  except Exception as e:print('Bridge status unavailable:',type(e).__name__);ok=False
  raise SystemExit(0 if ok else 1)
 args=[a.command]
 if a.command=='install':
  import usb.core
  from PIL import Image
  if not any(Path(x).is_file() for x in ['/opt/google/chrome/chrome','/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser']):raise SystemExit('Install Chrome/Chromium first.')
  ids=[d for d in Path('/sys/bus/usb/devices').glob('*') if (d/'idVendor').exists() and (d/'idVendor').read_text().strip()=='0b05' and (d/'idProduct').read_text().strip()=='1aa2']
  if len(ids)!=1:raise SystemExit('Expected exactly one ASUS Ryujin III (0b05:1aa2).')
  assets=Path('/opt/nexus/wwwroot/assets')
  if not any(b'Ve=ze===je||ze===Me' in x.read_bytes() for x in assets.glob('Card-*.js')):raise SystemExit('Unsupported Nexus web version; do not install this adapter.')
  panels=api(settings,'/panel/devices')['devices']
  matches=[d for d in panels if d['id']==a.panel_id] if a.panel_id else [d for d in panels if d.get('displayName')==NAME]
  if a.panel_id and not matches:raise SystemExit('Requested panel does not exist.')
  if len(matches)>1:raise SystemExit('Multiple matching panels; use --panel-id.')
  if matches:
   panel=matches[0];caps=panel.get('capabilities',{})
   if (caps.get('cssWidth'),caps.get('cssHeight'))!=(320,240):raise SystemExit('Existing panel must be 320×240; its layout was not changed.')
  else:
   created=api(settings,'/panel/devices',{'displayName':NAME,'capabilities':{'surface':'phone','cssWidth':320,'cssHeight':240,'dpr':1}})
   panels=api(settings,'/panel/devices')['devices'];matches=[d for d in panels if d.get('displayName')==NAME]
   if len(matches)!=1:raise SystemExit('Could not identify newly created panel; inspect Nexus before retrying.')
   panel=matches[0]
  args+=['--user',__import__('pwd').getpwuid(os.getuid()).pw_name,'--panel-id',panel['id']]
 launcher=['pkexec'] if shutil.which('pkexec') else ['sudo']
 subprocess.run(launcher+['/usr/bin/python3',str(source/'setup.py')]+args,check=True)
 if a.command=='install':print('Refresh Nexus, select “'+NAME+'”, and click widget tiles to add them. Enable ASUS Ryujin LCD → Nexus Control.')
if __name__=='__main__':main()
