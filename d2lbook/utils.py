import os
import glob
import shutil
import logging

def rm_ext(filename):
    return os.path.splitext(filename)[0]

def find_files(pattern, root=None):
    fnames = []
    patterns = pattern.split(' ')
    for p in patterns:
        if len(p) == 0:
            continue
        if root is not None:
            p = os.path.join(root, p)
        if os.path.isdir(p):
            p += '**'
        for fn in glob.glob(p, recursive=True):
            if os.path.isfile(fn):
                fnames.append(fn)
    return fnames

def get_mtimes(fnames):
    if isinstance(fnames, str):
        return os.path.getmtime(fnames)
    return [os.path.getmtime(fn) for fn in fnames]

def split_fname(fname, base_dir, ext=None):
    fname = os.path.relpath(fname, base_dir)
    base, fext = os.path.splitext(fname)
    if fext.startswith('.'):
        fext = fext[1:]
    if ext and ext != fext:
        logging.warn("%s doesn't have extension %s", fname, ext)
    return base, fext

def get_tgt_fname(src_dir, src_fname, tgt_dir, src_ext, tgt_ext):
    fname, ext = split_fname(src_fname, src_dir, src_ext)
    if tgt_ext:
        ext = tgt_ext
    return os.path.join(tgt_dir, fname+'.'+ext)

def get_updated_files(src_fnames, src_dir, tgt_dir,
                      src_ext=None, tgt_ext=None, deps_mtime=0):
    updated_fnames = []
    for src_fn in src_fnames:
        tgt_fn = get_tgt_fname(src_dir, src_fn, tgt_dir, src_ext, tgt_ext)
        if (not os.path.exists(tgt_fn) # new
            or get_mtimes(src_fn) > get_mtimes(tgt_fn) # target is old
            or get_mtimes(tgt_fn) < deps_mtime): # deps is updated
            updated_fnames.append((src_fn, tgt_fn))
    return updated_fnames

def get_removed_files(pattern, src_dir, tgt_dir, src_ext=None, tgt_ext=None):
    patterns = pattern.split(' ')
    for i, p in enumerate(patterns):
        f, ext = os.path.splitext(p)
        if ext == '.'+src_ext and tgt_ext:
            patterns[i] = f + '.' + tgt_ext
    tgt_files = find_files(' '.join(patterns), tgt_dir)
    removed_fnames = []
    for tgt_fn in tgt_files:
        src_fn = get_tgt_fname(tgt_dir, tgt_fn, src_dir, tgt_ext, src_ext)
        if not os.path.exists(src_fn):
            removed_fnames.append(tgt_fn)
    return removed_fnames

def mkdir(dirname):
    os.makedirs(dirname, exist_ok=True)

def copy(src, tgt):
    mkdir(os.path.dirname(tgt))
    shutil.copy(src, tgt)


def run_cmd(cmd):
    if isinstance(cmd, str):
        cmd = [cmd]
    ret = os.system(' '.join(cmd))
    if ret != 0:
        exit(-1)
