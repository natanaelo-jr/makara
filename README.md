# Makara

Makara is an automated and distributed pipeline designed to collect and organize a comprehensive dataset of **Linux perf** statistics from multiple program executions across different machines.

---

## Overview

Makara automates the process of compiling, executing, and profiling programs using `perf`, aggregating the results into a structured dataset.  
It supports distributed execution, making it suitable for large-scale performance analysis or research in compiler optimization and program behavior characterization.

---

## Dependencies

Ensure the following dependencies are installed on all machines participating in data collection:

- **GCC** – for compiling C/C++ programs
- **Python 3.x** – for orchestration and automation
- **Linux perf** – for collecting performance metrics

---

## Installation

You can install the dependencies using your package manager. For Ubuntu/Debian-based systems:

```bash
sudo apt update
sudo apt install build-essential python3 linux-tools-common linux-tools-$(uname -r)
```

_(If `perf` is not found after installation, you may need to create a symbolic link to `/usr/bin/perf`.)_

You can test if perf is installed with

```bash
perf --version
```

---

## ▶️ How to Run

To start the data collection process, simply execute:

```bash
python3 collect_data.py
```

Makara will:

1. Compile all source programs;
2. Execute each one while recording performance statistics with `perf`;
3. Store the results in a structured `results/` directory;
4. Automatically compress the collected data into a `.zip` archive for easy sharing.

---
