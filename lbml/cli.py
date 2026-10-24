import argparse
from pathlib import Path
from .simulator import run_comparison


def main():
    parser = argparse.ArgumentParser(description="ML load-balancing simulator")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--scenario", default="E3")
    demo.add_argument("--duration", type=int, default=180)
    demo.add_argument("--seed", type=int, default=101)
    args = parser.parse_args()
    if args.command == "demo":
        results, details = run_comparison(args.scenario, args.duration, args.seed)
        out = Path("results/demo")
        out.mkdir(parents=True, exist_ok=True)
        results.to_csv(out / "comparison.csv", index=False)
        for policy, frame in details.items():
            frame.to_csv(out / f"{policy}.csv", index=False)
        print(results[["policy", "requests", "avg_latency_s", "p95_latency_s", "throughput_rps", "overload_events", "imbalance_cv"]].to_string(index=False))


if __name__ == "__main__":
    main()
