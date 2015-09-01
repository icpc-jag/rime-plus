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

## exploit parallelism at the expense of precision

import signal

from rime.basic import consts
from rime.basic import codes as basic_codes
from rime.basic import test  as basic_test
from rime.core  import codes
from rime.core  import taskgraph

@taskgraph.task_method
def _ExecInternal(self, args, cwd, stdin, stdout, stderr,
                    timeout=None, precise=False):
    task = taskgraph.ExternalProcessTask(
      args, cwd=cwd, stdin=stdin, stdout=stdout, stderr=stderr, timeout=timeout,
      exclusive=precise)
    proc = yield task
    code = proc.returncode
    # Retry if TLE.
    if not precise and code == -(signal.SIGXCPU):
      self._ResetIO(stdin, stdout, stderr)
      task = taskgraph.ExternalProcessTask(
        args, cwd=cwd, stdin=stdin, stdout=stdout, stderr=stderr, timeout=timeout,
        exclusive=precise)
      proc = yield task
      code = proc.returncode
    if code == 0:
      status = codes.RunResult.OK
    elif code == -(signal.SIGXCPU):
      status = codes.RunResult.TLE
    elif code < 0:
      status = codes.RunResult.RE
    else:
      status = codes.RunResult.NG
    yield codes.RunResult(status, task.time)

basic_codes.CodeBase._ExecInternal = _ExecInternal

def IsTimingValid(self, ui):
    """Checks if timing stats are valid."""
    return (self.results and
            all((c.verdict == basic_test.TestCaseResult.AC
                 for c in self.results.values())))


basic_test.TestsetResult.IsTimingValid = IsTimingValid
