#!/usr/bin/env python
import sys
# force our version
sys.path.insert(0,'./vendor/pytodotxt')

import pytodotxt
import re

class TodoTxt_from_lines(pytodotxt.TodoTxt):
    def __init__(self, filename=None, encoding='utf-8', task_class=None):
        if filename is None:
            filename = '/dev/null'
        # allow to force lines content on save()
        self.get_lines_once = None
        super().__init__(filename, encoding, task_class)

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
            self.add_task(line, linenr)

        return self.tasks

    def add_task(self, line, linenr=None):
        if linenr is None:
            linenr = len(self.tasks)
        task = self.task_class(line.strip(), linenr=linenr, todotxt=self)
        self.tasks.append(task)

    def get_text_lines(self):
        """Get all Task as list on lines (str)
        """
        if self.get_lines_once is not None:
            lines = self.get_lines_once
            self.get_lines_once = None
            return lines
        else:
            return [str(task) for task in
                     sorted(self.tasks, key=lambda t: t.linenr if t.linenr is not None else len(self.tasks))]

    def save(self, target=None, safe=True, linesep=None, lines=None):
        if lines is not None:
            self.get_lines_once = lines
        super().save(target, safe, linesep)

