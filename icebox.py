import argparse
import os
import sys
import textwrap
import traceback

from app import common
from app import commands


# TODO: Need a dry run flag


USAGE = 'icebox <command> [<args>]'
DESCRIPTION = textwrap.dedent('''\
These are the common icebox commands:

    config      Configure icebox.
                Configuration is global and stored in user home.
                usage: config
    init        Initialize a directory as an icebox.
                The path must be a folder.
                usage: init <path>
    clone       Clone an icebox from an existing one.
                The path must not exist.
                usage: init <icebox> <path>
    freeze      Archive a given path.
                The path can be a file or folder. All files within a folder are
                recursively archived.
                usage: freeze <path>
    thaw        Unarchive a given path and restore original content.
                The path can be a file or folder. All files within a folder are
                recursively unarchived.
                usage: thaw <path>
    ls          List the contents of an icebox.
                The command can be run from an initialized icebox folder.
                Options:
                    -r : Lists files recursively.
                    -a : Lists all remote iceboxes.
                usage: ls [remote]
''')


def print_usage():
    print(USAGE)
    print(DESCRIPTION)


def config(args):
    if len(args) > 0:
        print("No arguments expected - config")
        return
    try:
        commands.IceboxConfigCommand().run()
    except common.IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def init(args):
    if len(args) != 1:
        print("Exactly one argument required - init <path>")
        return
    try:
        commands.IceboxInitCommand(path=args[0]).run()
    except common.IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def clone(args):
    if len(args) != 2:
        print("Exactly two argument required - clone <icebox> <path>")
        return
    try:
        commands.IceboxCloneCommand(icebox=args[0], path=args[1]).run()
    except common.IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def freeze(args):
    if len(args) != 1:
        print("Exactly one argument required - freeze <path>")
        return
    try:
        commands.IceboxFreezeCommand(path=args[0]).run()
    except common.IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def thaw(args):
    if len(args) != 1:
        print("Exactly one argument required - thaw <path>")
        return
    try:
        commands.IceboxThawCommand(path=args[0]).run()
    except common.IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def list(args):
    parser = argparse.ArgumentParser(
        description='Parse arguments for list command.')
    parser.add_argument('remote', type=str,
                        help='remote path to list.', default='.')
    parser.add_argument('-r', dest='recursive', action='store_true',
                        help='List files recursively.')
    parser.add_argument('-a', dest='all', action='store_true',
                        help='List all remote iceboxes.')
    parsed_args = parser.parse_args(args)
    try:
        if parsed_args.all:
            commands.IceboxListAllCommand().run()
        else:
            commands.IceboxListCommand(
                parent=os.getcwd(), remote=parsed_args.remote,
                recursive=parsed_args.recursive).run()
    except common.IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def main():
    command = None if len(sys.argv) == 1 else sys.argv[1]
    args = [] if len(sys.argv) < 3 else sys.argv[2:]
    if not command or command in ['help', '-h']:
        print_usage()
    elif command == 'config':
        config(args)
    elif command == 'init':
        init(args)
    elif command == 'clone':
        clone(args)
    elif command == 'freeze':
        freeze(args)
    elif command == 'thaw':
        thaw(args)
    elif command == 'ls':
        list(args)
    else:
        print(f'Unknown command "{command}".')
        print_usage()


if __name__ == '__main__':
    main()
