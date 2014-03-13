import json
import pipes
import re
import subprocess
import sys
import time

with open("config/config.json", "r") as f:
   global_config = json.load(f)

def zmap_gen(config_args={}):
   clean_args = dict((k, v) for k, v in config_args.iteritems() if k in global_config["allowed_args"])
   zmap_args = dict(clean_args.items() + global_config["enforced_args"].items())
   zmap_args["config"] = global_config["default_config"]

   config = ZMapConfig(zmap_args)

   return ZMap(config)

class ZMapConfig(dict):
   VALID_ARGS = {
         # Common Options
         "target-port":    (int, "common"),
         "output-file":    (str, "common"),
         "blacklist-file": (str, "common"),
         # Scan Options
         "max-targets":    (int, "scan"),
         "max-results":    (int, "scan"),
         "max-runtime":    (int, "scan"),
         "rate":           (int, "scan"),
         "bandwidth":      (str, "scan"),
         "cooldown-time":  (int, "scan"),
         "seed":           (int, "scan"),
         "sender-threads": (int, "scan"),
         "probes":         (int, "scan"),
         "dryrun":         (bool, "scan"),
         # Network Options
         "source-port":    (int, "network"),
         "source-ip":      (int, "network"),
         "gateway-mac":    (str, "network"),
         "interface":      (str, "network"),
         # Probe Options
         "probe-module":   (str, "probe"),
         "probe-args":     (str, "probe"),
         # Output Options
         "output-module":  (str, "output"),
         "output-fields":  (str, "output"),
         "output-filter":  (str, "output"),
         # Additional Options
         "config":         (str, "additional")
   }

   @staticmethod
   def verify_config(config):
      for key, value in config.items():
         if key not in ZMapConfig.VALID_ARGS.keys():
            return False

      return True

   def __init__(self, user_config={}):
      if not ZMapConfig.verify_config(user_config):
         raise Exception

      self.config = user_config

class ZMap(object):
   JOB_ID = 0

   @staticmethod
   def get_job_id():
      ret = ZMap.JOB_ID
      ZMap.JOB_ID += 1
      return ret

   def __init__(self, config):
      if not isinstance(config, ZMapConfig):
         raise TypeError

      self.job_id = ZMap.get_job_id()
      self.errfile = "/tmp/zmap-err-%d" % self.job_id

      self.args = []
      for key, value in config.config.items():
         if type(value) is not bool:
            self.args += ['--%s %s' % (pipes.quote(key), pipes.quote(value))]
         else:
            self.args += ['--%s' % pipes.quote(key)]

      self.process = None

   def start(self):
      args = ['zmap'] + self.args + ["2> %s" % self.errfile, "> /dev/null"]

      print(" ".join(args))

      self.process = subprocess.Popen(" ".join(args), shell=True)

   def stop(self):
      if not self.is_started():
         return

      self.process.kill()
      self.process = None

   def report(self):
      line = subprocess.check_output("tail -n 1 %s" % self.errfile, shell=True)

      if line is None:
         print(line)
         return None
      else:
         line = line.strip()

      data = {}

      match = re.search('([0-9:]+) ([0-9\.]+)%(?: \(([0-9dhms]+) left\))?', line)
      if match is None:
         print('Progress match: '+line)
         return None

      data['elapsed'] = match.group(1)
      data['progress'] = match.group(2)
      data['remaining'] = match.group(3)

      match = re.search('hits: ([0-9\.]+)%', line)
      if match is None:
         print('Hits match: '+line)
         return None

      data['hits'] = match.group(1)

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
