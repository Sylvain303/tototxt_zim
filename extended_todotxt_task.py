#!/usr/bin/env python
import pytodotxt
import re

class ZimTask(pytodotxt.Task):
    MATCH_TODO_RE = re.compile(r'^\[(.)\] (.+)')
    def __init__(self, line=None, linenr=None, todotxt=None):
        self.zim_check_box_char = None
        self.is_active = False
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

            if status_char == ' ':
                self.zim_check_box_char = 'space'
            elif status_char == '>':
                self.is_active = True
                #print(f"ACTIVE: {txt}")
        # parse
        super().parse(line)
        #if self.is_active:
        #    print(f"ACTIVE after super().parse: {self}")


    # output to string
    def __str__(self):
        zim_check_box_char = self.zim_check_box_char
        if self.zim_check_box_char is None or self.zim_check_box_char == 'space':
            zim_check_box_char = ' '

        task_str = super().__str__()
        if self.is_completed:
            self.zim_check_box_char = '*'
            # remove is_completed 'x ' prefix
            task_str = task_str[2:]

        if not self.is_active and self.zim_check_box_char == '>':
            zim_check_box_char = ' '

        task_str = f"[{zim_check_box_char}] {task_str}"
        return task_str

    # setter for completed keep coupling with container parent if present
    # can be used in loop:
    #
    #   for t in todotxt_zim.tasks:
    #       if condition_met:
    #           t.set_completed()
    #           print(f"set_completed: {t.linenr}")
    def set_completed(self, completed=True, completion_date=None):
        self.is_completed = completed

        # completed can be True without completion_date
        # But could completed be Fasle with a completion_date?
        # Or should we remove completion_date when completed is set to Fasle?
        if completion_date is not None:
            self.completion_date = completion_date

        # update parent item in tasks[]
        if self.todotxt and self.linenr and self == self.todotxt.tasks[self.linenr]:
            self.todotxt.tasks[self.linenr].is_completed = self.is_completed
            self.todotxt.tasks[self.linenr].completion_date = self.completion_date

