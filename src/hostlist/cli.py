import argparse
import sys
from hostlist import Hostlist

def expand_cmd(args):
    try:
        spec = args.spec
        if not spec and not sys.stdin.isatty():
            spec = sys.stdin.read().strip()
        
        if not spec:
            print("Error: missing specification", file=sys.stderr)
            sys.exit(1)
            
        hl = Hostlist.expand(spec)
        
        if args.format:
            for item in hl.format(args.format):
                print(item)
        elif args.quiet:
            print(hl.quiet())
        else:
            print(hl.compact(compress=False))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def compact_cmd(args):
    try:
        hosts = args.hosts
        if not hosts and not sys.stdin.isatty():
            hosts = sys.stdin.read().strip()
            
        if not hosts:
            print("Error: missing hostnames", file=sys.stderr)
            sys.exit(1)
            
        hl = Hostlist.expand(hosts)
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
    expand_parser.add_argument("spec", nargs="?", help="The hostlist specification to expand (or read from stdin)")
    expand_parser.add_argument("--format", help="Format the output using a template (e.g. 'ssh {host} uptime')")
    expand_parser.add_argument("--quiet", action="store_true", help="Output as a simple comma-separated list")
    expand_parser.set_defaults(func=expand_cmd)

    # compact command
    compact_parser = subparsers.add_parser("compact", help="Compact a list of hostnames")
    compact_parser.add_argument("hosts", nargs="?", help="The comma-separated list of hostnames to compact (or read from stdin)")
    compact_parser.set_defaults(func=compact_cmd)

    args = parser.parse_args()
    args.func(args)

def expand_wrapper():
    # This is used for the entry point hostlist-expand
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("spec", nargs="?")
    parser.add_argument("--format")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    
    class Args: pass
    a = Args()
    a.spec = args.spec
    a.format = args.format
    a.quiet = args.quiet
    expand_cmd(a)

def compact_wrapper():
    # This is used for the entry point hostlist-compact
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("hosts", nargs="?")
    args = parser.parse_args()
    
    class Args: pass
    a = Args()
    a.hosts = args.hosts
    compact_cmd(a)

if __name__ == "__main__":
    main()

