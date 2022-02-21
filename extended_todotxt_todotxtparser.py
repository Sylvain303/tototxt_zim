#!/usr/bin/env python
import sys
# force our version
sys.path.insert(0,'./vendor/pytodotxt')

import pytodotxt

class TodoTxtParser_from_lines(pytodotxt.TodoTxtParser):
    def parse(self, target, filter_func=None):
        if isinstance(target, list):
            return self.parse_from_lines(target, filter_func)
        else:
            return super().parse(target)

    def parse_from_lines(self, lines, filter_func=None):
        """(Re)parse an input from list of line of text used by parse()

        :param lines: a striped list of line of text
        :param filter_func: an optional function or method to get str from
                            if lines contain more complex object.
        :return: a list of tasks found in ``lines``
        """

        tasks = []
        # read lines and parse them as tasks
        for linenr, line in enumerate(lines):
            if callable(filter_func):
                line = filter_func(line)

            if len(line.strip()) == 0:
                continue

            tasks.append(self.task_type(line, linenr))

        return tasks


