global board
global positionsDict
positionsDict = dict()

def isEmpty(row, col):
    global board
    if row > 7 or row < 0 or col > 7 or col < 0:
        return False
    return board[row][col] is None

def initBoard():
    global board
    board = [ [ None for i in range(8) ] for j in range(8) ]

def getPiece(row, col):
    global board
    return board[row][col]

def getString(turn):
    global board
    string = ""
    for r in board:
        empty = 0
        for piece in r:
            if piece is None:
                empty += 1
            else:
                if empty:
                    string += str(empty)
                    empty = 0
                if piece.notation[0] == "w":
                    string += piece.notation[1].upper()
                else:
                    string += piece.notation[1]
        if empty: 
            string += str(empty)
        string += "/"

    string += " " + turn + " "
    if not isEmpty(7, 4) and getPiece(7, 4).hasMoved == False:
        if not isEmpty(7, 0) and getPiece(7, 0).hasMoved == False:
            string += "K"
        if not isEmpty(7, 7) and getPiece(7, 7).hasMoved == False:
            string += "Q"
        
    if not isEmpty(0, 4) and getPiece(0, 4).hasMoved == False:
        if not isEmpty(0, 0) and getPiece(0, 0).hasMoved == False:
            string += "k"
        if not isEmpty(0, 7) and getPiece(0, 7).hasMoved == False:
            string += "q"

    if string[len(string)-1] == " ":
        string += "-"
    string += " "

    for row in board:
        for piece in row:
            if piece is None or piece.notation[1] != "p" or piece.notation[0] == turn:
                continue
            if piece.hasJustMovedTwo == True:
                row = 8-piece.row
                col = piece.col
                square = chr(ord("a")+col)
                if turn == "w":
                    square += str(row+1)
                else:
                    square += str(row-1)
                string += square

    if string[len(string)-1] == " ":
        string += "-"

    return string



