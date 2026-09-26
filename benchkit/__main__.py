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
    report = commands.add_parser("report", help="Render saved results without running benchmarks")
    report.add_argument("--results", type=Path, default=ROOT / "results")
    report.add_argument("--output", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    if args.command == "list":
        for name, case in discover().items():
            print("%s: %s" % (name, ", ".join(a["id"] for a in case["adapters"])))
    elif args.command == "run":
        count = run(args.results, args.case, args.force, args.quick)
        print("Measured %d case(s)." % count)
    else:
        from .report import render
        render(args.results, args.output)
        print("Report: " + str(args.output / "index.html"))


if __name__ == "__main__":
    main()
