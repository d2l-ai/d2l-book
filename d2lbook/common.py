import re
from typing import Optional, List, Any, Callable, Tuple

# Our special mark in markdown, e.g. :label:`chapter_intro`
md_mark_pattern = re.compile(':([-\/\\._\w\d]+):(`[\ \*-\/\\\._\w\d]+`)?')
# Same for md_mark_pattern, but for rst files
rst_mark_pattern = re.compile(':([-\/\\._\w\d]+):(``[\ \*-\/\\\._\w\d]+``)?')
# The source code tab mark
source_tab_pattern = re.compile('# *@tab +([\w\,\ ]+)')

# Markdown code fence
md_code_fence = re.compile('(```+) *(.*)')

def group_list(list_obj: List[Any], status_fn: Callable[[Any, Any], Any]
              ) -> List[Tuple[Any, List[Any]]]:
    """Cut a list into multiple parts when fn returns True"""
    prev_status = None
    prev_pos = 0
    ret = []
    for i, item in enumerate(list_obj):
        cur_status = status_fn(item, prev_status)
        if prev_status is not None and cur_status != prev_status:
            ret.append((prev_status, list_obj[prev_pos:i]))
            prev_pos = i
        prev_status = cur_status
    ret.append((cur_status, list_obj[prev_pos:]))
    return ret
