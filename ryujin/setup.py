#!/usr/bin/env python3
"""Install/remove only the Ryujin companion; never restart or reconfigure Nexus."""
import argparse, hashlib, json, os, pwd, re, shutil, subprocess, sys, tempfile
from pathlib import Path
LIB=Path('/usr/local/lib/nexus-ryujin-bridge')
CONFIG=Path('/etc/nexus-ryujin-bridge.json')
STATE=Path('/var/lib/nexus-ryujin-bridge')
WEB=Path('/opt/nexus/wwwroot')
UNIT='nexus-ryujin-usb.service';USER_UNIT='nexus-ryujin-renderer.service'
BEGIN=b'<!-- BEGIN nexus-ryujin-bridge -->';END=b'<!-- END nexus-ryujin-bridge -->'

def run(*args):subprocess.run(args,check=True)
def user_run(user,*args):
 account=pwd.getpwnam(user)
 run('runuser','-u',user,'--','env',f'XDG_RUNTIME_DIR=/run/user/{account.pw_uid}',f'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{account.pw_uid}/bus',*args)
def quote(value):return '"'+str(value).replace('%','%%').replace('\\','\\\\').replace('"','\\"')+'"'
def strip_patch(data):return re.sub(re.escape(BEGIN)+b'.*?'+re.escape(END)+b'\n?',b'',data,flags=re.S)
def atomic_write(path,data):
 old=path.stat() if path.exists() else None
 fd,name=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data)
  os.chmod(name,old.st_mode & 0o777 if old else 0o644)
  if old:os.chown(name,old.st_uid,old.st_gid)
  os.replace(name,path)
 finally:
  if os.path.exists(name):os.unlink(name)
def patch(config):
 index=WEB/'index.html';data=index.read_bytes()
 STATE.mkdir(mode=0o700,parents=True,exist_ok=True)
 backup=STATE/('index-'+hashlib.sha256(data).hexdigest()+'.html')
 if not backup.exists():backup.write_bytes(data)
 js=(LIB/'nexus_adapter.js').read_text().replace('__PANEL_ID__',config['panel_id'])
 atomic_write(WEB/'nexus-ryujin-bridge.js',js.encode())
 block=BEGIN+b'\n<script src="/nexus-ryujin-bridge.js"></script>\n'+END+b'\n'
 clean=strip_patch(data)
 if b'<head>' not in clean:raise RuntimeError('Unsupported Nexus index')
 changed=clean.replace(b'<head>',b'<head>'+block,1)
 if data!=changed:atomic_write(index,changed)
def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['install','repair','uninstall','patch']);p.add_argument('--user');p.add_argument('--panel-id');p.add_argument('--original-state');a=p.parse_args()
 if os.geteuid()!=0:raise SystemExit('Run this installer through sudo or pkexec')
 if a.command=='install':
  if not a.user or not a.panel_id or not re.fullmatch('[A-Za-z0-9_-]+',a.panel_id):raise SystemExit('--user and a valid --panel-id are required')
  u=pwd.getpwnam(a.user)
  if not u.pw_uid:raise SystemExit('Choose a non-root desktop user')
  cfg={'user':a.user,'uid':u.pw_uid,'home':u.pw_dir,'panel_id':a.panel_id,'port':9412}
 else:cfg=json.loads(CONFIG.read_text());u=pwd.getpwnam(cfg['user'])
 userdir=Path(u.pw_dir)/'.config/systemd/user';userfile=userdir/USER_UNIT
 if a.command=='uninstall':
  user_run(cfg['user'],'systemctl','--user','disable','--now',USER_UNIT)
  run('systemctl','disable','--now',UNIT)
  index=WEB/'index.html';atomic_write(index,strip_patch(index.read_bytes()))
  (WEB/'nexus-ryujin-bridge.js').unlink(missing_ok=True)
  userfile.unlink(missing_ok=True);(Path('/etc/systemd/system')/UNIT).unlink(missing_ok=True)
  user_run(cfg['user'],'systemctl','--user','daemon-reload');run('systemctl','daemon-reload')
  print('Removed companion services and editor adapter. Nexus panel, browser profile and backups preserved.');return
 if a.command=='patch':patch(cfg);return
 # Check runtime dependencies without installing packages or changing the system runtime.
 import usb.core
 from PIL import Image
 chrome=next((x for x in ['/opt/google/chrome/chrome','/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser'] if Path(x).is_file()),None)
 if chrome is None:raise SystemExit('Chrome/Chromium is required')
 LIB.mkdir(parents=True,exist_ok=True);STATE.mkdir(mode=0o700,parents=True,exist_ok=True)
 source=Path(__file__).resolve().parent
 for name in ['setup.py','bridge.py','usb_worker.py','bridge_capture.js','nexus_adapter.js']:
  target=LIB/name
  if (source/name).resolve()!=target.resolve():shutil.copyfile(source/name,target)
  target.chmod(0o644);os.chown(target,0,0)
 CONFIG.write_text(json.dumps(cfg,indent=2)+'\n');CONFIG.chmod(0o600)
 state=STATE/'original-mode.json'
 if a.original_state and not state.exists():
  old=json.loads(Path(a.original_state).read_text())
  if not isinstance(old.get('mode'),int) or not 0<=old['mode']<=255 or len(old.get('args',[]))!=2 or any(type(x)!=int or not 0<=x<=255 for x in old['args']):raise SystemExit('Invalid original LCD state')
  state.write_text(json.dumps(old));state.chmod(0o600)
 patch(cfg)
 rootunit=f'''[Unit]
Description=Nexus Ryujin III display-only USB bridge
After=systemd-udevd.service

[Service]
Type=simple
ExecStartPre=/usr/bin/python3 {LIB}/setup.py patch
ExecStart=/usr/bin/python3 {LIB}/usb_worker.py --socket /run/nexus-ryujin-bridge/pixels.sock --uid {u.pw_uid} --state-file {state}
RuntimeDirectory=nexus-ryujin-bridge
RuntimeDirectoryMode=0755
Restart=on-failure
RestartSec=3
TimeoutStopSec=10
NoNewPrivileges=true
ProtectHome=true

[Install]
WantedBy=multi-user.target
'''
 (Path('/etc/systemd/system')/UNIT).write_text(rootunit)
 userdir.mkdir(parents=True,exist_ok=True);os.chown(userdir,u.pw_uid,u.pw_gid)
 profile=Path(u.pw_dir)/'.local/share/nexus-ryujin-bridge/chrome'
 argv=['/usr/bin/python3',str(LIB/'bridge.py'),'--socket','/run/nexus-ryujin-bridge/pixels.sock','--panel',cfg['panel_id'],'--settings',str(Path(u.pw_dir)/'.config/Nexus/settings.json'),'--port',str(cfg['port']),'--browser',chrome,'--profile',str(profile)]
 execstart=' '.join(map(quote,argv))+' --key-file %t/nexus-ryujin-bridge.key'
 userfile.write_text(f'''[Unit]
Description=Nexus Ryujin III panel renderer
After=graphical-session.target

[Service]
ExecStart={execstart}
Restart=always
RestartSec=3
TimeoutStopSec=15
KillMode=control-group

[Install]
WantedBy=default.target
''');os.chown(userfile,u.pw_uid,u.pw_gid)
 run('systemctl','daemon-reload');user_run(cfg['user'],'systemctl','--user','daemon-reload')
 run('systemctl','enable','--now',UNIT);user_run(cfg['user'],'systemctl','--user','enable','--now',USER_UNIT)
 if a.command=='repair':
  run('systemctl','restart',UNIT);user_run(cfg['user'],'systemctl','--user','restart',USER_UNIT)
 print('Ryujin companion installed. Refresh Nexus to load its separate editor entry.')
if __name__=='__main__':main()
