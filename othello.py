#!/usr/bin/env python

from copy import deepcopy
from random import choice
from sys import stdout
from time import sleep
from time import time
from urlparse import urlparse

import BaseHTTPServer
import SimpleHTTPServer

RequestHandler = SimpleHTTPServer.SimpleHTTPRequestHandler

EMPTY = '.'
BLACK = 'x'
WHITE = 'o'

REVERSE = {BLACK: WHITE, WHITE: BLACK}
HIGHLIGHT = {BLACK: 'X', WHITE: 'O'}


class Board:
    def __init__(self):
        self.grid = [[EMPTY] * 8 for _ in xrange(8)]
        self.grid[3][3] = BLACK
        self.grid[3][4] = WHITE
        self.grid[4][4] = BLACK
        self.grid[4][3] = WHITE
        self.moves = []
        self.count = {BLACK: 2, WHITE: 2}

    def __str__(self):
        return '\n%s\n%s-%s' % (
                '\n'.join(' '.join(str(x) for x in row)
                          for row in self.grid),
                self.count[BLACK], self.count[WHITE])

    def valid(self, i, j):
        return 0 <= i < 8 and 0 <= j < 8

    def try_play(self, i, j, color):
        if not self.valid(i, j):
            return 0
        kills = list(self.kills(i, j, color))
        if kills:
            self.play(i, j, color, kills=kills)
        return len(kills)

    def play(self, i, j, color, kills=None):
        assert self.valid(i, j)
        assert self.grid[i][j] == EMPTY

        if kills is None:
            kills = list(self.kills(i, j, color))
        k = len(kills)
        assert k > 0

        self.moves.append((i, j, color, kills))

        self.grid[i][j] = color
        for i, j in kills:
            self.grid[i][j] = color

        self.count[color] += k + 1
        self.count[REVERSE[color]] -= k

        return k

    def unplay(self):
        i, j, color, kills = self.moves.pop()
        self.grid[i][j] = EMPTY
        reverse = REVERSE[color]
        for i, j in kills:
            self.grid[i][j] = reverse
        k = len(kills)
        self.count[color] -= k + 1
        self.count[REVERSE[color]] += k

    def kills(self, i, j, color):
        for i_inc in [-1, 0, 1]:
            for j_inc in [-1, 0, 1]:
                if i_inc == 0 and j_inc == 0:
                    continue
                for kill in self.kills_in(i, j, color, i_inc, j_inc):
                    yield kill

    def kills_in(self, i, j, color, i_inc, j_inc):
        i += i_inc
        j += j_inc
        reverse = REVERSE[color]
        kills = []
        while self.valid(i, j) and self.grid[i][j] == reverse:
            kills.append((i, j))
            i += i_inc
            j += j_inc
        if self.valid(i, j) and self.grid[i][j] == color:
            return kills
        else:
            return []

    def positions(self):
        for i in xrange(8):
            for j in xrange(8):
                yield i, j

    def empty(self):
        for i, j in self.positions():
            if self.grid[i][j] == EMPTY:
                yield i, j

    def valid_moves(self, color):
        for i, j in self.empty():
            kills = list(self.kills(i, j, color))
            if kills:
                yield i, j, kills

    def show_moves(self, color):
        board = deepcopy(self)
        for i, j, kills in self.valid_moves(color):
            board.grid[i][j] = 'B' if color == BLACK else 'W'
        return str(board)

    def show_last_move(self):
        board = deepcopy(self)
        i, j, color, kills = self.moves[-1]
        color = HIGHLIGHT[color]
        board.grid[i][j] = color
        for i, j in kills:
            board.grid[i][j] = color
        return str(board)

    def lead(self, color):
        return self.count[color] - self.count[REVERSE[color]]
    
    def load(self):
        return float(64 - len(list(self.empty()))) / 64

    def potential(self, color):
        l = self.load()
        return l*self.self.count[color] + (1 - l)*len(list(self.valid_moves(color)))*3


class Random:
    def move(self, board, color):
        try:
            move = choice(list(board.valid_moves(color)))
            return move
        except IndexError:
            return None


class Search:
    def __init__(self, depth, random=True, alphabeta=True):
        self.depth = depth
        self.random = random
        self.alphabeta = alphabeta

    def move(self, board, color):
        return self.move_score(board, color)[0]

    def move_score(self, board, color, alpha=-65, beta=65):
        if self.random:
            best_move = []
        else:
            best_move = None

        best_score = -65

        for i, j, kills in board.valid_moves(color):
            board.play(i, j, color, kills=kills)
            score = board.count[color]
            if self.depth > 1:
                opponent = Search(self.depth - 1, random=self.random,
                                  alphabeta=self.alphabeta)
                opponent_move, opponent_score = opponent.move_score(
                        board, REVERSE[color], -beta, -alpha)
                if opponent_move:
                    score = -opponent_score
                else:
                    me_again = Search(self.depth - 1, random=self.random,
                                      alphabeta=self.alphabeta)
                    next_move, next_score = me_again.move_score(
                            board, color, alpha, beta)
                    if next_move:
                        score = next_score

            if score > best_score:
                best_score = score
                if self.random:
                    best_move = [(i, j)]
                else:
                    best_move = (i, j)
                if best_score > alpha:
                    alpha = best_score
                if self.alphabeta and alpha >= beta:
                    board.unplay()
                    break
            elif self.random and score == best_score:
                best_move.append((i, j))

            board.unplay()

        if self.random:
            if best_move:
                return choice(best_move), best_score
            else:
                return None, best_score
        else:
            return best_move, best_score

class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = Board()
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
            start = time()
            move = player.move(self.board, color)
            player.time += time() - start

            if move:
                i, j = move
                kills = self.board.play(i, j, color)
                if show:
                    print self.board.show_last_move()
                passes = 0
            else:
                if show:
                    print "%s pass!" % color
                if passes == 0:
                    passes = 1
                else:
                    break
            player = self.switch(player)
            color = REVERSE[color]

        if show:
            if self.board.count[BLACK] > self.board.count[WHITE]:
                    print '%s won!' % self.player1.__class__.__name__
            elif self.board.count[BLACK] < self.board.count[WHITE]:
                    print '%s won!' % self.player2.__class__.__name__
            else:
                    print 'draw!'
            print 'time: %.2f, %.2f' % (self.player1.time, self.player2.time)

    def winner(self):
        if self.board.count[BLACK] == self.board.count[WHITE]:
            return EMPTY
        else:
            return max([BLACK, WHITE], key=lambda c: self.board.count[c])


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


def parse_query(path):
    query = urlparse(path).query
    return dict(pair.split('=') for pair in query.split('&'))


class Handler(RequestHandler):
    def do_GET(self):
        i = self.path.find('?')
        if i != -1:
            method = self.path[1:i]
            getattr(self, method)(parse_query(self.path))
        else:
            RequestHandler.do_GET(self)
    
    def send(self, s):
        s = str(s)
        self.wfile.write(b'HTTP/1.0 200 OK\r\nContent-Length: %s\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n%s\r\n' % (len(s), s))

    def cell(self, query):
        i = int(query['i'])
        j = int(query['j'])
        self.send(board.grid[i][j])

    def play(self, query):
        i = int(query['i'])
        j = int(query['j'])
        print 'x: (%s, %s)' % (i, j)
        kills = board.try_play(i, j, BLACK)
        if kills:
            print 'x += %s' % kills
        else:
            print 'invalid move'
        self.send(kills)

    def respond(self, query):
        move = Search(7, alphabeta=True).move(board, WHITE)
        if not move:
            print 'I pass'
            return
        i, j = move
        print 'o: (%s, %s)' % (i, j)
        kills = board.play(i, j, WHITE)
        print 'o += %s' % kills
        if list(board.valid_moves(BLACK)):
            self.send(kills)
        else:
            print 'you pass'
            sleep(4)
            self.send('you pass')

    def count(self, query):
        color = query['color']
        print color
        self.send(board.count[color])


def serve():
    server = BaseHTTPServer.HTTPServer(("", 8080), Handler)
    server.serve_forever()

if __name__ == '__main__':
    board = Board()
    serve()

    #g = Game(Search(2, random=False, alphabeta=False), Search(7, random=False, alphabeta=True))
    #g.run(show=True)

    #games = GameSet(Search(5), Search(5, alphabeta=True))
    #games.run(10, show=True)
    #print games.result()
