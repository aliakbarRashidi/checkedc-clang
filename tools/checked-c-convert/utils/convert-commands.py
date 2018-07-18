import re
import os
import json
import argparse
import traceback
import subprocess

"""
This tool will invoke checked-c-convert on a compile_commands.json database. 
It contains some work-arounds for cmake+nmake generated compile_commands.json 
files, where the files are malformed. 
"""

DEFAULT_ARGS = ["-dump-stats", "-output-postfix=checked"]
if os.name == "nt":
  DEFAULT_ARGS.append("-extra-arg-before=--driver-mode=cl")

def tryFixUp(s):
  """
  Fix-up for a failure between cmake and nmake.
  """
  b = open(s, 'r').read()
  b = re.sub(r'@<<\n', "", b)
  b = re.sub(r'\n<<', "", b)
  f = open(s, 'w')
  f.write(b)
  f.close()
  return

def runMain(args):
  runs = 0
  cmds = None
  while runs < 2:
    runs = runs + 1
    try:
      cmds = json.load(open(args.compile_commands, 'r'))
    except:
      traceback.print_exc()
      tryFixUp(args.compile_commands)

  if cmds == None:
    print "failed"
    return

  s = set()
  for i in cmds:
    file_to_add = os.path.realpath(i['file'])
    if file_to_add.endswith(".cpp"):
      continue # Checked C extension doesn't support cpp files yet
    s.add(file_to_add)

  print s

  new_args = []
  new_args.append(args.prog_name)
  new_args.extend(DEFAULT_ARGS)
  new_args.extend(list(s))
  f = open('convert.sh', 'w')
  f.write(" \\\n".join(new_args))
  f.close()
  if args.convert_immediately:
    subprocess.check_call(new_args)

  return

if __name__ == '__main__':
  parser = argparse.ArgumentParser("runner")
  parser.add_argument("compile_commands", type=str)
  parser.add_argument("prog_name", type=str)
  parser.add_argument("--convert_immediately", action="store_true")
  args = parser.parse_args()
  runMain(args)
