import re
import subprocess
import sys
import time

class ZMap(object):
   OUTFILE_NUM = 0

   def __init__(self, port=80):
      self.port = port
      self.outfile = "/tmp/zmap_out-%d" % ZMap.OUTFILE_NUM
      self.errfile = "/tmp/zmap_err-%d" % ZMap.OUTFILE_NUM
      ZMap.OUTFILE_NUM += 1

      args = ['zmap', "-p %d" % self.port, '-i eth0', "-o %s" % self.outfile, "2> %s" % self.errfile, '-d > /dev/null']
      print(" ".join(args))

      self.process = subprocess.Popen(" ".join(args), shell=True)

   def report(self):
      line = subprocess.check_output("tail -n 1 %s" % self.errfile, shell=True)

      if line is None:
         print(line)
         return None

      data = {}

      match = re.search('([0-9:]+) ([0-9\.]+)% \(([0-9dhm]+) left\)', line)
      if match is None:
         print('Progress match: '+line)
         return None

      data['elapsed'] = match.group(1)
      data['progress'] = match.group(2)
      data['remaining'] = match.group(3)

      data['send'] = self.__fill_data('send', line)
      data['recv'] = self.__fill_data('recv', line)
      data['drops'] = self.__fill_data('drops', line)

      print("Success: "+line)
      return data

   def __fill_data(self, prefix, line):
      stat_re = ': ([0-9]* )?([0-9\.]+) [Kp]+/s \(([0-9\.]+) [Kp]+/s avg\);'

      match = re.search(prefix+stat_re, line)
      if match is None:
         print(prefix+' match: '+line)
         return None

      ret = {}
      ret['count'] = match.group(1)
      ret['rate'] = match.group(2)
      ret['avg'] = match.group(3)

      return ret


def launch_zmap(port=80):
   return ZMap(port)

def get_zmap_status(zmap):
   return zmap.report()

if __name__ == '__main__':
   zmap = ZMap()

   while True:
      time.sleep(2)
      print("Output:")
      print(zmap.report())
