#!/usr/bin/env python
from copy import deepcopy

EMPTY = '.'
BLACK = 'x'
WHITE = 'o'

def opponent(color):
    if color == BLACK:
        return WHITE
    if color == WHITE:
        return BLACK

class Board:
    def __init__(self):
        self.grid = [[EMPTY] * 8 for _ in xrange(8)]

    def __str__(self):
        return '\n' + '\n'.join(' '.join(str(x) for x in row) for row in self.grid) + '\n'

    def valid(self, i, j):
        return 0 <= i < 8 and 0 <= j < 8

    def play(self, i, j, color):
        self.grid[i][j] = color
        kills = 0
        for x_inc in [-1, 0, 1]:
            for y_inc in [-1, 0, 1]:
                if not (x_inc == 0 and y_inc == 0):
                    kills += self.play_direction(
                            i, j, color,
                            lambda x, y: (x + x_inc, y + y_inc))
        return kills

    def play_direction(self, i, j, color, next):
        i, j = next(i, j)
        kills = []
        while self.valid(i, j):
            if self.grid[i][j] == opponent(color):
                kills.append((i, j))
                i, j = next(i, j)
            else:
                break
        if self.valid(i, j) and self.grid[i][j] == color:
            for x, y in kills:
                self.grid[x][y] = color
            return len(kills)
        else:
            return 0

    def start(self):
        self.play(3, 3, BLACK)
        self.play(3, 4, WHITE)
        self.play(4, 4, BLACK)
        self.play(4, 3, WHITE)

def greedy(board, color):
    best_move = None
    best_kills = 0
    for i in xrange(8):
        for j in xrange(8):
            if board.grid[i][j] == EMPTY:
                kills = deepcopy(board).play(i, j, color)
                if kills > best_kills:
                    best_kills = kills
                    best_move = (i, j)
    return best_move

if __name__ == '__main__':
    b = Board()
    b.start()
    print b
    color = BLACK
    for _ in xrange(64):
        i, j = greedy(b, color)
        b.play(i, j, color)
        print b
        color = opponent(color)
