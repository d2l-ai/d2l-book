import os

def rm_ext(filename):
    return os.path.splitext(filename)[0]

def find_files(pattern, root):
    fnames = []
    patterns = pattern.split(' ')
    for p in patterns:
        if len(p) == 0:
            continue
        p = os.path.join(root, p)
        if os.path.isdir(p):
            p += '*'
        for fn in glob.glob(p):
            if not os.path.isfile(p):
                fnames.append(fn)
    return fnames

def get_mtimes(fnames):
    if isinstance(fnames, str):
        fnames = [fnames]
    return [os.path.getmtime(fn) for fn in fnames]

def get_updated_files(src_fnames, src_dir, tgt_dir, new_ext=None, deps_mtime=0):
    updated_fnames = []
    for src_fn in src_fnames:
        tgt_fn = os.path.join(tgt_dir, os.path.relpath(src_fn, src_dir))
        if new_ext is not None:
            tgt_fn = rm_ext(tgt_fn) + '.' + new_ext
        if (not os.path.exists(tgt_fn) # new
            or os.path.getmtime(src_fn) > os.path.getmtime(tgt_fn) # target is old
            or os.path.getmtime(src_fn) < deps_mtime): # deps is updated
            updated_fnames.append((src_fn, tgt_fn))
    return updated_fnames

def mkdir(dirname):
    os.makedirs(dirname, exist_ok=True)

def run_cmd(cmd):
    if isinstance(cmd, str):
        cmd = [cmd]
    os.system(' '.join(cmd))
