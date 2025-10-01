import os
import subprocess

perf_events = """
cpu-cycles
instructions
cache-references
cache-misses
duration_time
"""


def parse_perf_output(output_lines: list, expected_events: list) -> dict:
    parsed_values = {}
    for line in output_lines:
        parts = line.split(",")
        if len(parts) >= 3:
            # CORREÇÃO: Remove o sufixo (:u, :k, etc.) do nome do evento
            event_name_from_perf = parts[2].strip().split(":")[0]

            # O valor do contador é o primeiro campo, remove vírgulas de milhares
            counter_value = parts[0].strip().replace(",", "")

            # Confere se o evento está na lista dos que estamos esperando
            if event_name_from_perf in expected_events:
                parsed_values[event_name_from_perf] = counter_value
    return parsed_values


def runPerf(executable_path: str) -> dict:
    events_list = perf_events.strip().split("\n")
    perf_command = ["perf", "stat", "-x,"]
    perf_command += ["-e", ",".join(events_list), f"./{executable_path} 0"]
    result = subprocess.run(perf_command, capture_output=True, check=False, text=True)
    perf_output_lines = result.stderr.strip().split("\n")
    collected_data = parse_perf_output(perf_output_lines, events_list)
    return collected_data


def executeMultipleRuns(executable_path: str, runs: int = 100) -> list[dict]:
    # warmup run
    for _ in range(3):
        runPerf(executable_path)

    all_runs_data = []

    # definitive runs
    for _ in range(runs):
        run_data = runPerf(executable_path)
        all_runs_data.append(run_data)

    return all_runs_data


def saveToCSV(data: list[dict], csv_path: str, program_name: str):
    with open(csv_path, "w") as f:
        f.write("program," + "run," + ",".join(data[0].keys()) + "\n")
        i = 1
        for run in data:
            f.write(program_name + f",{i}," + ",".join(run.values()) + "\n")
            i += 1


def main():

    # Collect CPU data
    os.makedirs("results", exist_ok=True)
    os.makedirs("bin", exist_ok=True)
    subprocess.run(["cat", "/proc/cpuinfo"], stdout=open("results/cpuinfo.txt", "w"))

    sources = os.listdir("Jotai")
    programs = []
    errors = []

    # Clean non-compilable files
    for program in sources:
        output_name = program.replace(".c", ".out")
        print(f"Compiling {program}...")
        try:
            result = subprocess.run(
                ["gcc", "-o", f"bin/{output_name}", f"Jotai/{program}"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to compile {program}: {e}")
            print(f"Removing {program} from Jotai...")
            errors.append(program)
            os.remove(f"Jotai/{program}")
            continue
        finally:
            programs.append(output_name)
    print("Compilation finished.")
    print(f"Programs to be executed: {programs}")
    print(f"Errors: {errors}")
    with open("results/errors.txt", "w") as f:
        for error in errors:
            f.write(error + "\n")

    for program in programs:
        print(f"Running {program}...")
        all_data = executeMultipleRuns(f"bin/{program}", runs=100)
        saveToCSV(
            all_data,
            f"results/{program.replace(".out", "")}.csv",
            program.replace(".out", ""),
        )
        print(f"Finished {program}.")

    # Zip results folder
    subprocess.run(["zip", "-r", "results.zip", "results"], stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
