import argparse
import textwrap
import traceback
from common import IceboxError
from commands import IceboxConfigCommand
from commands import IceboxInitCommand
# from commands import IceboxSyncCommand
from commands import IceboxFreezeCommand
from commands import IceboxThawCommand

## TODO: Need a dry run command
## TODO: where are the test cases?

parser = argparse.ArgumentParser(
    prog='icebox',
    usage='%(prog)s <command> [<args>]',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
These are the common icebox commands:

    config      Configure icebox.
                Configuration is global and stored in user home.
                usage: config
    init        Initialize a directory as an icebox.
                The path must be a folder.
                usage: init <path>
    freeze      Archive a given path.
                The path can be a file or folder. All files within a folder are recursively archived.
                usage: freeze <path>
    thaw        Unarchive a given path and restore original content.
                The path can be a file or folder. All files within a folder are recursively unarchived.
                usage: thaw <path>
    ls          List the contents of a remote icebox.
                usage: ls <remote>
    sync        Sync a directory with a remote icebox.
                Local path should not be within an existing icebox.
                usage: sync <remote> <path>
    '''))
parser.add_argument('command')
parser.add_argument('args', nargs='*')

def config(args):
    if len(args) > 0:
        print("No arguments expected - config")
        return
    try:
        IceboxConfigCommand().run()
    except IceboxError as e:
        print(e)
    except:
        traceback.print_exc()

def init(args):
    if len(args) != 1:
        print("Exactly one argument required - init <path>")
        return
    try:
        IceboxInitCommand(path=args[0]).run()
    except IceboxError as e:
        print(e)
    except:
        traceback.print_exc()

def freeze(args):
    if len(args) != 1:
        print("Exactly one argument required - freeze <path>")
        return
    IceboxFreezeCommand(path=args[0]).run()

def thaw(args):
    if len(args) != 1:
        print("Exactly one argument required - thaw <path>")
        return
    IceboxThawCommand(path=args[0]).run()

def sync(args):
    if len(args) != 2:
        print("Exactly two arguments required - sync <remote> <path>")
        return
    # IceboxSync(remote=args[0], path=args[1]).run()

def main():
    args = parser.parse_args()
    if args.command == 'config':
        config(args.args)
    elif args.command == 'init':
        init(args.args)
    elif args.command == 'sync':
        sync(args.args)
    elif args.command == 'freeze':
        freeze(args.args)
    elif args.command == 'thaw':
        thaw(args.args)
    else:
        print(f'Unknown command "{args.command}".')
        parser.print_help()

if __name__ == '__main__':
    main()
