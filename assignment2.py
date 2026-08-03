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
    bars = int(percent * length)
    spaces = length - bars
    return "#" * bars + " " * spaces


def get_sys_mem() -> int:
    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                return int(line.split()[1])


def get_avail_mem() -> int:
    with open("/proc/meminfo", "r") as f:
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
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suf_index = 0
    value = float(kibibytes)

    while value >= 1024 and suf_index < len(suffixes) - 1:
        value /= 1024
        suf_index += 1

    return f"{value:.{decimal_places}f} {suffixes[suf_index]}"


if __name__ == "__main__":
    args = parse_command_args()

    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    used_mem = total_mem - avail_mem

    percent_used = used_mem / total_mem
    graph = percent_to_graph(percent_used, args.length)

    if args.human_readable:
        total_str = bytes_to_human_r(total_mem, 1)
        used_str = bytes_to_human_r(used_mem, 1)
    else:
        total_str = f"{total_mem} KiB"
        used_str = f"{used_mem} KiB"

    if not args.program:
        print(f"Total: {total_str}")
        print(f"Used:  {used_str}")
        print(f"[{graph}]")
        sys.exit(0)

    pids = sorted(pids_of_prog(args.program), key=int)

    if len(pids) == 0:
        print(f"No running processes found for {args.program}")
        sys.exit(0)

    for pid in pids:
        rss = rss_mem_of_pid(pid)

        if args.human_readable:
            rss_str = bytes_to_human_r(rss, 1)
        else:
            rss_str = f"{rss} KiB"

        percent = rss / total_mem
        bar = percent_to_graph(percent, args.length)

        print(f"PID {pid}: {rss_str} [{bar}]")

