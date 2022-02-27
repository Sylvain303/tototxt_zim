#!/usr/bin/env python
import re
import io
from pathlib import Path
from collections import namedtuple

# our new type to store extrated section from zim page with _extract_todo_from_zim_checkbox()
Section_line = namedtuple('Section_line', ['lineno', 'txt'])

class ZimPage_todotxt:
    MATCH_TODO_RE = re.compile(r'^\[(.)\] (.+\n?)')
    def __init__(self, zim_notebook=None, zim_page=None, filename=None, zim_section_name=None):
        self.zim_notebook = None
        self.zim_page = None
        self.filename = None
        self.my_todo = None
        self.zim_config_section = "Todo config"
        self.zim_section_name = zim_section_name

        if zim_notebook is None and zim_page is None and filename is None:
            raise("must define, zim_notebook+zim_page or filename")
        elif filename is None:
            self.zim_notebook = zim_notebook
            self.zim_page = zim_page
        else:
            self.filename = filename

    def get_zim_filename(self):
        if self.filename is not None:
            return self.filename
        else:
            filename = self.zim_page.replace(':', '/')
            filename = filename.replace(' ', '_')
            return f"{Path(self.zim_notebook).expanduser()}/{filename}.txt"

    def get_todo_zim_section_name(self):
        """
        look for `zim_config` section in the same page
        """
        found, zim_section = self.get_lines_from_zim_section(
                    self.zim_config_section,
                    match_filter=lambda l: l if len(l) > 2 else None
                )
        if found:
            self.zim_section_name = zim_section[0]
        else:
            print(f"section_found: {self.zim_config_section}")
        return self.zim_section_name

    def _read_zim_lines(self, strip_lines=True):
        filename = self.get_zim_filename()
        with open(filename) as f:
            if strip_lines:
               lines = [ l.strip() for l in f.readlines() ]
            else:
                lines = f.readlines()
        return lines

    def get_lines_from_zim_section(self, section_name=None, match_filter=None, strip_lines=True):
        if section_name is None:
            section_name = self.zim_section_name

        if section_name is None:
            raise(f"section_name is None")

        lines = self._read_zim_lines(strip_lines)
        section_found = False
        section_lines = []
        section_match = re.compile(f'^=+ {section_name} =+$')
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
                    section_lines.append(l)

        return section_found, section_lines

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
        return self.get_lines_from_zim_section(section, self._extract_todo_from_zim_checkbox)

    # TODO: could it be accomplished with get_lines_from_zim_section()?
    def _match_zim_section(self, section_name, lines):
        """
        return list of tuple (num_line, txt) for the matching content in `section_name`, into `lines
        """
        section_found = False
        section_lines = []
        for nr, l in enumerate(lines):
            if section_name in l:
                section_found = True
                #print("section_name", l.strip())
                continue
            if section_found and l.startswith('==='):
                section_found = False
                break
            if section_found:
                txt = l.strip()
                section_lines.append(Section_line(nr+1, txt))
        return section_lines

    def save_todos_into_zimpage(self, section):
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
        nb_task = len(self.my_todo.tasks)
        i = start_line
        for t in self.my_todo.tasks:
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
        self.my_todo.save(target=filename, safe=True, lines=lines)

        return True

    def get_todo_as_StringIO(self, section):
        io_buffer = io.StringIO()
        section_found, lines = self.get_lines_from_zim_section(section, self._extract_todo_from_zim_checkbox, strip_lines=False)
        if not section_found:
            return io_buffer

        for l in lines:
            io_buffer.write(l)
        # rewind
        io_buffer.seek(0)
        return io_buffer

    def make_first(self, actives_task):
        if len(actives_task) == 0:
            return
        others = list(filter(lambda t: t not in actives_task and not t.is_completed, self.my_todo.tasks))
        dones = list(filter(lambda t: t.is_completed, self.my_todo.tasks))
        actives_task[0].remove_attribute('next')
        for t in actives_task[1:]:
            t.is_active = False
            t.remove_attribute('next')
            #print(f"set inactive: {t}")
            t.add_attribute('next', 'active')

        # reset new order
        self.my_todo.tasks = actives_task + others + dones
