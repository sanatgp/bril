import subprocess
import csv
import statistics

def run_brench():
    result = subprocess.run(
        ["brench", "../examples/brench.py", "brench.toml"],
        capture_output=True,
        text=True
    )
    with open("results.csv", "w") as f:
        f.write(result.stdout)

def analyze_results():
    with open("results.csv", "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    improvements = []
    for row in data:
        baseline = int(row['baseline_result'])
        optimized = int(row['optimized_result'])
        improvement = (baseline - optimized) / baseline * 100
        improvements.append(improvement)

    print(f"Average improvement: {statistics.mean(improvements):.2f}%")
    print(f"Median improvement: {statistics.median(improvements):.2f}%")
    print(f"Max improvement: {max(improvements):.2f}%")
    print(f"Min improvement: {min(improvements):.2f}%")
    print(f"Number of benchmarks improved: {sum(1 for i in improvements if i > 0)}")
    print(f"Number of benchmarks unchanged: {sum(1 for i in improvements if i == 0)}")
    print(f"Number of benchmarks degraded: {sum(1 for i in improvements if i < 0)}")

if __name__ == "__main__":
    run_brench()
    analyze_results()
