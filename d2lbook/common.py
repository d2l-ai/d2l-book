import re
from typing import Optional, List, Any, Callable, Tuple

# Our special mark in markdown, e.g. :label:`chapter_intro`
md_mark_pattern = re.compile(':([-\/\\._\w]+):(`[\ \*-\/\\\._\w]+`)?')
# Same for md_mark_pattern, but for rst files
rst_mark_pattern = re.compile(':([-\/\\._\w]+):(``[\ \*-\/\\\._\w]+``)?')
# The source code tab mark
source_tab_pattern = re.compile('# *@tab +([\w\,\ ]+)')
source_tab_pattern_2 = re.compile('%%tab +([\w\,\ ]+)')

# Markdown code fence
md_code_fence = re.compile('(```+) *(.*)')

def split_list(list_obj: List[Any], split_fn: Callable[[Any], Any]) -> List[List[Any]]:
    """Cut a list into multiple parts when fn returns True"""
    prev_pos = 0
    ret = []
    for i, item in enumerate(list_obj):
        if split_fn(item):
            ret.append(list_obj[prev_pos:i])
            prev_pos = i
    ret.append(list_obj[prev_pos:])
    return ret

def group_list(
        list_obj: List[Any],
        status_fn: Callable[[Any, Any], Any]) -> List[Tuple[Any, List[Any]]]:
    """Cut a list into multiple parts when based on the value returned by status_fn"""
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

def head_spaces(line: str):
    """"Return the head spaces."""
    return line[: len(line)-len(line.lstrip())]

def flatten(x):
    """flatten a list of lists into a list."""
    return [item for sublist in x for item in sublist]

def print_list(x):
    print(f'len: {len(x)}')
    for i, y in enumerate(x):
        print(f'{i}\t{y}')

def print_dict(x):
    print(f'len: {len(x)}')
    for k in x:
        print(f'{k}\t{x[k]}')
