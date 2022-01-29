#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# This file is Copyright (c) 2020 David Shah <dave@ds0.me>, 2021 Jevin Sweval <jevinsweval@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import shlex
import sys

# LAZY: need to install or comment out uses
from rich import print
import pp

"""
This is a script to parse an Altera QSF file and produce a LiteX board Python file.

It has been tested on the Altera MAX 10 Dev kit rev C max10_top.qsf file from
https://www.intel.com/content/www/us/en/programmable/products/boards_and_kits/dev-kits/altera/max-10-fpga-development-kit.html

The "extras" section and name parsing rules will need modification to support other boards.
"""


def qsf_to_pins(qsf_path: str):
    pins = {}
    lines = open(qsf_path).readlines()
    for l in lines:
        # print(l)
        l = shlex.split(l, comments=True)
        if (
            len(l) == 4
            and l[0] == "set_location_assignment"
            and l[1].startswith("PIN_")
            and l[2] == "-to"
        ):
            pin_name = l[3]
            pin_name_orig = pin_name
            idx = None
            if pin_name[-1] == "]":
                pin_name, idx = pin_name.split("[")
                idx = int(idx[:-1])
            pin_pad = l[1].removeprefix("PIN_")
            if pin_name_orig in pins:
                pins[pin_name_orig]["name"] = pin_name
                pins[pin_name_orig]["pad"] = pin_pad
                pins[pin_name_orig]["name_orig"] = pin_name_orig
            else:
                pins[pin_name_orig] = {
                    "name": pin_name,
                    "name_orig": pin_name_orig,
                    "pad": pin_pad,
                }
            if idx is not None:
                pins[pin_name_orig]["idx"] = idx
        elif (
            len(l) == 6
            and l[0] == "set_instance_assignment"
            and l[1] == "-name"
            and l[2] == "IO_STANDARD"
            and l[4] == "-to"
        ):
            pin_name_orig = l[5]
            iostd = l[3]
            if pin_name_orig in pins:
                pins[pin_name_orig]["iostd"] = iostd
            else:
                pins[pin_name_orig] = {"iostd": iostd}
        elif (
            len(l) == 6
            and l[0] == "set_instance_assignment"
            and l[1] == "-name"
            and l[4] == "-to"
        ):
            pin_name_orig = l[5]
            misc_key = l[2]
            misc_val = l[3]
            if "misc" not in pins[pin_name_orig]:
                pins[pin_name_orig]["misc"] = {}
            pins[pin_name_orig]["misc"][misc_key] = misc_val
        else:
            if len(l) > 0:
                print(f'unhandled: {" ".join(l)}')
                pass

    # post process arrays and subsignals
    pin_arrays = {}
    for pin_name_orig, pin in pins.items():
        # print(f'{pin_name_orig}: {pin}')
        if "idx" in pin:
            if pin["name"] not in pin_arrays:
                pin_arrays[pin["name"]] = []
            pin_arrays[pin["name"]].append(pin)
    # print(f'pin_arrays: {pin_arrays}')
    # pp(pin_arrays)

    pin_groups = {}
    for group_name, pin_array in pin_arrays.items():
        pin_array.sort(key=lambda p: p["idx"])
        assert min([p["idx"] for p in pin_array]) == 0
        sz = max([p["idx"] for p in pin_array]) + 1
        assert sz == len(pin_array)
        iostd = None
        if "iostd" in pin_array[0]:
            iostd = pin_array[0]["iostd"]
            for p in pin_array:
                assert p["iostd"] == iostd
        misc = None
        if "misc" in pin_array[0]:
            misc = pin_array[0]["misc"]
            for p in pin_array:
                # if 'misc' not in p:
                # 	print(f'misc missing from p: {p}')
                # if 'misc' in p and p['misc'] != misc:
                # 	print(f'p: {p} misc: {misc}')
                assert p["misc"] == misc
        pin_groups[group_name] = {"pads": [p["pad"] for p in pin_array]}
        if iostd is not None:
            pin_groups[group_name]["iostd"] = iostd
        if misc is not None:
            pin_groups[group_name]["misc"] = misc
        for p in pin_array:
            del pins[p["name_orig"]]
        pins[group_name] = pin_groups[group_name]
    # pp(pin_groups)

    return pins


def pins_to_litex(pins):
    for pin_name, pin in sorted(pins.items(), key=lambda t: t[0]):
        iostd = pin["iostd"] if "iostd" in pin else None
        misc = pin["misc"] if "misc" in pin else None

        if "pads" not in pin:
            lpin = [f'"{pin_name}"', "0", f'Pins("{pin["pad"]}")']
            if iostd is not None:
                lpin.append(f'IOStandard("{iostd}")')
            if misc is not None:
                for mk, mv in misc.items():
                    lpin.append(f'Misc(["{mk}", "{mv}"])')
            print("(" + ", ".join(lpin) + "),")
        else:
            pads = pin["pads"]
            for i, pad in enumerate(pads):
                lpin = [f'"{pin_name}"', f"{i}", f'Pins("{pad}")']
                if iostd is not None:
                    lpin.append(f'IOStandard("{iostd}")')
                if misc is not None:
                    for mk, mv in misc.items():
                        lpin.append(f'Misc(["{mk}", "{mv}"])')
                print("(" + ", ".join(lpin) + "),")
    return


if __name__ == "__main__":
    pins = qsf_to_pins(sys.argv[1])
    # print(pins)
    pp(pins)
    print(len(pins))
    pins_to_litex(pins)
    sys.exit(0)
