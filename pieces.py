import pygame
import board
pygame.init()

global whiteKing
global blackKing
global currentPiece
global fiftyMove

# this function initializes the board and the starting pieces on their starting squares
def initGame():
    board.initBoard()

    global whiteKing
    global blackKing
    global currentPiece

    # the current piece is the piece that is being dragged by the player with the mouse
    currentPiece = None

    for i in range(0, 8):
        Pawn(6, i, "w")
        Pawn(1, i, "b")
    for i in [0, 7]:
        Rook(7, i, "w")
        Rook(0, i, "b")
    for i in [1, 6]:
        Knight(7, i, "w")
        Knight(0, i, "b")
    for i in [2, 5]:
        Bishop(7, i, "w")
        Bishop(0, i, "b")
    
    Queen(7, 3, "w")
    Queen(0, 3, "b")
    whiteKing = King(7, 4, "w")
    blackKing = King(0, 4, "b")

# a piece class that has the methods and attributes that all pieces should have
class Piece:
    def __init__(self, row, col, notation):
        self.notation = notation
        self.row = row
        self.col = col
        self.img = pygame.image.load("imgs/"+self.notation+".png")
        board.board[row][col] = self
        self.imgRect = self.img.get_rect()
        self.hasMoved = False

    # this displays the piece on the screen
    def draw(self, screen, width, height):
        screen.blit(self.img, self.imgRect)
        self.imgRect.center = (height/8 * self.col + height/16, width/8*self.row + width/16)

    # a method that checks if a move is legal (it doesn't put the respective king in check)
    def isLegalMove(self, newRow, newCol):

        # if the move is out of bounds, it is not legal
        if newRow < 0 or newRow > 7 or newCol < 0 or newCol > 7:
            return False
    
        currentRow = self.row
        currentCol = self.col
        piece = board.getPiece(newRow, newCol)

        board.board[newRow][newCol] = self
        board.board[self.row][self.col] = None
        self.row = newRow
        self.col = newCol

        answer = True
        if (self.notation[0] == "w" and whiteKing.isInCheck(whiteKing.row, whiteKing.col) or
        self.notation[0] == "b" and blackKing.isInCheck(blackKing.row, blackKing.col)):
            answer = False

        board.board[currentRow][currentCol] = self
        board.board[self.row][self.col] = piece
        self.row = currentRow
        self.col = currentCol

        return answer

    # updates the board and positions after a capture / move
    def updateBoard(self, newRow, newCol):
        global fiftyMove
        self.hasMoved = True

        # increment the fifty-move rule counter or reset it if a pawn moves or a piece is captured
        if board.getPiece(newRow, newCol) is not None or self.notation[1] == "p":
            fiftyMove = 0
            board.positionsDict.clear()
        else:
            fiftyMove += 1
            

        board.board[newRow][newCol] = self
        board.board[self.row][self.col] = None
        self.row = newRow
        self.col = newCol

        return True
        
    # a method that tries to move the piece to a certain square
    # the piece can move if the move is legal (doesn't put their king in check) and it is in their move set
    def move(self, row, col):

        # special cases for the en passant and castling moves
        if self.notation[1] == "p" and self.canTakeEnPassant(row, col):
            self.enPassant(row, col)
            return True
        if self.notation[1] =="k" and self.canCastle(row, col):
            self.castle(row, col)
            return True

        if self.canMove(row, col) and self.isLegalMove(row, col):
            self.updateBoard(row, col)
            return True
        
        return False

# the pawn class that is a child of the piece class and has unique movement
class Pawn(Piece):
    def __init__(self, row, col, color):
        self.hasJustMovedTwo = False

        # the notation is useful when trying to display the board 
        notation = color[0]+"p"
        
        
        # moves is a set of tuples that describe the squares where the pawn can move
        # attackMoves describes the squares which can be captured by the pawn 
        self.moves = set()
        self.attackMoves = set()

        # the pawn can attack 1 square up (if it is white) or down (if it is black) diagonally
        # and can move 1 square up / down on the same column
        # or 2 squares up / down on the first move
        if color[0] == "w":
            self.moves = {(-1, 0), (-2, 0)}
            self.attackMoves = {(-1, -1), (-1, 1)}
        else:
            self.moves = {(1, 0), (2, 0)}
            self.attackMoves = {(1, 1), (1, -1)}

        super().__init__(row, col, notation)


    # a method that checks if the piece can move to another square and moves it / captures the piece that is there
    def canMove(self, newRow, newCol):

        # if the piece can't attack nor move there, it is not valid
        if ((newRow-self.row, newCol-self.col) not in self.moves) and ((newRow-self.row, newCol-self.col) not in self.attackMoves):
            return False

        # if that square is not empty
        if not board.isEmpty(newRow, newCol):

            # the pawn can capture the piece on that square if the square is in the attackMoves set
            # and the piece is not of the same color
            if board.getPiece(newRow, newCol).notation[0] != self.notation[0]:
                if (newRow-self.row, newCol-self.col) in self.attackMoves:
                    return True
            
            # otherwise, the piece is of the same color as this pawn or the pawn is just not allowed to go there
            return False

        # if it is in the moves set
        if (newRow-self.row, newCol-self.col) in self.moves:

            # after the first move, the 2-square move is not valid anymore
            if self.notation[0] == "w" and self.col == 6:
                self.moves = {(-1, 0)}
            elif self.notation[0] == "b" and self.col == 1:
                self.moves = {(1, 0)}

            # if the pawn wants to move 2 squares, there have to be no pieces between those squares
            if abs(self.row-newRow)== 2:
                if (self.notation[0] == "w" and not board.isEmpty(self.row-1, self.col) or
                self.notation[0] == "b" and not board.isEmpty(self.row+1, self.col)):
                    return False    
                else:
                    self.hasJustMovedTwo = True


            return True
        
        return False

    # en passant is a special move where the pawn captures another pawn that has just moved 2 squares and is on the same row as it
    def canTakeEnPassant(self, row, col):
        if not board.isEmpty(row, col):
            return False

        # check the position of the pawn and the next position
        if self.notation[0] == "w":
            if row != self.row-1 or abs(col-self.col) != 1:
                return False
            if board.isEmpty(self.row, col) or board.getPiece(self.row, col).notation != "bp" or not board.getPiece(self.row, col).hasJustMovedTwo:
                return False
        else:
            if row != self.row+1 or abs(col-self.col) != 1:
                return False
            if board.isEmpty(self.row, col) or board.getPiece(self.row, col).notation != "wp" or not board.getPiece(self.row, col).hasJustMovedTwo:
                return False

        otherPawn = board.getPiece(self.row, col)
        currentRow = self.row
        currentCol = self.col

        board.board[self.row][col] = None
        board.board[row][col] = self
        self.row = row
        self.col = col
        valid = True

        # if the move puts the pawn's king in check, it's not valid
        if (self.notation[0] == "w" and whiteKing.isInCheck(whiteKing.row, whiteKing.col) or 
        self.notation[0] == "b" and blackKing.isInCheck(blackKing.row, blackKing.col)):
            valid = False

        self.row = currentRow
        self.col = currentCol
        board.board[self.row][self.col] = self
        board.board[row][col] = None
        board.board[self.row][col] = otherPawn

        return valid

    # the pawn that captures goes 1 square forward and on the column of the captured pawn
    def enPassant(self, row, col):
        board.board[self.row][col] = None
        self.updateBoard(row, col)

     
    # checks if the piece is attacking a square
    def isAttacking(self, row, col):
        return (row-self.row, col-self.col) in self.attackMoves

#the knight class also has unique movement
class Knight(Piece):
    def __init__(self, row, col, color):
        notation = color[0]+"n"

        # the knight can move/attack in an L shape, which means it can move 2 squares in 1 dimension and 1 in the other 
        self.moves = {(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)}
        self.attackMoves = self.moves

        super().__init__(row, col, notation)

    def canMove(self, newRow, newCol):

        # if it doesn't move in an L shape, the move isn't valid
        if(newRow-self.row, newCol-self.col) not in self.moves:
            return False

        #if there is a piece on that square, it can capture it if it's of a different color, or otherwise it can't move there
        if not board.isEmpty(newRow, newCol):
            if board.getPiece(newRow, newCol).notation[0] != self.notation[0]:
                return True
            else:
                return False

        return True

    def isAttacking(self, row, col):
        return (row-self.row, col-self.col) in self.moves

# a parent class for the rook, bishop and queen, as they are similar in how they move
#the only differences between them are the moves sets and the notations
class RBQ(Piece):
    def __init__(self, row, col, notation, moves):
        self.moves = moves
        self.attackMoves = self.moves

        super().__init__(row, col, notation)

    def canMove(self, newRow, newCol):
        # it can't move there if it's not in the moves set
        if not (newRow-self.row, newCol-self.col) in self.moves:
            return False
        
        # finding out the direction the piece will go, on the x and y axes
        signRow = 0
        signCol = 0
        if self.row != newRow:
            signRow = int(abs(newRow-self.row)/(newRow-self.row))
        if self.col != newCol:
            signCol = int(abs(newCol-self.col)/(newCol-self.col))



        # it can't move if there is a piece between its current and new position
        # we check every single suare between the current and next position, in the direction that we found out earlier
        diff = 0
        while self.row + signRow*diff != newRow or self.col + signCol*diff != newCol:
            diff += 1

            # if there is a piece between the current and next position
            if not board.isEmpty(self.row + signRow*diff, self.col + signCol*diff):

                # if the piece is exactly on the next position and its color is opposite to this piece's, then the piece can capture it
                if (self.row + signRow*diff == newRow and self.col + signCol*diff == newCol and 
                board.getPiece(newRow, newCol).notation[0] != self.notation[0]):
                    return True

                # otherwise, it can't move there
                return False


        return True

    # the rook, bishop and queen can attack another square if
    def isAttacking(self, row, col):

        # it is in their moves set
        if not (row-self.row, col-self.col) in self.moves:
            return False

        signRow = 0
        signCol = 0
        if self.row != row:
            signRow = int(abs(row-self.row)/(row-self.row))
        if self.col != col:
            signCol = int(abs(col-self.col)/(col-self.col))

        # and there is no piece between those 2 squares
        diff = 1
        while self.row + signRow*diff != row or self.col + signCol*diff != col:
            if not board.isEmpty(self.row + signRow*diff, self.col + signCol*diff): 
                return False
            diff += 1
        return True


class Bishop(RBQ):
    def __init__(self, row, col, color):
        notation = color[0]+"b"

        # the bishop can only move diagonally
        moves = set()
        for i in range(1, 8):
            for sgn1 in [-1, 1]:
                for sgn2 in [-1, 1]:
                    moves.add((i*sgn1, i*sgn2))

        super().__init__(row, col, notation, moves)

class Rook(RBQ):
    def __init__(self, row, col, color):
        notation = color[0]+"r"
        
        # the rook can only move in a straight line
        moves = set()
        for i in range(1, 8):
            for j in [-1, 1]:
                moves.add((i*j, 0))
                moves.add((0, i*j))

        super().__init__(row, col, notation, moves)


class Queen(RBQ):
    def __init__(self, row, col, color):
        notation = color[0]+"q"

        # the queen can move diagonally and in a straight line 
        moves = set()
        for i in range(1, 8):
            for sgn1 in [-1, 0, 1]:
                for sgn2 in [-1, 0, 1]:
                    if sgn1 != 0 or sgn2 != 0:
                        moves.add((i*sgn1, i*sgn2))

        super().__init__(row, col, notation, moves)

# the king is a special piece, it can only move to a square that isn't attacked by enemy pieces
class King(Piece):
    def __init__(self, row, col, color):
        notation = color[0]+"k"

        # it can only attack / move to the squares "touching" it
        self.moves = {(-1, -1), (-1, 0), (-1, 1), (0, 1), (0, -1), (1, -1), (1, 0), (1, 1)}
        self.attackMoves = self.moves

        super().__init__(row, col, notation)

    def canMove(self, newRow, newCol):
        if (newRow-self.row, newCol-self.col) not in self.moves:
            return False

        if (not board.isEmpty(newRow, newCol)) and board.getPiece(newRow, newCol).notation[0] != self.notation[0]:
            return True

        if board.isEmpty(newRow, newCol):
            return True

        return False

    # castling is a special move that involves the king and the rook kind of swapping places
    def canCastle(self, row, col):
        # the king cannot castle if it has already moved or if it's in check
        if self.hasMoved or self.isInCheck(self.row, self.col):
            return False

        # short castle
        if row == self.row and col == 6:
            # a lot of conditions have to be met: the king and the rook must not have moved, 
            # there has to be no piece between the king and the rook and every square between the king and the rook has to be safe from
            # checks from the enemy pieces
            return (board.isEmpty(self.row, 5) and board.isEmpty(self.row, 6) and not board.isEmpty(self.row, 7) and 
                    board.getPiece(self.row, 7).hasMoved == False and 
                    not self.isInCheck(self.row, 5) and not self.isInCheck(self.row, 6))
        
        # long castle
        elif row == self.row and col == 2:
            return (board.isEmpty(self.row, 3) and board.isEmpty(self.row, 2) and board.isEmpty(self.row, 1) 
                    and not board.isEmpty(self.row, 0) and 
                    board.getPiece(self.row, 0).hasMoved == False and 
                    not self.isInCheck(self.row, 3) and not self.isInCheck(self.row, 2))

        return False

    # the rook comes over and the king goes to the edge
    def castle(self, row, col):
        if col == 6:
            board.getPiece(self.row, 7).updateBoard(self.row, 5)
        else:
            board.getPiece(self.row, 0).updateBoard(self.row, 3)

        self.updateBoard(row, col)
                
    def isAttacking(self, row, col):
        return (row-self.row, col-self.col) in self.moves

    # we say the king is in check if it is attacked by an enemy piece
    # this method checks if any enemy piece is attacking a certain square
    def isInCheck(self, row, col):
        for r in board.board:
            for piece in r:
                if piece is None:
                    continue
                if piece.isAttacking(row, col) and piece.notation[0] != self.notation[0]:
                    return True
        return False