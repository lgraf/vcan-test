import can
import time


def test_virtual_can():
  with can.Bus(interface='socketcan', channel='vcan0', receive_own_messages=True) as bus:
    collector = MessageCollector()
    try:
      notifier = can.Notifier(bus, [collector])

      msg = can.Message(arbitration_id=0xC0FFEE, data=[0, 25, 0, 1, 3, 1, 4, 1])
      bus.send(msg)

      wait_for(lambda: collector.count() == 1)

      assert collector.count() == 1
      assert collector.collected_messages[0].arbitration_id == 0xC0FFEE
      assert collector.collected_messages[0].data == bytearray([0, 25, 0, 1, 3, 1, 4, 1])
    finally:
      notifier.stop()


class MessageCollector(can.Listener):
  collected_messages = []

  def on_message_received(self, msg):
    self.collected_messages.append(msg)

  def count(self):
    return len(self.collected_messages)


def wait_for(predicate, timeout=5):
  start_time = time.time()
  while not predicate():
    if time.time() - start_time > timeout:
      raise TimeoutError("Timeout waiting for condition")
    time.sleep(0.1)
