#!/usr/bin/env python

import sys
# force our version
sys.path.insert(0,'./vendor/pytodotxt')

from pathlib import Path
import re
import pytodotxt
from collections import namedtuple
from extended_todotxt_task import ZimTask
from extended_todotxt_todotxt import TodoTxt_from_lines

class ZimPage_todotxt:
    MATCH_TODO_RE = re.compile(r'^\[(.)\] (.+)')
    def __init__(self, zim_notebook, zim_page):
        self.zim_notebook = zim_notebook
        self.zim_page = zim_page

    def get_zim_filename(self):
        filename = self.zim_page.replace(':', '/')
        filename = filename.replace(' ', '_')
        return f"{Path(self.zim_notebook).expanduser()}/{filename}.txt"

    def _read_zim_lines(self):
        filename = self.get_zim_filename()
        with open(filename) as f:
           lines = [ l.strip() for l in f.readlines() ]
        return lines

    def get_todo_from_zimpage_raw(self, section, match_filter=None):
        lines = self._read_zim_lines()
        section_found = False
        todos = []
        section_match = re.compile(f'^=+ {section} =+$')
        for l in lines:
            # section detection start
            if not section_found and section_match.match(l):
                section_found = True
                continue
            if section_found and l.startswith('==='):
                # end section living loop
                break
            if section_found:
                if callable(match_filter):
                    l = match_filter(l)
                if l is not None:
                    todos.append(l)

        return section_found, todos

    def _extract_todo_from_zim_checkbox(self, line):
        m = self.__class__.MATCH_TODO_RE.match(line)
        if m:
            # only match todos
            status_char = m.group(1)
            txt = m.group(2)
            if status_char == '*':
                # convert to todo.txt completed format
                txt = f"x {txt}"
            return txt
        else:
            return None

    def get_todo_from_zimpage(self, section):
        return self.get_todo_from_zimpage_raw(section, self._extract_todo_from_zim_checkbox)

    def _match_zim_section(self, section, lines):
        section_found = False
        section_lines = []
        for nr, l in enumerate(lines):
            if section in l:
                section_found = True
                print("section", l.strip())
                continue
            if section_found and l.startswith('==='):
                section_found = False
                break
            if section_found:
                txt = l.strip()
                section_lines.append(Section_line(nr+1, txt))

        return section_lines

    def save_todos_into_zimpage(self, section, todotxt):
        lines = self._read_zim_lines()
        section_lines = self._match_zim_section(section, lines)

        # seek first non empty line for replace the continuous
        # block of lines
        start_line = 0
        end_line = 0
        for sl in section_lines:
            #print(f"actual lines: {sl}")
            n = len(sl.txt)
            if start_line == 0 and n > 0:
                start_line = sl.lineno
                continue
            if start_line > 0 and n > 0:
                # increase end_line to the current line
                end_line = sl.lineno
            if n == 0:
                # found an empty line stop
                break

        if start_line == 0:
            # no content found
            return False

        # no empty was found after start_line so assuming it ends
        # on the last line
        if end_line == 0:
            end_line = section_lines[-1].lineno

        #print(f"{start_line}, {end_line} -------- replace with:")

        # replace loop, will replace actual zim page lines
        # within start_line to end_line with the new content
        nb_task = len(todotxt.tasks)
        i = start_line
        for t in todotxt.tasks:
            txt = str(t)
            # update lines
            if i <= end_line:
                # replace
                lines[i-1] = txt
            else:
                # insert some lines
                lines.insert(i-1, txt)
            i += 1

        # compare if we are saving fewer lines than it was into de zim page
        pos_last_updated_task = start_line + nb_task -1
        if pos_last_updated_task < end_line:
            # remove extra size lines
            for i in range(pos_last_updated_task, end_line):
                print(f"remove line {i+1}")
                del lines[i]

        # full page update output
        for i, l in enumerate(lines):
            print(f"{(i+1):02d} {l}")

        # save back to the file
        filename = self.get_zim_filename()
        # we call our mofified TodoTxt with get_text_lines()
        todotxt.save(target=filename, safe=True, lines=lines)

        return True

# ====================================================================== main
# out type to store extrated section from zim page with _extract_todo_from_zim_checkbox()
Section_line = namedtuple('Section_line', ['lineno', 'txt'])

# out config
zim_page = "knowledge:todo.txt:sample todo list"
zim_notebook = "./Notebooks/Notes"

zim_todotxt = ZimPage_todotxt(zim_notebook, zim_page)
zim_section = 'Todo section'
print(f"zim: {zim_todotxt.get_zim_filename()}")
section_found, todos_zim_lines_raw = zim_todotxt.get_todo_from_zimpage_raw(zim_section)
if not section_found:
    print(f"section not found: {zim_section}, exiting")
    sys.exit(1)

section_found, todos_zim_lines = zim_todotxt.get_todo_from_zimpage(zim_section)


print(todos_zim_lines)
print(todos_zim_lines_raw)

#todotxt = pytodotxt.TodoTxt('todo.txt')
#todotxt.parse()
#for task in todotxt.tasks:
#    if not task.is_completed:
#        print(task.description)

todotxt_zim = TodoTxt_from_lines('zimtodo.txt', task_class=ZimTask)
todotxt_zim.parse_from_lines(todos_zim_lines)
todotxt_zim.add_task("new tasks")

print(f"================== parse_from_lines todotxt_zim list not completed: {len(todotxt_zim.tasks)}")
for t in todotxt_zim.tasks:
    if not t.is_completed:
        print(f"{t.linenr}: {t.description}")

    if 'finish him' in t.description:
        t.set_completed()
        print(f"set_completed: {t.linenr}")

#del todotxt_zim.tasks[-1]
zim_todotxt.save_todos_into_zimpage(zim_section, todotxt_zim)
todotxt_zim.save()
