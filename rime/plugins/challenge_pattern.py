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

## enable patterns in challenge cases

import fnmatch
import os.path

from rime.basic import consts
from rime.basic import test
import rime.basic.targets.testset  # target dependency
from rime.core import targets
from rime.core import taskgraph
from rime.util import files


class Testset(targets.registry.Testset):
  def __init__(self, *args, **kwargs):
    super(Testset, self).__init__(*args, **kwargs)

  @taskgraph.task_method
  def _TestSolutionWithChallengeCases(self, solution, ui):
    """Test a wrong solution which has explicitly-specified challenge cases."""
    all_testcases = self.ListTestCases()
    challenge_infiles = solution.challenge_cases
    testcases = []
    for infile in challenge_infiles:
      matched_testcases = [testcase for testcase in all_testcases
                           if fnmatch.fnmatch(os.path.basename(testcase.infile),
                                  infile)]

      if not matched_testcases:
        ui.errors.Error(solution,
                        'Challenge case not found: %s' % infile)
        result = test.TestsetResult(self, solution, [])
        result.Finalize(False,
                        'Challenge case not found: %s' % infile)
        yield result

      testcases.extend([t for t in matched_testcases if t.infile not in testcases])
    # Try challenge cases.
    result = test.TestsetResult(self, solution, testcases)
    yield taskgraph.TaskBranch([
        self._TestSolutionWithChallengeCasesOne(solution, testcase, result, ui)
        for testcase in testcases],
        unsafe_interrupt=True)
    if not result.IsFinalized():
      result.Finalize(True,
                      'Expectedly failed all challenge cases')
    yield result


targets.registry.Override('Testset', Testset)
