#!/usr/bin/env python
import sys
# force our version
sys.path.insert(0,'./vendor/pytodotxt')

import pytodotxt
import re

class ZimTask(pytodotxt.Task):
    MATCH_TODO_RE = re.compile(r'^\[(.)\] (.+)')
    def __init__(self, line=None, linenr=None, todotxt=None):
        self.zim_check_box_char = None
        super().__init__(line, linenr, todotxt)

    def parse(self, line):
        m = self.__class__.MATCH_TODO_RE.match(line)
        if m:
            # only match todos
            status_char = m.group(1)
            self.zim_check_box_char = status_char

            txt = m.group(2)
            if status_char == '*':
                # convert to todo.txt completed format
                line = f"x {txt}"
            else:
                line = txt
        # parse
        super().parse(line)

    # output to string
    def __str__(self):
        result = super().__str__()
        if self.is_completed:
            self.zim_check_box_char = '*'
            # remove is_completed 'x ' prefix
            result = result[2:]

        zim_check_box_char = self.zim_check_box_char
        if self.zim_check_box_char is None:
            zim_check_box_char = ' '

        result = f"[{zim_check_box_char}] {result}"
        return result

