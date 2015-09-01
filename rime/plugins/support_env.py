#!/usr/bin/python
#
# Copyright (c) 2011 Rime Project.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

## support shebang like /bin/env ruby

import os.path

from rime.basic import consts
from rime.basic import codes as basic_codes
from rime.core  import codes
from rime.core  import taskgraph
from rime.util  import files

# codes.registry.ScriptCode is not supported
class ScriptCode(basic_codes.ScriptCode):
  def __init__(self, src_name, src_dir, out_dir, run_flags=[]):
    super(ScriptCode, self).__init__(src_name, src_dir, out_dir, run_flags)
    # Replace the executable with the shebang line
    run_args = list(self.run_args)
    try:
      run_args = self._ReadAndParseShebangLine().split(' ') + run_args[1:]
    except IOError:
      pass
    self.run_args = tuple(run_args)

  @taskgraph.task_method
  def Compile(self, *args, **kwargs):
    """Fail if the script is missing a shebang line."""
    try:
      interpreter = self._ReadAndParseShebangLine()
    except IOError:
      yield codes.RunResult('File not found', None)
    if not interpreter:
      yield codes.RunResult('Script missing a shebang line', None)
    if not os.path.exists(interpreter.split(' ')[0]):
      yield codes.RunResult('Interpreter not found: %s' % interpreter.split(' ')[0], None)
    yield (yield basic_codes.CodeBase.Compile(self, *args, **kwargs))


codes.registry.Override('ScriptCode', ScriptCode)
