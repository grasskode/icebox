import argparse
import sys
import textwrap
import traceback

from app import common
from app import commands
from app.elements.icebox import IceboxError


USAGE = 'icebox <command> [<args>]'
DESCRIPTION = textwrap.dedent('''\
These are the common icebox commands:

    config      Configure icebox.
                Configuration is global and stored in user home.
                usage: config
    init        Initialize a directory as an icebox.
                The path must be a folder.
                usage: init <path>
    clone       Clone an existing icebox to a local path.
                Does not download the frozen files by default. The path must
                not exist.
                usage: init <icebox> <path>
    freeze      Archive a given path.
                The path can be a file or folder. All files within a folder are
                recursively archived.
                usage: freeze <path>
    thaw        Unarchive a given path and restore original content.
                The path can be a file or folder. All files within a folder are
                recursively unarchived.
                usage: thaw <path>
    ls          List the contents of an icebox (local or remote).
                * Local paths must be inside an initialized icebox. Omitting
                  the path resolves to the current working directory.
                * Remote paths should exist. Omitting the path lists all
                  available iceboxes.
                Options:
                    -a / --remote : List remote iceboxes.
                usage: ls [options] [path]
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
    except IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def init(args):
    if len(args) != 1:
        print("Exactly one argument required - init <path>")
        return
    try:
        commands.IceboxInitCommand(path=args[0]).run()
    except IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def clone(args):
    if len(args) != 2:
        print("Exactly two argument required - clone <icebox> <path>")
        return
    try:
        commands.IceboxCloneCommand(icebox=args[0], path=args[1]).run()
    except IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def freeze(args):
    if len(args) != 1:
        print("Exactly one argument required - freeze <path>")
        return
    try:
        cmd = commands.IceboxFreezeCommand(path=args[0])
        cmd.run()
    except IceboxError as e:
        print(e)
    except KeyboardInterrupt as e:
        if cmd and cmd.icebox:
            common.utils.Finalize(cmd.icebox)
    except Exception:
        traceback.print_exc()


def thaw(args):
    if len(args) != 1:
        print("Exactly one argument required - thaw <path>")
        return
    try:
        cmd = commands.IceboxThawCommand(path=args[0])
        cmd.run()
    except IceboxError as e:
        print(e)
    except KeyboardInterrupt as e:
        if cmd and cmd.icebox:
            common.utils.Finalize(cmd.icebox)
    except Exception:
        traceback.print_exc()


def list(args):
    parser = argparse.ArgumentParser(
        description='Parse arguments for list command.')
    parser.add_argument(
        'path', type=str, nargs='?', default=None,
        help='path to list.')
    parser.add_argument(
        '-a', '--remote', dest='remote', action='store_true',
        help='list remote iceboxes.')
    parsed_args = parser.parse_args(args)
    try:
        commands.IceboxListCommand(
            path=parsed_args.path, remote=parsed_args.remote).run()
    except IceboxError as e:
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
