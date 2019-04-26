import logging
import shutil

__all__  = ['clear']

def clear(config):
    build_dir = config.tgt_dir
    logging.info('Delete %s', build_dir)
    shutil.rmtree(build_dir, ignore_errors=True)
