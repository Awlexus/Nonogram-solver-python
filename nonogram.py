import re

def stroke_sum(stroke, offset=0):
    shifted = stroke[offset:]
    if len(shifted) > 0:
        return sum(shifted) + len(shifted) - offset - 1
    else:
        return 0

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

class Nonogram:
    __slots__ = 'width', 'height', 'total', 'cols', 'rows', 'field'

    def __init__(self, args):
        with open(args.file) as f:
            numbers = [int(x) for x in re.findall("\d+", f.read())]

        self.cols = []
        self.rows = []

        b = 2
        [self.width, self.height] = numbers[:b]
        self.field = [[0 for x in range(self.width)] for y in range(self.height)]
        self.total = self.width * self.height

        c = numbers[b:b+self.width]
        b += self.width
        r = numbers[b:b+self.height]
        b += self.height

        for i in c:
            x = []
            for j in range(i):
                x.append(numbers[b + j])
            b += i
            self.cols.append(x)

        for i in r:
            x = []
            for j in range(i):
                x.append(numbers[b + j])
            b += i
            self.rows.append(x)

    def apply_first_step_column(self, x):
        col = self.cols[x]
        _sum = stroke_sum(col)
        pos = diff = self.width - _sum

        for i in col:
            for j in range(i):
                if i - diff - j > 0:
                    self.field[pos][x] = 1
                pos += 1
            pos += 1

    def apply_first_step_row(self, y):
        row = self.rows[y]
        _sum = stroke_sum(row)
        pos = diff = self.height - _sum

        for i in row:
            for j in range(i):
                if i - diff - j > 0:
                    self.field[y][pos] = 1
                pos += 1
            pos += 1


    def apply_first_step(self):
        [self.apply_first_step_column(x) for x in range(self.width)]
        [self.apply_first_step_row(x) for x in range(self.height)]

    def validate_column(self, x, y):
        strokes = []
        i = 0;
        current = 0
        while i <= y:
            while i <= y and self.field[i][x] != 1: i+=1
            while i <= y and self.field[i][x] == 1: current += 1; i+=1
            if current != 0: strokes.append(current)
            current = 0

        if len(strokes) == 0:
            strokes.append(0)

        return validate_stroke(self.cols[x], strokes, y, self.height)

    def validate_row(self, x, y):
        strokes = []
        i = 0;
        current = 0
        while i <= x:
            while i <= x and self.field[y][i] != 1: i+=1
            while i <= x and self.field[y][i] == 1: current += 1; i+=1
            if current != 0: strokes.append(current)
            current = 0

        if len(strokes) == 0:
            strokes.append(0)

        return validate_stroke(self.rows[y], strokes, x, self.width)

    def valid(self, x, y):
        return self.validate_row(x, y) and self.validate_column(x, y)

    def validate_field(self):
        return all([self.validate_column(x, self.height-1) for x in range(self.width)]) and all([validate_row(self.width - 1, y) for y in range(self.height)])

