from typing import List, Optional

__version__ = "22.0.3"


def main(args: Optional[List[str]] = None) -> int:
    """This is an internal API only meant for use by pip's own console scripts.

    For additional details, see https://github.com/pypa/pip/issues/7498.
    """
    from pipenv.patched.notpip._internal.utils.entrypoints import _wrapper

    return _wrapper(args)
