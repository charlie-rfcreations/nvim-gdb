#!/usr/bin/env python3

import os
import subprocess
import sys


# Prepare lldb initialization commands
this_dir = os.path.realpath(os.path.dirname(__file__))

# The script can be launched as `python3 script.py`
args_to_skip = 0 if os.path.basename(__file__) == sys.argv[0] else 1
argv = sys.argv[args_to_skip:]
tmp_dir = '/tmp'
if argv[0] == '-t':
    tmp_dir = argv[1]
    argv = argv[2:]

# Assuming the first argument is path to lldb, the rest are arguments.
# We'd like to ensure gdb is launched with our custom initialization
# injected.

# lldb command
lldb = argv[0]

# the rest are lldb arguments
argv = argv[1:]

exit_code = 0

lldb_init = os.path.join(tmp_dir, "lldb_init")
with open(lldb_init, "w") as f:
    f.write(f"command script import {this_dir}/lldb_commands.py\n")
    f.write("command script add -f lldb_commands.init")
    f.write(" nvim-gdb-init\n")
    server_addr = os.path.join(tmp_dir, "port")
    f.write(f"nvim-gdb-init {server_addr}\n")
    f.write(r"settings set frame-format")
    f.write(r" frame #${frame.index}: ${frame.pc}{")
    f.write(r" ${module.file.basename}{\`${function.name-with-args}")
    f.write(r"{${frame.no-debug}${function.pc-offset}}}}")
    f.write(r"{ at \032\032${line.file.fullpath}:${line.number}}")
    f.write(r"{${function.is-optimized} [opt]}\n")
    f.write("\n")
    f.write("settings set auto-confirm true\n")
    f.write("settings set stop-line-count-before 0\n")
    f.write("settings set stop-line-count-after 0\n")

# Execute lldb finally with our custom initialization script
result = subprocess.run([lldb, '-S', lldb_init] + argv)
sys.exit(result.returncode)
