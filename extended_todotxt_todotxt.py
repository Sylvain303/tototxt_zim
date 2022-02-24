#!/usr/bin/env python
import sys
# force our version
sys.path.insert(0,'./vendor/pytodotxt')

import pytodotxt
import re

class TodoTxt_from_lines(pytodotxt.TodoTxt):
    def __init__(self, filename=None, encoding='utf-8', parser=None):
        if filename is None:
            filename = '/dev/null'
        # allow to force lines content on save()
        self.get_lines_once = None
        super().__init__(filename, encoding, parser)

    # replace TodoTxt.parse() which only handle its own filename
    def parse_from_lines(self, lines, filter_func=None):
        """(Re)parse an input from list of line of text
        used by parse()
        filter_func: an optional function or method to get str from
                     if lines contain more complex object.
        """
        self.tasks = []

        # read lines and parse them as tasks
        for linenr, line in enumerate(lines):
            if callable(filter_func):
                line = filter_func(line)

            if len(line.strip()) == 0:
                continue
            self.tasks.append(self.parser.task_type(line, linenr))

        return self.tasks

    # override build_lines() allows to override input list with our own lines if get_lines_once is set.
    # Used to call our extended save() with lines as extra argument.
    def build_lines(self):
        """Get all Task as list of lines (str)
        """
        if self.get_lines_once is not None:
            lines = self.get_lines_once
            self.get_lines_once = None
            return lines
        else:
            return super().build_lines()

    # wrapper TodoTxt.save() with lines as input if lines argument is given
    def save(self, target=None, safe=True, linesep=None, lines=None):
        if lines is not None:
            self.get_lines_once = lines
        super().save(target, safe, linesep)

