"""A single place for constructing and exposing the main parser
"""

import os
import sys


__all__ = ["create_main_parser", "parse_command"]


def create_main_parser():
    """Creates and returns the main parser for pip's CLI
    """

    from pipenv.patched.notpip import __version__
    from pipenv.patched.notpip._internal.cli import cmdoptions
    from pipenv.patched.notpip._internal.cli.parser import (
        ConfigOptionParser, UpdatingDefaultsHelpFormatter,
    )
    from pipenv.patched.notpip._internal.commands import get_summaries
    from pipenv.patched.notpip._internal.utils.misc import get_prog
    parser_kw = {
        'usage': '\n%prog <command> [options]',
        'add_help_option': False,
        'formatter': UpdatingDefaultsHelpFormatter(),
        'name': 'global',
        'prog': get_prog(),
    }

    parser = ConfigOptionParser(**parser_kw)
    parser.disable_interspersed_args()

    pip_pkg_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
    ))
    parser.version = 'pip %s from %s (python %s)' % (
        __version__, pip_pkg_dir, sys.version[:3],
    )

    # add the general options
    gen_opts = cmdoptions.make_option_group(cmdoptions.general_group, parser)
    parser.add_option_group(gen_opts)

    parser.main = True  # so the help formatter knows

    # create command listing for description
    command_summaries = get_summaries()
    description = [''] + ['%-27s %s' % (i, j) for i, j in command_summaries]
    parser.description = '\n'.join(description)

    return parser


def parse_command(args):
    from pipenv.patched.notpip._internal.commands import (
        commands_dict, get_similar_commands
    )
    from pipenv.patched.notpip._internal.exceptions import CommandError
    parser = create_main_parser()

    # Note: parser calls disable_interspersed_args(), so the result of this
    # call is to split the initial args into the general options before the
    # subcommand and everything else.
    # For example:
    #  args: ['--timeout=5', 'install', '--user', 'INITools']
    #  general_options: ['--timeout==5']
    #  args_else: ['install', '--user', 'INITools']
    general_options, args_else = parser.parse_args(args)

    # --version
    if general_options.version:
        sys.stdout.write(parser.version)
        sys.stdout.write(os.linesep)
        sys.exit()

    # pip || pip help -> print_help()
    if not args_else or (args_else[0] == 'help' and len(args_else) == 1):
        parser.print_help()
        sys.exit()

    # the subcommand name
    cmd_name = args_else[0]

    if cmd_name not in commands_dict:
        guess = get_similar_commands(cmd_name)

        msg = ['unknown command "%s"' % cmd_name]
        if guess:
            msg.append('maybe you meant "%s"' % guess)

        raise CommandError(' - '.join(msg))

    # all the args without the subcommand
    cmd_args = args[:]
    cmd_args.remove(cmd_name)

    return cmd_name, cmd_args