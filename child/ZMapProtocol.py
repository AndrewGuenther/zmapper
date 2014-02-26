import socket

class ZMapProtocol(object):
   MAX_MSG_LEN = 1024

   def __init__(self):
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.setblocking(0)

   def connect(self, host='localhost', port=9876):
      self.sock.connect((host, port))

   def start(self, args):
      self.sock.send("start "+args)

   def stop(self):
      self.sock.send("stop")

   def report(self):
      self.sock.send("report")

      return self.sock.recv(ZMapProtocol.MAX_MSG_LEN)

if __name__ == "__main__":
   z = ZMapProtocol()
   z.connect()
   z.start()
   print(z.report())
   z.stop()
