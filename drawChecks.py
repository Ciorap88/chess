import board
import pieces

# a function that checks if a player has available moves
# useful for determining if the game is won or drawn
def hasLegalMoves(color):
    # iterate through all the pieces on the board
    for row in board.board:
        for piece in row:

            # if there is no piece or the piece has a different color, skip it
            if piece is None or piece.notation[0] != color[0]:
                continue

            # check all the moves for legality, and return True if we find a legal move
            for move in piece.moves:
                if piece.isLegalMove(move[0]+piece.row, move[1]+piece.col) and piece.canMove(move[0]+piece.row, move[1]+piece.col):
                    return True
            for move in piece.attackMoves:
                if piece.isLegalMove(move[0]+piece.row, move[1]+piece.col) and piece.canMove(move[0]+piece.row, move[1]+piece.col):
                    return True


    # otherwise, there is no legal move and we return False
    return False


# a function that checks if there is enough material left on the board in order for checkamte to be possible
# if not, then the game ends in a draw
def enoughMaterial():
    bishops = []
    knights = []

    for row in board.board:
        for piece in row:
            if piece == None:
                continue
            if piece.notation[1] in ["r", "q", "p"]:
                return True
            elif piece.notation[1] == "b":
                bishops.append(piece)
            elif piece.notation[1] == "n":
                knights.append(piece)

    # kings alone or king vs king + 1 knight or bishop
    if len(bishops)+len(knights) < 2:
        return False

    # king + bishop vs king + bishop with same color bishops
    if (len(bishops) == 2 and len(knights) == 0 and bishops[0].notation[0] != bishops[1].notation[0] and 
    (bishops[0].row+bishops[0].col)%2 == (bishops[1].row+bishops[1].col)%2):
        return False

    return True