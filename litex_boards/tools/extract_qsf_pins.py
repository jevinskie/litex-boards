#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# This file is Copyright (c) 2020 David Shah <dave@ds0.me>, 2021 Jevin Sweval <jevinsweval@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import re
import shlex
import sys


from rich import print
import pretty_errors

"""
This is a script to parse an Altera QSF file and produce a LiteX board Python file.

It has been tested on the Altera MAX 10 Dev kit rev C max10_top.qsf file from
https://www.intel.com/content/www/us/en/programmable/products/boards_and_kits/dev-kits/altera/max-10-fpga-development-kit.html

The "extras" section and name parsing rules will need modification to support other boards.
"""

def qsf_to_litex(qsf_path: str):
	pins = {}
	lines = open(qsf_path).readlines()
	for l in lines:
		# print(l)
		l = shlex.split(l, comments=True)
		if len(l) == 4 and l[0] == 'set_location_assignment' and l[1].startswith('PIN_') and l[2] == '-to':
			pin_name = l[3]
			pin_name_orig = pin_name
			idx = None
			if pin_name[-1] == ']':
				pin_name, idx = pin_name.split('[')
				idx = int(idx[:-1])
			pin_pad = l[1].removeprefix('PIN_')
			pins[pin_name_orig] = {'name': pin_name, 'pad': pin_pad}
			if idx is not None:
				pins[pin_name_orig]['idx'] = idx
		elif len(l) == 6 and l[0] == 'set_instance_assignment' and l[1] == '-name' and l[2] == 'IO_STANDARD' and l[4] == '-to':
			pin_name_orig = l[5]
			iostd = l[3]
			pins[pin_name_orig]['iostd'] = iostd
		elif len(l) == 6 and l[0] == 'set_instance_assignment' and l[1] == '-name' and l[4] == '-to':
			pin_name_orig = l[5]
			misc_key = l[2]
			misc_val = l[3]
			if 'misc' not in pins[pin_name_orig]:
				pins[pin_name_orig]['misc'] = {}
			pins[pin_name_orig]['misc'][misc_key] = misc_val
		else:
			if len(l) > 0:
				print(l)
	return pins


if __name__ == '__main__':
	pins = qsf_to_litex(sys.argv[1])
	print(pins)
	sys.exit(0)
