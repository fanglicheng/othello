#!/usr/bin/env python

from copy import deepcopy
from random import choice
from sys import stdout
from time import time

EMPTY = '.'
BLACK = 'x'
WHITE = 'o'

def Reverse(color):
    if color == BLACK:
        return WHITE
    if color == WHITE:
        return BLACK

def HighLight(color):
    if color == BLACK:
        return 'X'
    if color == WHITE:
        return 'O'


class Board:
    def __init__(self):
        self.grid = [[EMPTY] * 8 for _ in xrange(8)]

    def __str__(self):
        blacks, whites = self.count()
        return '\n%s\n%s-%s' % (
                '\n'.join(' '.join(str(x) for x in row)
                          for row in self.grid),
                blacks, whites)

    def valid(self, i, j):
        return 0 <= i < 8 and 0 <= j < 8

    def play(self, move, color, highlight=False):
        i, j = move
        self.grid[i][j] = HighLight(color) if highlight else color
        kills = 0
        for x_inc in [-1, 0, 1]:
            for y_inc in [-1, 0, 1]:
                if not (x_inc == 0 and y_inc == 0):
                    kills += self.play_direction(
                            i, j, color,
                            lambda x, y: (x + x_inc, y + y_inc),
                            highlight=highlight)
        return kills

    def play_direction(self, i, j, color, next, highlight=False):
        i, j = next(i, j)
        kills = []
        while self.valid(i, j):
            if self.grid[i][j] == Reverse(color):
                kills.append((i, j))
                i, j = next(i, j)
            else:
                break
        if self.valid(i, j) and self.grid[i][j] == color:
            for x, y in kills:
                self.grid[x][y] = HighLight(color) if highlight else color
            return len(kills)
        else:
            return 0

    def start(self):
        self.play((3, 3), BLACK)
        self.play((3, 4), WHITE)
        self.play((4, 4), BLACK)
        self.play((4, 3), WHITE)

    def positions(self):
        for i in xrange(8):
            for j in xrange(8):
                yield i, j

    def empty_positions(self):
        for i, j in self.positions():
            if self.grid[i][j] == EMPTY:
                yield i, j

    def legal_positions(self, color):
        for i, j in self.empty_positions():
            if deepcopy(self).play((i, j), color) > 0:
                yield i, j

    def show_legal_positions(self, color):
        board = deepcopy(self)
        for i, j in self.legal_positions(color):
            board.grid[i][j] = 'B' if color == BLACK else 'W'
        return str(board)

    def count(self):
        blacks = 0
        whites = 0
        for i, j in self.positions():
            if self.grid[i][j] == 'x':
                blacks += 1
            elif self.grid[i][j] == 'o':
                whites += 1
        return blacks, whites


class Random:
    def move(self, board, color):
        try:
            move = choice(list(board.legal_positions(color)))
            return move
        except IndexError:
            return None


class Greedy:
    def move(self, board, color):
        best_move = None
        best_kills = 0
        for i, j in board.empty_positions():
            kills = deepcopy(board).play((i, j), color)
            if kills > best_kills:
                best_kills = kills
                best_move = (i, j)
        return best_move


class RandomGreedy:
    def move(self, board, color):
        best_move = []
        best_kills = 0
        for i, j in board.empty_positions():
            kills = deepcopy(board).play((i, j), color)
            if kills > best_kills:
                best_kills = kills
                best_move = [(i, j)]
            elif kills == best_kills:
                best_move.append((i, j))
        if best_move:
            return choice(best_move)
        else:
            return None


class Search:
    def __init__(self, depth, random=True):
        self.depth = depth
        self.random = random

    def move(self, board, color):
        return self.move_kills(board, color)[0]

    def move_kills(self, board, color):
        if self.random:
            best_move = []
        else:
            best_move = None
        best_kills = -64
        for i, j in board.empty_positions():
            new_board = deepcopy(board)
            kills = new_board.play((i, j), color)
            if self.depth > 1:
                opponent = Search(self.depth - 1, random=self.random)
                opponent_move, opponent_kills = opponent.move_kills(
                        new_board, Reverse(color))
                if opponent_move:
                    kills -= opponent_kills
                else:
                    me_again = Search(self.depth - 1, random=self.random)
                    next_move, next_kills = me_again.move_kills(
                            new_board, Reverse(color))
                    if next_move:
                        kills += next_kills
            if kills > best_kills:
                best_kills = kills
                if self.random:
                    best_move = [(i, j)]
                else:
                    best_move = (i, j)
            elif self.random and kills == best_kills:
                best_move.append((i, j))
        if self.random:
            if best_move:
                return choice(best_move), best_kills
            else:
                return None, best_kills
        else:
            return best_move, best_kills


class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = Board()
        self.board.start()
        self.player1.time = 0.0
        self.player2.time = 0.0

    def switch(self, player):
        if player is self.player1:
            return self.player2
        elif player is self.player2:
            return self.player1
        else:
            assert False, "player to switch not in game"

    def run(self, show=False):
        player = self.player1
        color = BLACK
        passes = 0
        while True:
            if show:
                print self.board.show_legal_positions(color)

            start = time()
            move = player.move(self.board, color)
            player.time += time() - start

            if move:
                if show:
                    new_board = deepcopy(self.board)
                    new_board.play(move, color, highlight=True)
                    print new_board
                self.board.play(move, color)
                passes = 0
            else:
                if show:
                    print "%s pass!" % color
                if passes == 0:
                    passes = 1
                else:
                    break
            player = self.switch(player)
            color = Reverse(color)

        if show:
            counts = self.board.count()
            blacks, whites = counts
            if blacks > whites:
                    print '%s won!' % self.player1.__class__.__name__
            elif blacks < whites:
                    print '%s won!' % self.player2.__class__.__name__
            else:
                    print 'draw!'
            print 'time: %.2f, %.2f' % (self.player1.time, self.player2.time)

    def winner(self):
        counts = self.board.count()
        blacks, whites = counts
        if blacks > whites:
            return BLACK
        elif blacks < whites:
            return WHITE
        else:
            return EMPTY


class GameSet:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.player1_time = 0.0
        self.player2_time = 0.0
        self.black_wins = 0
        self.white_wins = 0
        self.draws = 0

    def run(self, n, show=False):
        for i in xrange(n):
            game = Game(self.player1, self.player2)
            game.run()
            winner = game.winner()
            if winner == BLACK:
                self.black_wins += 1
            elif winner == WHITE:
                self.white_wins += 1
            elif winner == EMPTY:
                self.draws += 1
            self.player1_time += self.player1.time
            self.player2_time += self.player2.time
            if show:
                stdout.write(winner)
                stdout.flush()
        if show:
            print

    def result(self):
        return '%s - %s - %s\n%.2f - %.2f' % (
                self.black_wins, self.draws, self.white_wins,
                self.player1_time, self.player2_time)

if __name__ == '__main__':
    g = Game(Search(2), Search(3))
    g.run(show=True)

    #games = GameSet(Search(2), RandomGreedy())
    #games.run(20, show=True)
    #print games.result()
