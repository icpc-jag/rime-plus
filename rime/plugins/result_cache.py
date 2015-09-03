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
#

## test results cache

import os.path
import json

from rime.basic import consts
from rime.basic import test
import rime.basic.targets.testset  # target dependency
from rime.core import targets
from rime.core import taskgraph
from rime.core import commands
from rime.util import files

class Testset(targets.registry.Testset):
  def __init__(self, *args, **kwargs):
    super(Testset, self).__init__(*args, **kwargs)


  @taskgraph.task_method
  def _TestOneCase(self, solution, testcase, ui):
    """Test a solution with one case.

    Cache results if option is set.
    Returns TestCaseResult.
    """
    cache_file_name = os.path.join(solution.out_dir,
                   os.path.splitext(os.path.basename(testcase.infile))[0] + consts.CACHE_EXT)
    solution_file_name = os.path.join(solution.src_dir, solution.code.src_name)

    cache_flag = (
      ui.options.cache_tests and
      files.GetModified(solution_file_name) < files.GetModified(cache_file_name) and
      files.GetModified(testcase.infile) < files.GetModified(cache_file_name))

    if cache_flag:
      case_result_cache = files.ReadFile(cache_file_name)
      if case_result_cache is not None:
        j = json.loads(case_result_cache)
        if j['time'] is not None:
          j['time'] = float(j['time'])
        if j['verdict'] is not None:
          j['verdict'] = j['verdict'].encode('ascii')

        case_result = test.TestCaseResult(solution, testcase, None, None, True)
        case_result.time = j['time']
        case_result.verdict = [
          verdict for verdict in test.TestCaseResult.__dict__.values()
          if isinstance(verdict, test.TestVerdict) and verdict.msg == j['verdict']][0]

      yield case_result

    # TODO(nya): enable result cache.
    case_result = yield self._TestOneCaseNoCache(solution, testcase, ui)

    # always cache in json
    files.WriteFile(json.dumps({
      'verdict' : case_result.verdict.msg,
      'time'    : case_result.time
      }),cache_file_name)

    yield case_result


targets.registry.Override('Testset', Testset)
