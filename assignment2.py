#!/usr/bin/env python3

'''
OPS445 Assignment 2 - Winter 2023
Program: assignment2.py 
Author: Favour Jegede

The python code in this file is original work written by
Favour Jegede. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description:
This program is a memory visualizer. It reads system memory values
from /proc/meminfo and displays memory usage as a bar graph. When a
program name is provided, the script finds all related process IDs
and calculates the Resident Set Size (RSS) memory for each process
using /proc/<pid>/smaps. The script supports human-readable output
and adjustable graph length.

Date: August 2026
'''

import argparse
import os, sys

def parse_command_args() -> object:
    """
    Parse command-line arguments for the memory visualizer.
    Handles:
      -H / --human-readable
      -l LENGTH / --length LENGTH
      optional program name
    """
    parser = argparse.ArgumentParser(
        description="Memory Visualiser -- See Memory Usage Report with bar charts",
        epilog="Copyright 2023"
    )

    parser.add_argument(
        "-H", "--human-readable",
        action="store_true",
        help="Prints sizes in human readable format"
    )

    parser.add_argument(
        "-l", "--length",
        type=int,
        default=20,
        help="Specify the length of the graph. Default is 20."
    )

    parser.add_argument(
        "program",
        nargs="?",
        help="if a program is specified, show memory use of all associated processes. "
             "Show only total use if not."
    )

    return parser.parse_args()


def percent_to_graph(percent: float, length: int=20) -> str:
    """
    Convert a percent (0.0–1.0) into a bar graph string.
    """
    bars = int(percent * length)
    return "#" * bars + "." * (length - bars)


def get_sys_mem() -> int:
    """
    Return total system memory (MemTotal) in kB.
    """
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                return int(line.split()[1])


def get_avail_mem() -> int:
    """
    Return available system memory (MemAvailable) in kB.
    """
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])


def pids_of_prog(app_name: str) -> list:
    """
    Use pidof to find all PIDs for a given program.
    Returns a list of PID strings.
    """
    result = os.popen(f"pidof {app_name}").read().strip()

    if result == "":
        return []

    return result.split()


def rss_mem_of_pid(proc_id: str) -> int:
    """
    Open /proc/<pid>/smaps and sum all Rss: values.
    Returns total RSS memory in kB.
    """
    total_rss = 0

    try:
        with open(f"/proc/{proc_id}/smaps", "r") as f:
            for line in f:
                if line.startswith("Rss:"):
                    parts = line.split()
                    total_rss += int(parts[1])
    except FileNotFoundError:
        return 0

    return total_rss


def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result


if __name__ == "__main__":
    args = parse_command_args()
    if not args.program:  # no program name specified
        pass
    else:
        pass