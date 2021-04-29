import sys
import textwrap
import traceback

from app import common
from app import commands


# TODO: Need a dry run flag
# TODO: where are the test cases?


USAGE = 'icebox <command> [<args>]'
DESCRIPTION = textwrap.dedent('''\
These are the common icebox commands:

    config      Configure icebox.
                Configuration is global and stored in user home.
                usage: config
    init        Initialize a directory as an icebox.
                The path must be a folder.
                usage: init <path>
    freeze      Archive a given path.
                The path can be a file or folder. All files within a folder are
                recursively archived.
                usage: freeze <path>
    thaw        Unarchive a given path and restore original content.
                The path can be a file or folder. All files within a folder are
                recursively unarchived.
                usage: thaw <path>
    ls          List the contents of an icebox.
                A remote icebox can be provided else the icebox in the current
                directory would be used.
                usage: ls [remote]
    sync        Sync a directory with a remote icebox.
                Local path should not be within an existing icebox.
                usage: sync <remote> <path>
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
    try:
        commands.IceboxListCommand(args=args).run()
    except common.IceboxError as e:
        print(e)
    except Exception:
        traceback.print_exc()


def sync(args):
    try:
        commands.IceboxSyncCommand(args=args).run()
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
    elif command == 'freeze':
        freeze(args)
    elif command == 'thaw':
        thaw(args)
    elif command == 'ls':
        list(args)
    elif command == 'sync':
        sync(args)
    else:
        print(f'Unknown command "{command}".')
        print_usage()


if __name__ == '__main__':
    main()
