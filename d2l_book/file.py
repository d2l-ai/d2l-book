"""Deal files"""
import os
import glob

def find_file(pattern, root='.'):
    fnames = []
    patterns = pattern.split(' ')
    for p in patterns:
        p = os.path.join(root, p)
        if os.path.isdir(p):
            p += '*'
        for fn in glob.glob(p):
            if os.path.isfile(p):
                fnames.append(p)
    return fnames

def get_mtime(fnames):
    if isinstance(fnames, str):
        fnames = [fnames]
    return [os.path.getmtime(fn) for fn in fnames]
