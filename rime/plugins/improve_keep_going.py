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
  def _TestSolutionWithAllCasesOne(self, solution, testcase, result, ui):
    """Test a solution without challenge cases.

    The solution can be marked as wrong but without challenge cases.
    """
    case_result = yield self._TestOneCase(solution, testcase, ui)
    result.results[testcase] = case_result
    if case_result.verdict not in (test.TestCaseResult.AC,
                                   test.TestCaseResult.WA,
                                   test.TestCaseResult.TLE,
                                   test.TestCaseResult.RE):
      result.Finalize(False,
                      '%s: Judge Error' %
                      os.path.basename(testcase.infile),
                      notable_testcase=testcase)
      ui.errors.Error(solution, result.detail)
      if ui.options.keep_going:
        yield False
      else:
        raise taskgraph.Bailout([False])
    elif case_result.verdict != test.TestCaseResult.AC:
      expected = not solution.IsCorrect()
      r = test.TestsetResult(result.testset, result.solution, result.testcases)
      r.Finalize(expected,
                      '%s: %s' % (os.path.basename(testcase.infile),
                                  case_result.verdict),
                      notable_testcase=testcase)
      result.Finalize(expected,
                      '%s: %s' % (os.path.basename(testcase.infile),
                                  case_result.verdict),
                      notable_testcase=testcase)
      if solution.IsCorrect():
        if case_result.verdict == test.TestCaseResult.WA:
          judgefile = os.path.join(
            solution.out_dir,
            os.path.splitext(os.path.basename(testcase.infile))[0] +
            consts.JUDGE_EXT)
          ui.errors.Error(solution,
                          '%s\n  judge log: %s' % (r.detail, judgefile))
        else:
          ui.errors.Error(solution, r.detail)
      if ui.options.keep_going:
        yield False
      else:
        raise taskgraph.Bailout([False])
    ui.console.PrintAction('TEST', solution,
                           '%s: PASSED' % os.path.basename(testcase.infile),
                           progress=True)
    yield True


targets.registry.Override('Testset', Testset)
