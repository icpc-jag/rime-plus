#!/usr/bin/python

import re
import sys

MAX = 1000000000

def main():
  m = re.match(r'^(\d+)\n$', sys.stdin.read())
  assert m, 'Does not match with regexp'
  a, = map(int, m.groups())
  assert 0 <= a <= MAX, 'a out of range: %d' % a

if __name__ == '__main__':
  main()
