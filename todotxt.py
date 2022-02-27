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

# this code is based on pytodotxt from https://github.com/vonshednob/pytodotxt
#import pytodotxt
from extended_todotxt_task import ZimTask
from extended_todotxt_todotxt import TodoTxt_from_lines
from extended_todotxt_todotxtparser import TodoTxtParser_from_lines
from zimpage_todotxt import ZimPage_todotxt
from time import strftime,localtime

def init_zimtodo(zim_section_name=None):
    zim_todotxt = ZimPage_todotxt(filename=argument_filename, zim_section_name=zim_section_name)
    print(f"zim: {zim_todotxt.get_zim_filename()}")
    zim_section = zim_todotxt.get_todo_zim_section_name()
    print(f"parsing section: '{zim_section}'")
    section_found, todos_zim_lines_raw = zim_todotxt.get_lines_from_zim_section(zim_section)
    if not section_found:
        print(f"section not found: '{zim_section}', exiting")
        sys.exit(1)

    todotxt_zim = TodoTxt_from_lines('zimtodo.txt', parser=TodoTxtParser_from_lines(task_type=ZimTask))
    # parse our lines buffer through the extended TodoTxtParser_from_lines class
    todotxt_zim.parse_from_lines(todos_zim_lines_raw)
    zim_todotxt.my_todo = todotxt_zim
    return zim_todotxt

def debug():
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

# ====================================================================== main

#zim_todotxt = ZimPage_todotxt(zim_notebook, zim_page)
argument_filename=sys.argv[1]
action=sys.argv[2]


# active-on-top: will reorder active ZimTask the first ordered active will become the top tasks
# all other active became inactive with appended attibute: next:active
if action == 'active-on-top':
    zim_todotxt = init_zimtodo()

    actives = []
    for t in zim_todotxt.my_todo.tasks:
        if t.is_active:
            actives.append(t)
    zim_todotxt.make_first(actives)
    zim_todotxt.save_todos_into_zimpage(zim_todotxt.zim_section_name)
elif action == "zim_section_name":
    zim_todotxt = ZimPage_todotxt(filename=argument_filename)
    print(zim_todotxt.get_todo_zim_section_name())
    found, lines = zim_todotxt.get_lines_from_zim_section()
    if not found:
        print(f"section not found: '{zim_todotxt.zim_section_name}'")
    else:
        for l in lines:
            print(l)
else:
    print(f"action unknonwn: {action}")

