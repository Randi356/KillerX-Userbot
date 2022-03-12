# Ported By @rencprx

""" Init file which loads all of the modules """
from userbot import LOGS


def __list_all_modules():
    from os.path import dirname, isfile, relpath
    from glob import glob

    root_dir = dirname(__file__)
    mod_paths = glob(root_dir + "/**/*.py", recursive=True)
    all_modules = [
        '.'.join(relpath(f, root_dir).split('/'))[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]
    return all_modules


ALL_MODULES = sorted(__list_all_modules())
LOGS.info("Modules to load: %s", str(ALL_MODULES))
__all__ = ALL_MODULES + ["ALL_MODULES"]
