import importlib.util, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('worker',Path(__file__).parents[1]/'usb_worker.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
class PacketTests(unittest.TestCase):
 def test_native_frame_length_and_exact_last_chunk(self):
  packet=w.lcd_packet([0xec,0x7f,3,0,0x84,3,0])
  self.assertEqual(packet[:7],bytes.fromhex('ec7f0300840300'))
  self.assertEqual(len(packet),65)
  self.assertEqual(w.SIZE%4096,1024)
 def test_reject_fan_pump_flash_and_arbitrary_bulk_commands(self):
  for cmd in [[0xec,0x1a,100],[0xec,0x73,1],[0xec,0x7f,2,0,0x84,3,0],[0xec,0x7f,3,1,0x84,3,0]]:
   with self.assertRaises(ValueError):w.lcd_packet(cmd)
 def test_display_state_query_and_restore(self):
  self.assertEqual(w.lcd_packet([0xec,0xd0])[:2],bytes.fromhex('ecd0'))
  self.assertEqual(w.lcd_packet([0xec,0x51,0x14,0,0])[:5],bytes.fromhex('ec51140000'))
if __name__=='__main__':unittest.main()
