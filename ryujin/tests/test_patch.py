import importlib.util, unittest, tempfile
from unittest.mock import patch
from pathlib import Path
spec=importlib.util.spec_from_file_location('setup',Path(__file__).parents[1]/'setup.py');setup=importlib.util.module_from_spec(spec);spec.loader.exec_module(setup)
class PatchTests(unittest.TestCase):
 def test_removal_preserves_existing_y70_fix(self):
  previous=b'<head><!-- BEGIN nexus-y70-local-simulator-fix -->existing<!-- END nexus-y70-local-simulator-fix --></head>'
  block=setup.BEGIN+b'\n<script src="/nexus-ryujin-bridge.js"></script>\n'+setup.END+b'\n'
  patched=previous.replace(b'<head>',b'<head>'+block)
  self.assertEqual(setup.strip_patch(patched),previous)
  self.assertEqual(setup.strip_patch(previous),previous)
 def test_apply_twice_and_remove_preserves_y70(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);web=root/'web';lib=root/'lib';state=root/'state'
   web.mkdir();lib.mkdir()
   original=b'<html><head><!-- Y70 existing patch --></head><body></body></html>'
   (web/'index.html').write_bytes(original)
   (lib/'nexus_adapter.js').write_text("const panel='__PANEL_ID__';")
   with patch.multiple(setup,WEB=web,LIB=lib,STATE=state):
    setup.patch({'panel_id':'example'});first=(web/'index.html').read_bytes()
    setup.patch({'panel_id':'example'})
    self.assertEqual((web/'index.html').read_bytes(),first)
    self.assertEqual(setup.strip_patch(first),original)
    self.assertEqual(first.count(setup.BEGIN),1)
 def test_systemd_escaping(self):
  self.assertEqual(setup.quote('/home/A B/100%'), '"/home/A B/100%%"')
if __name__=='__main__':unittest.main()
