#!/usr/bin/env python3
"""Ryujin III pixel-only worker. Fixed model, fixed LCD commands, no fan commands."""
import argparse, json, os, select, signal, socket, struct, time
from pathlib import Path
import usb.core, usb.util
SIZE=320*240*3

def lcd_packet(data):
 data=bytes(data)
 valid=(data==bytes([0xec,0xd0]) or (len(data)==5 and data[:2]==bytes([0xec,0x51])) or data==bytes([0xec,0x7f,0x03])+SIZE.to_bytes(4,'little'))
 if not valid:raise ValueError('Command outside display-only allowlist')
 return data.ljust(65,b'\0')

def main():
 p=argparse.ArgumentParser();p.add_argument('--socket',required=True);p.add_argument('--uid',type=int,required=True);p.add_argument('--state-file',required=True);a=p.parse_args()
 if os.geteuid()!=0: raise SystemExit('USB worker must run as root')
 def stop(*_): raise KeyboardInterrupt
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 server=socket.socket(socket.AF_UNIX);server.bind(a.socket);os.chown(a.socket,a.uid,-1);os.chmod(a.socket,0o600);server.listen(1);server.settimeout(1)
 dev=fd=original=None;active=False
 def send(data):
  if os.write(fd,lcd_packet(data))!=65: raise RuntimeError('Short LCD command')
 def restore():
  nonlocal active
  if active and original is not None:
   send([0xec,0x51,original[5],original[6],original[7]]);active=False
 def close_usb():
  nonlocal fd,dev,original,active
  try: restore()
  finally:
   if fd is not None: os.close(fd);fd=None
   if dev is not None:
    try:usb.util.release_interface(dev,0);usb.util.dispose_resources(dev)
    finally:dev=None
   original=None;active=False
 def open_usb():
  nonlocal dev,fd,original
  devices=list(usb.core.find(find_all=True,idVendor=0x0b05,idProduct=0x1aa2))
  if len(devices)!=1: raise RuntimeError('Expected exactly one Ryujin III')
  dev=devices[0]
  if dev.is_kernel_driver_active(0): raise RuntimeError('Refusing to detach bulk driver')
  paths=[p for p in Path('/sys/class/hidraw').glob('hidraw*') if 'HID_ID=0003:00000B05:00001AA2' in (p/'device/uevent').read_text().upper()]
  if len(paths)!=1: raise RuntimeError('Expected one matching HID interface')
  for attempt in range(2):
   fd=os.open('/dev/'+paths[0].name,os.O_RDWR|os.O_NONBLOCK)
   try:
    if Path(a.state_file).exists():
     send([0xec,0xd0])
     saved=json.loads(Path(a.state_file).read_text());original=bytes([0xec,0x50,0,0,0,saved['mode'],*saved['args']]);usb.util.claim_interface(dev,0);return
    send([0xec,0xd0]);end=time.monotonic()+3
    while time.monotonic()<end:
     if select.select([fd],[],[],.1)[0]:
      reply=os.read(fd,65)
      if reply[:2]==b'\xec\x50':
       original=reply;Path(a.state_file).write_text(json.dumps({'mode':reply[5],'args':list(reply[6:8])}));usb.util.claim_interface(dev,0);return
   except OSError as e:
    if e.errno!=108:raise
   os.close(fd);fd=None
   if attempt==0:
    interface=(paths[0]/'device').resolve().parent
    # The generic HID interface can remain shut down after a USB reset.
    # Rebind this interface only, never reset the whole cooler.
    if (interface/'driver').resolve().name!='usbhid':raise RuntimeError('Unexpected HID driver')
    for action in ('unbind','bind'):
     (Path('/sys/bus/usb/drivers/usbhid')/action).write_text(interface.name)
    time.sleep(.2)
    paths=[p for p in Path('/sys/class/hidraw').glob('hidraw*') if 'HID_ID=0003:00000B05:00001AA2' in (p/'device/uevent').read_text().upper()]
    if len(paths)!=1:raise RuntimeError('Ryujin HID did not return')
  raise RuntimeError('LCD state unavailable')
 def recv_exact(conn,n):
  data=bytearray()
  while len(data)<n:
   b=conn.recv(n-len(data))
   if not b: raise EOFError()
   data.extend(b)
  return data
 print('Ryujin pixel worker ready',flush=True)
 try:
  while True:
   try: conn,_=server.accept()
   except socket.timeout:continue
   with conn:
    _,uid,_=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    if uid!=a.uid:continue
    conn.settimeout(10)
    try:
     while True:
      n=struct.unpack('!I',recv_exact(conn,4))[0]
      if n!=SIZE:raise ValueError('Wrong frame size')
      frame=recv_exact(conn,n)
      if dev is None or original is None:open_usb()
      if not active:
       send([0xec,0x51,0x20,original[6],original[7]]);time.sleep(.1);active=True
       send([0xec,0x7f,0x03,*SIZE.to_bytes(4,'little')]);time.sleep(.1)
      for offset in range(0,SIZE,4096):
       chunk=frame[offset:offset+4096]
       if dev.write(0x01,chunk,timeout=1000)!=len(chunk):raise RuntimeError('Short LCD frame')
      send([0xec,0x7f,0x03,*SIZE.to_bytes(4,'little')])
      conn.sendall(b'OK')
    except (EOFError,TimeoutError,BrokenPipeError): pass
    except Exception as e:
     print('LCD transport:',type(e).__name__,str(e),flush=True)
     try:close_usb()
     except Exception:dev=fd=original=None;active=False
    finally:
     try:restore()
     except Exception as e:print('LCD restore:',type(e).__name__,flush=True)
 except KeyboardInterrupt:pass
 finally:
  try:close_usb()
  finally:server.close();Path(a.socket).unlink(missing_ok=True)
if __name__=='__main__':main()
