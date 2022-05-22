#!/usr/bin/env python3

import sys

vcd_lines = open(sys.argv[1], "r").readlines()

NUM_SIGS = 7

sigs = [[] for i in range(NUM_SIGS)]

for i in range(len(vcd_lines) - NUM_SIGS):
    if vcd_lines[i][0] == "#" and vcd_lines[i + NUM_SIGS - 1].startswith("b1"):
        for j in range(NUM_SIGS):
            l = vcd_lines[i + 1 + j]
            sigs[j].append(int(l[1:2]))

trigger_idx = sigs[4].index(1)
print(trigger_idx)
print("".join(map(str, sigs[1])))
print("".join(map(str, sigs[1][trigger_idx:trigger_idx+96])))

