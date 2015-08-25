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

## add O2 as a default option, add cxx11 and cxx14 compile settings

import os.path

from rime.basic import consts
from rime.basic import codes as basic_codes
from rime.core  import codes

class CCode(codes.registry.CCode):
  def __init__(self, src_name, src_dir, out_dir, flags=['-lm']):
    super(CCode, self).__init__(src_name, src_dir, out_dir, ['-O2'] + flags)

class CXXCode(codes.registry.CXXCode):
  EXTENSIONS = ['cc', 'cxx', 'cpp']
  def __init__(self, src_name, src_dir, out_dir, flags=[]):
    super(CXXCode, self).__init__(src_name, src_dir, out_dir, ['-O2'] + flags)

class CXX11Code(basic_codes.CodeBase):
  PREFIX = 'cxx11'
  EXTENSIONS = ['cc11', 'cxx11', 'cpp11']

  def __init__(self, src_name, src_dir, out_dir, flags=[]):
    exe_name = os.path.splitext(src_name)[0] + consts.EXE_EXT
    super(CXX11Code, self).__init__(
      src_name=src_name, src_dir=src_dir, out_dir=out_dir,
      compile_args=(['g++', '-O2', '-std=c++11',
                     '-o', os.path.join(out_dir, exe_name),
                     src_name] + list(flags)),
      run_args=[os.path.join(out_dir, exe_name)])

class CXX14Code(basic_codes.CodeBase):
  PREFIX = 'cxx14'
  EXTENSIONS = ['cc14', 'cxx14', 'cpp14']

  def __init__(self, src_name, src_dir, out_dir, flags=[]):
    exe_name = os.path.splitext(src_name)[0] + consts.EXE_EXT
    super(CXX14Code, self).__init__(
      src_name=src_name, src_dir=src_dir, out_dir=out_dir,
      compile_args=(['g++', '-O2', '-std=c++14',
                     '-o', os.path.join(out_dir, exe_name),
                     src_name] + list(flags)),
      run_args=[os.path.join(out_dir, exe_name)])

codes.registry.Override('CCode', CCode)
codes.registry.Override('CXXCode', CXXCode)
codes.registry.Add(CXX11Code)
codes.registry.Add(CXX14Code)

