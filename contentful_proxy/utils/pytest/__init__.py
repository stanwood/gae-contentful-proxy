import sys


def reload_pkg_resources():
    """
    Reload `pkg_resources` modules (unload version imported from default path).
    """

    for module in sys.modules.keys():
        if module.startswith('pkg_resources'):
            del sys.modules[module]

    sys.meta_path = [
        importer
        for importer in sys.meta_path
        if importer.__class__.__module__ != 'pkg_resources.extern'
    ]
reload_pkg_resources()
