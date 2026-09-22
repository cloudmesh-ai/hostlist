import argparse
import sys
from hostlist import Hostlist

def expand_cmd(args):
    try:
        hl = Hostlist.expand(args.spec)
        print(hl.compact(compress=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def compact_cmd(args):
    try:
        hl = Hostlist.expand(args.hosts)
        print(hl.compact())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for expanding and compacting Slurm-style hostlists."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # expand command
    expand_parser = subparsers.add_parser("expand", help="Expand a compressed hostlist string")
    expand_parser.add_argument("spec", help="The hostlist specification to expand")
    expand_parser.set_defaults(func=expand_cmd)

    # compact command
    compact_parser = subparsers.add_parser("compact", help="Compact a list of hostnames")
    compact_parser.add_argument("hosts", help="The comma-separated list of hostnames to compact")
    compact_parser.set_defaults(func=compact_cmd)

    args = parser.parse_args()
    args.func(args)

def expand_wrapper():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("spec", nargs="?")
    args = parser.parse_args()
    if not args.spec:
        print("Error: missing specification", file=sys.stderr)
        sys.exit(1)
    # Create a mock args object for expand_cmd
    class Args: pass
    a = Args(); a.spec = args.spec
    expand_cmd(a)

def compact_wrapper():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("hosts", nargs="?")
    args = parser.parse_args()
    if not args.hosts:
        print("Error: missing hostnames", file=sys.stderr)
        sys.exit(1)
    # Create a mock args object for compact_cmd
    class Args: pass
    a = Args(); a.hosts = args.hosts
    compact_cmd(a)

if __name__ == "__main__":
    main()
