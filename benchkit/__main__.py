import argparse
from pathlib import Path

from .runner import ROOT, discover, run


def main():
    parser = argparse.ArgumentParser(description="ACL benchmark runner and static reports")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List discovered cases and implementations")
    benchmark = commands.add_parser("run", help="Measure new/changed cases using this interpreter")
    benchmark.add_argument("--results", type=Path, default=ROOT / "results")
    benchmark.add_argument("--case", action="append", help="Case directory name (repeatable)")
    benchmark.add_argument("--force", action="store_true", help="Re-measure unchanged cases")
    benchmark.add_argument("--quick", action="store_true", help="Smoke test: smallest size, two samples")
    build = commands.add_parser("build", help="Prepare pinned sources and native libraries without measuring")
    build.add_argument("--source", action="append", required=True, help="Source ID (repeatable)")
    build.add_argument("--print-path", action="store_true", help="Only print PYTHONPATH entries")
    reference = commands.add_parser("cpp-reference", help="Add standalone C++ reference timings to saved PyPy results")
    reference.add_argument("--results", type=Path, default=ROOT / "results")
    reference.add_argument("--case", action="append", help="Case directory name (repeatable)")
    reference.add_argument("--force", action="store_true", help="Re-measure unchanged references")
    report = commands.add_parser("report", help="Render saved results without running benchmarks")
    report.add_argument("--results", type=Path, default=ROOT / "results")
    report.add_argument("--output", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    if args.command == "list":
        for name, case in discover().items():
            print("%s: %s" % (name, ", ".join(a["id"] for a in case["adapters"])))
    elif args.command == "build":
        import os
        from .sources import prepare
        paths = prepare(ROOT, args.source)
        if args.print_path:
            print(os.pathsep.join(str(path) for path in paths.values()))
        else:
            for name, path in paths.items():
                print("%s: %s" % (name, path))
            print("Use these directories in PYTHONPATH when importing a native library directly.")
    elif args.command == "cpp-reference":
        from .cpp_reference import attach
        count = attach(args.results, args.case, args.force)
        print("Measured C++ references for %d case(s)." % count)
    elif args.command == "run":
        count = run(args.results, args.case, args.force, args.quick)
        print("Measured %d case(s)." % count)
    else:
        from .report import render
        render(args.results, args.output)
        print("Report: " + str(args.output / "index.html"))


if __name__ == "__main__":
    main()
