cells = []

SERVER = 'http://localhost:8080'

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
            console.log(data)
            if (data == 'x') {
                cells[i][j].put(Piece('black'))
            } else if (data == 'o') {
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
            this.put(Piece('black'))
            $.get(SERVER + '/play', {i: this.i, j: this. j}, function(data) {
                console.log(data)
                board_refresh()
                $.get(SERVER + '/respond', {param: 'null'}, function(data) {
                    console.log(data)
                    board_refresh()
                })
            })
        }.bind(cell) )

    return cell
}

function board() {
    var table = $('<table>')
    for (var i = 0; i < 8; i++) {
        row = $('<tr>')
        cell_row = []
        for (var j = 0; j < 8; j++) {
            cell = Cell(i, j)
            cell_row.push(cell)
            row.append(cell)
        }
        cells.push(cell_row)
        table.append(row)
    }
    table.css('boarder', '1px')
    return table
}

function Piece(color) {
    var piece = $('<div>')
    piece.css('width', '40px')
    piece.css('height', '40px')
    piece.css('background-color', color)
    piece.css('border-radius', '40px')
    return piece
}

function board_refresh() {
    for (var i = 0; i < 8; i++) {
        for (var j = 0; j < 8; j++) {
            cells[i][j].refresh()
        }
    }
}

window.onload = function() {
    $('body').append(board())
    board_refresh()
}
