from collections import Mapping, namedtuple

from gogtool.main import initialize_gogtool, run_gogtool


def namedtuple_with_defaults(typename, field_names, default_values=()):
    """
    Factory to create a namedtuple with optional default values.

    Reference: https://stackoverflow.com/a/18348004/8074325
    """
    T = namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


Args = namedtuple_with_defaults(
    'Args',
    [
        'clean',
        'debug',
        'download',
        'edit_lgogconfig',
        'files',
        'info',
        'install',
        'launch',
        'list',
        'platform',
        'refresh',
        'remove',
        'uninstall',
        'update',
        'view'
    ],
    dict(
        clean=False,
        debug='warning',
        download=None,
        edit_lgogconfig=False,
        files=False,
        info=False,
        install=None,
        launch=None,
        list=None,
        platform='l',
        refresh=False,
        remove=None,
        uninstall=None,
        update=None,
        view=None
    )
)


def main(args):
    config, library = initialize_gogtool(args)

    try:
        return run_gogtool(config, library, args, cli=False)
    except KeyboardInterrupt:
        pass
