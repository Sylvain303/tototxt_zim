#!/usr/bin/env python
import re
import io
from pathlib import Path
from collections import namedtuple

# our new type to store extrated section from zim page with _extract_todo_from_zim_checkbox()
Section_line = namedtuple('Section_line', ['lineno', 'txt'])

class ZimPage_todotxt:
    MATCH_TODO_RE = re.compile(r'^\[(.)\] (.+\n?)')
    def __init__(self, zim_notebook, zim_page):
        self.zim_notebook = zim_notebook
        self.zim_page = zim_page
        self.tasks = []

    def get_zim_filename(self):
        filename = self.zim_page.replace(':', '/')
        filename = filename.replace(' ', '_')
        return f"{Path(self.zim_notebook).expanduser()}/{filename}.txt"

    def _read_zim_lines(self, strip_lines=True):
        filename = self.get_zim_filename()
        with open(filename) as f:
            if strip_lines:
               lines = [ l.strip() for l in f.readlines() ]
            else:
                lines = f.readlines()
        return lines

    def get_todo_from_zimpage_raw(self, section, match_filter=None, strip_lines=True):
        lines = self._read_zim_lines(strip_lines)
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
                #print("section", l.strip())
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
            if start_line == 0 and n > 0 and self.__class__.MATCH_TODO_RE.match(sl.txt):
                start_line = sl.lineno
                continue
            if start_line > 0 and n > 0:
                # increase end_line to the current line
                end_line = sl.lineno
            if start_line > 0 and n == 0:
                # found an empty line stop
                break

        if start_line == 0:
            # no content found
            # or instead of leaving False we could replace the whole section?
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
                # print(f"remove line {i+1}")
                del lines[i]

        # full page update output
        #for i, l in enumerate(lines):
        #    print(f"{(i+1):02d} {l}")

        # save back to the file
        filename = self.get_zim_filename()
        # we call our mofified TodoTxt with get_text_lines()
        todotxt.save(target=filename, safe=True, lines=lines)

        return True

    def get_todo_as_StringIO(self, section):
        io_buffer = io.StringIO()
        section_found, lines = self.get_todo_from_zimpage_raw(section, self._extract_todo_from_zim_checkbox, strip_lines=False)
        if not section_found:
            return io_buffer

        for l in lines:
            io_buffer.write(l)
        # rewind
        io_buffer.seek(0)
        return io_buffer
