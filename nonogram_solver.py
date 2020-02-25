#!/usr/bin/env python

import argparse
import os.path

import nonogram
import drawer

parser = argparse.ArgumentParser(description="Solve a nonogram puzzle")
parser.add_argument("file", help="The file ontining the puzzle you want to solve", metavar="FILE")
parser.add_argument("-s", "--scale", help="Scale the image", metavar="SCALE", type=int, default=1)
parser.add_argument("-l", "--live", help="Display the processing live", action="store_const", const=True, default=False)
parser.add_argument("-f", "--first-step", help="Only calculate the first step", action="store_const", const=True, default=False)

def solve(index, drawer):
    nonogram = drawer.nonogram
    field = nonogram.field
    if index == nonogram.total:
        return True

    x, y = index % nonogram.width, index // nonogram.width
    current = field[y][x]

    if current != 0:
        return solve(index + 1, drawer)

    field[y][x] = 1
    drawer.draw_field()
    if nonogram.valid(x, y) and solve(index + 1, drawer):
        return True

    field[y][x] = current
    drawer.draw_field()
    if nonogram.valid(x,y) and solve(index + 1, drawer):
        return True

    return False

def validate_args(args):
    if args.scale < 1:
        print("The scale may not be smaller than 1")
        exit(-1)

    if not os.path.isfile(args.file):
        print("The file \"{}\" does not exist or is not a file", args.file)
        exit(-1)

if __name__ == '__main__':
    args = parser.parse_args()
    validate_args(args)

    nonogram = nonogram.Nonogram(args)
    drawer = drawer.Drawer(nonogram, args)

    nonogram.apply_first_step()

    drawer.draw_numbers()
    drawer.draw_field(True)

    if not args.first_step:
        solve(0, drawer)

    drawer.draw_field(True)
    drawer.cleanup()

