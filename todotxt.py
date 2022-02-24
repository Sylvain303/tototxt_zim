#!/usr/bin/env python
#
# this script is a prototype to manage todo.txt lines embedded into a Zim-ziki's page
#
# Usage: ./todotxt.py ZIM_NOTEBOOK ZIM_PAGENAME ZIM_SECTION
#
# Arguments:
#   ZIM_NOTEBOOK     a local path to the Notebook root, ex: ~/Notebooks/Notes
#   ZIM_PAGENAME     a zim name to a page, that can be obtained by SHIFT+CTRL+L inside Zim
#                    ex: "knowledge:todo.txt:sample todo list"
#   ZIM_PAGENAME     the name of the section in the page that hold the check-boxes that
#                    store the todo.txt format as a continuous block of check-boxes.

import sys
# force our version
sys.path.insert(0,'./vendor/pytodotxt')

# this code is based on pytodotxt from https://github.com/vonshednob/pytodotxt
#import pytodotxt
from extended_todotxt_task import ZimTask
from extended_todotxt_todotxt import TodoTxt_from_lines
from extended_todotxt_todotxtparser import TodoTxtParser_from_lines
from zimpage_todotxt import ZimPage_todotxt
from time import strftime,localtime

# ====================================================================== main

if len(sys.argv) == 1:
    # our local config, using an exported page
    zim_notebook = "./Notebooks/Notes"
    zim_page = "knowledge:todo.txt:sample todo list"
    zim_section = 'Todo section'
else:
    zim_notebook = sys.argv[1]
    zim_page = sys.argv[2]
    zim_section = sys.argv[3]

zim_todotxt = ZimPage_todotxt(zim_notebook, zim_page)
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

todotxt_zim = TodoTxt_from_lines('zimtodo.txt', parser=TodoTxtParser_from_lines(task_type=ZimTask))
# parse our lines buffer through the extended TodoTxtParser_from_lines class
todotxt_zim.parse_from_lines(todos_zim_lines)

todotxt_zim.add(ZimTask("new tasks"))

print(f"================== list of tasks not completed: {len(todotxt_zim.tasks)}")
for t in todotxt_zim.tasks:
    if not t.is_completed:
        print(f"{t.linenr}: {t.description}")

    if 'finish him' in t.description:
        t.is_completed = True
        print(f"set_completed: {t.linenr} {t.description}")

#del todotxt_zim.tasks[-1]

# save modified zim page
if not zim_todotxt.save_todos_into_zimpage(zim_section, todotxt_zim):
    print(f"error: writing outout to {zim_todotxt.get_zim_filename()}")

# for debug purpose we can still save as normal todo.txt too (will use TodoTxt filename argument)
todotxt_zim.save()

for l in todotxt_zim.lines:
    print(l)

