#!/usr/bin/env python

import argparse
import re
import curses
import os.path
import math

# For calculating the solution
width = height = total = 0
cols, rows = [], []
field = None

# For drawing 
stdscr = None
numbers_width = numbers_height = field_start_x = field_start_y = min_width = min_height = field_width = field_height = 0

parser = argparse.ArgumentParser(description="Solve a nonogram puzzle")
parser.add_argument("file", help="The file ontining the puzzle you want to solve", metavar="FILE")
parser.add_argument("-s", "--scale", help="Scale the image", metavar="SCALE", type=int, default=1)
parser.add_argument("-l", "--live", help="Display the processing live", action="store_const", const=True, default=False)
parser.add_argument("-f", "--first-step", help="Only calculate the first step", action="store_const", const=True, default=False)

def stroke_sum(stroke, offset=0):
    shifted = stroke[offset:]
    if len(shifted) > 0:
        return sum(shifted) + len(shifted) - offset - 1
    else:
        return 0

def parse_file(file):
    global width, height, total, field
    with open(file) as f:
        numbers = [int(x) for x in re.findall("\d+", f.read())]

    b = 2
    [width, height] = numbers[:b]
    field = [[0 for x in range(width)] for y in range(height)]
    total = width * height

    c = numbers[b:b+width]
    b += width
    r = numbers[b:b+height]
    b += height

    for i in c:
        x = []
        for j in range(i):
            x.append(numbers[b + j])
        b += i
        cols.append(x)

    for i in r:
        x = []
        for j in range(i):
            x.append(numbers[b + j])
        b += i
        rows.append(x)

def apply_first_step_column(x):
    col = cols[x]
    _sum = stroke_sum(col)
    pos = diff = width - _sum

    for i in col:
        for j in range(i):
            if i - diff - j > 0:
                field[pos][x] = 1
            pos += 1
        pos += 1

def apply_first_step_row(y):
    row = rows[y]
    _sum = stroke_sum(row)
    pos = diff = height - _sum

    for i in row:
        for j in range(i):
            if i - diff - j > 0:
                field[y][pos] = 1
            pos += 1
        pos += 1


def apply_first_step():
    [apply_first_step_column(x) for x in range(width)]
    [apply_first_step_row(x) for x in range(height)]

def write(arg):
    print(arg, end='')

def validate_stroke(stroke, current, offset, _max):
    if stroke_sum(stroke, len(current)) + offset > _max:
        return False

    if len(current) == 0:
        return False

    if stroke_sum(current) > _max:
        return False

    if offset == _max - 1:
        return stroke == current

    until_offset = stroke[:len(current)]

    if current[:-1] != until_offset[:-1] or current[-1] > until_offset[-1]:
        return False

    return True

def validate_column(x, y):
    strokes = []
    i = 0;
    current = 0
    while i <= y:
        while i <= y and field[i][x] != 1: i+=1
        while i <= y and field[i][x] == 1: current += 1; i+=1
        if current != 0: strokes.append(current)
        current = 0

    if len(strokes) == 0:
        strokes.append(0)

    return validate_stroke(cols[x], strokes, y, height)

def validate_row(x, y):
    strokes = []
    i = 0;
    current = 0
    while i <= x:
        while i <= x and field[y][i] != 1: i+=1
        while i <= x and field[y][i] == 1: current += 1; i+=1
        if current != 0: strokes.append(current)
        current = 0

    if len(strokes) == 0:
        strokes.append(0)

    return validate_stroke(rows[y], strokes, x, width)

def valid(x, y):
    return validate_row(x, y) and validate_column(x, y)

def validate_field():
    return all([validate_column(x, height-1) for x in range(width)]) and all([validate_row(width - 1, y) for y in range(height)])

def calculate_bounds(scale):
    global numbers_width, numbers_height, field_start_x, field_start_y, min_width, min_height, field_height, field_width

    widest = max(rows, key=len)

    numbers_width =  sum([math.floor(math.log10(x)) + 1 for x in widest]) + len(widest)
    numbers_height = max([len(col) for col in cols])

    field_start_x = numbers_width + 4
    field_start_y = numbers_height

    field_width = width * scale * 2
    field_height = height * scale

    min_width  = field_start_x + field_width
    min_height = field_start_y + field_height

def prepare_curses(args):
    global stdscr

    stdscr = curses.initscr()
    (screen_height, screen_width) = stdscr.getmaxyx()
    if min_width > screen_width or min_height + 1 > screen_height:
        curses.endwin()
        print("Window is not large enough in order to render the nonogram.",
              "In order to render the nonogram, follow the following steps",
              " * Make your window larger",
              " * Decrease the font-size",
              " * Reduce the scale", sep="\r\n")
        exit(-1)

    curses.noecho()
    stdscr.keypad(True)
    stdscr.clear()

def cleanup_curses(args):
    global stdscr

    stdscr.addstr(min_height + 1, 0, "Press any key to exit")
    stdscr.getch()

    curses.nocbreak()
    curses.echo()
    stdscr.keypad(False)

    curses.endwin()

def debug(*args):
    stdscr.addstr(min_height + 1, 0, " ".join([str(x) for x in args]))
    stdscr.refresh()
    stdscr.getch()

def draw_numbers(args):
    for (col_n, col) in enumerate(cols):
        for (index, num) in enumerate(col):
            stdscr.addstr(numbers_height - len(col) + index, field_start_x + col_n * 2 * args.scale, str(num))

    for (row_n, row) in enumerate(rows):
        text = " ".join([str(x) for x in row])
        stdscr.addstr(field_start_y + row_n * args.scale + 1, numbers_width - len(text), text)

    stdscr.hline(numbers_height, numbers_width + 4, '-', field_width)
    stdscr.vline(numbers_height + 1, numbers_width + 2, '|', field_height)

    stdscr.refresh()

def draw_field(args, do_draw=False):
    if args.live or do_draw :
        for y in range(height):
            text = "".join(["xx" * args.scale if s == 1 else "  " * args.scale for s in [field[y][x] for x in range(width)]])
            for i in range(args.scale):
                stdscr.addstr(field_start_y + y * args.scale + i + 1, field_start_x, text)
        stdscr.refresh()

def solve(index, args):
    if index == total:
        return True

    x, y = index % width, index // width
    current = field[y][x]

    if current != 0:
        return solve(index + 1, args)

    field[y][x] = 1
    draw_field(args)
    if valid(x, y) and solve(index + 1, args):
        return True

    field[y][x] = current
    draw_field(args)
    if valid(x,y) and solve(index + 1, args):
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
    parse_file(args.file)

    calculate_bounds(args.scale)
    prepare_curses(args)

    apply_first_step()
    draw_numbers(args)
    draw_field(args, True)

    if not args.first_step:
        solve(0, args)

    draw_field(args, True)
    cleanup_curses(args)

