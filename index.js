cells = []

SERVER = 'http://localhost:8080'

BLACK = 'x'
WHITE = 'o'

function Piece(color, size='40px') {
    var piece = $('<div>')
    piece.css('width', size)
    piece.css('height', size)
    piece.css('background-color', color)
    piece.css('border-radius', size)
    return piece
}

function CpuMove() {
    $.get(SERVER + '/respond', {param: 'null'}, function(data) {
        console.log(data)
        game.refresh()
        if (data == 'you pass') {
            CpuMove()
        }
    })
}

function Cell(i, j) {
    var cell = $('<td>')
    cell.attr('height', '50px')
    cell.attr('width', '50px')
    cell.attr('align', 'center')
    cell.attr('valign', 'center')
    cell.css('background-color', 'green')

    cell.i = i
    cell.j = j
    cell.is_empty = true

    cell.refresh = function() {
        $.get(SERVER + '/cell', {i: this.i, j: this.j}, function(data) {
            if (data == BLACK) {
                cells[i][j].put(Piece('black'))
            } else if (data == WHITE) {
                cells[i][j].put(Piece('white'))
            }
        })
    }.bind(cell)

    cell.put = function(piece) {
        this.empty()
        this.append(piece)
        this.is_empty = false
    }.bind(cell)

    cell.click(function() {
            $.get(SERVER + '/play', {i: this.i, j: this. j}, function(data) {
                console.log(data)
                if (data == '0') {
                    return
                }
                game.refresh()
                CpuMove()
            })
        }.bind(cell) )

    return cell
}

function Count(color) {
    var count = $('<td>')

    count.color = color

    count.refresh = function() {
        $.get(SERVER + '/count', {color: this.color}, function(data) {
            count.empty()
            count.append(data)
        })
    }.bind(count)

    return count
}

function ScoreBoard() {
    var board = $('<table>')

    black_row = $('<tr>')
    black_row.append($('<td>').append(Piece('black', '20px')))
    black_row.append($('<td>').append('='))
    black_score = Count(BLACK)
    black_row.append(black_score)
    board.append(black_row)

    white_row = $('<tr>')
    white_piece = Piece('white', '19px').css('border', 'solid').css('border-width', '1px')
    white_row.append($('<td>').append(white_piece))
    white_row.append($('<td>').append('='))
    white_score = Count(WHITE)
    white_row.append(white_score)
    board.append(white_row)

    board.black_score = black_score
    board.white_score = white_score

    board.refresh = function() {
        this.black_score.refresh()
        this.white_score.refresh()
    }.bind(board)

    return board
}

function Board() {
    var board = $('<table>')

    for (var i = 0; i < 8; i++) {
        var row = $('<tr>')
        var cell_row = []
        for (var j = 0; j < 8; j++) {
            var cell = Cell(i, j)
            cell_row.push(cell)
            row.append(cell)
        }
        cells.push(cell_row)
        board.append(row)
    }
    board.css('border', 'solid')
    board.css('border-width', '3px')

    board.cells = cells

    board.refresh = function() {
        for (var i = 0; i < 8; i++) {
            for (var j = 0; j < 8; j++) {
                this.cells[i][j].refresh()
            }
        }
    }.bind(board)

    return board
}

function Game() {
    var game = $('<table>')

    var board = Board()
    var score_board = ScoreBoard()

    game.append(board)
    game.append(score_board)

    game.board = board
    game.score_board = score_board

    game.refresh = function() {
        this.board.refresh()
        this.score_board.refresh()
    }.bind(game)
    
    return game
}

window.onload = function() {
    game = Game()
    $('body').append(game)
    game.refresh()
}
