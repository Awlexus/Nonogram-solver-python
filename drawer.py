import curses
import math

class Drawer:
    __slots__ = 'stdscr', 'numbers_width', 'numbers_height', 'field_start_x', 'field_start_y', 'min_width', 'min_height', 'field_width', 'field_height', 'nonogram', 'scale', 'live', 'first_step'

    def __init__(self, nonogram, args):
        self.nonogram = nonogram
        self.scale = args.scale
        self.live = args.live
        self.first_step = args.first_step

        widest = max(nonogram.rows, key=len)

        self.numbers_width =  sum([math.floor(math.log10(x)) + 1 for x in widest]) + len(widest)
        self.numbers_height = max([len(col) for col in nonogram.cols])

        self.field_start_x = self.numbers_width + 4
        self.field_start_y = self.numbers_height

        self.field_width = nonogram.width * self.scale * 2
        self.field_height = nonogram.height * self.scale

        self.min_width  = self.field_start_x + self.field_width
        self.min_height = self.field_start_y + self.field_height

        self.stdscr = curses.initscr()
        (screen_height, screen_width) = self.stdscr.getmaxyx()

        if self.min_width > screen_width or self.min_height + 1 > screen_height:
            curses.endwin()
            print("Window is not large enough in order to render the nonogram.",
                  "In order to render the nonogram, follow the following steps",
                  " * Make your window larger",
                  " * Decrease the font-size",
                  " * Reduce the scale", sep="\r\n")
            exit(-1)

        curses.noecho()
        self.stdscr.keypad(True)
        self.stdscr.clear()

    def cleanup(self):
        self.stdscr.addstr(self.min_height + 1, 0, "Press any key to exit")
        self.stdscr.getch()

        curses.nocbreak()
        curses.echo()
        self.stdscr.keypad(False)

        curses.endwin()

    def debug(self, *args):
        self.stdscr.addstr(min_height + 1, 0, " ".join([str(x) for x in args]))
        self.stdscr.refresh()
        self.stdscr.getch()

    def draw_numbers(self):
        for (col_n, col) in enumerate(self.nonogram.cols):
            for (index, num) in enumerate(col):
                self.stdscr.addstr(self.numbers_height - len(col) + index, self.field_start_x + col_n * 2 * self.scale, str(num))

        for (row_n, row) in enumerate(self.nonogram.rows):
            text = " ".join([str(x) for x in row])
            self.stdscr.addstr(self.field_start_y + row_n * self.scale + 1, self.numbers_width - len(text), text)

        self.stdscr.hline(self.numbers_height,     self.numbers_width + 4, '-', self.field_width)
        self.stdscr.vline(self.numbers_height + 1, self.numbers_width + 2, '|', self.field_height)

        self.stdscr.refresh()

    def draw_field(self, do_draw=False):
        if self.live or do_draw :
            for y in range(self.nonogram.height):
                text = "".join(["xx" * self.scale if s == 1 else "  " * self.scale for s in [self.nonogram.field[y][x] for x in range(self.nonogram.width)]])
                for i in range(self.scale):
                    self.stdscr.addstr(self.field_start_y + y * self.scale + i + 1, self.field_start_x, text)
            self.stdscr.refresh()
