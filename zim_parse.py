#import logging
#import itertools

#from zim.parsing import link_type
#from zim.formats.wiki import WIKI_FORMAT_VERSION # FIXME hard coded preference for wiki format

#import zim.fs
#import zim.newfs

# /usr/lib/python3/dist-packages/zim/notebook/page.py
import zim.notebook.page
import zim.formats
from zim.tokenparser import collect_untill_end_token, tokens_to_text
from zim.formats import get_format, \
	UNCHECKED_BOX, CHECKED_BOX, XCHECKED_BOX, BULLET, TAG, \
	HEADING, PARAGRAPH, BLOCK, NUMBEREDLIST, BULLETLIST, LISTITEM, STRIKE, \
	Visitor, VisitorSkip
from zim.tokenparser import skip_to_end_token, TEXT, END

#import zim.datetimetz as datetime

def get_todo_from_token(filename):
    zim_format = zim.formats.get_format('wiki')
    parser = zim_format.Parser()
    with open(filename) as f:
        text = f.read()
    parsetree = parser.parse(text, file_input=True)
    # from get_headings(parsetree) /usr/lib/python3/dist-packages/zim/plugins/tableofcontents.py
    tokens = parsetree.iter_tokens()
    stack = [(0, None, [])]
    current_section = ""
    for t in tokens:
        if t[0] == HEADING:
            level = int(t[1]['level'])
            text = tokens_to_text( collect_untill_end_token(tokens, HEADING) )
            while stack[-1][0] >= level:
                stack.pop()
            node = (level, text, [])
            stack[-1][2].append(node)
            stack.append(node)
        elif t[0] == LISTITEM:
            # _parse_list() plugins/tasklist/indexer.py
            bullet = t[1].get('bullet')
            line = []
            for r in tokens:
                if t[0] in (BULLETLIST, NUMBEREDLIST) \
                or t == (END, LISTITEM):
                        next_token = t
                        break
                else:
                        line.append(t)
            print(bullet, line)
        else:
            print(t[0])
    print(stack[0][-1])

