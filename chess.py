import math
import sys
import pygame
import pieces
import drawChecks
import board
import time
pygame.init()

global turn
global done

size = width, height = 560, 560
screen = pygame.display.set_mode(size)


# the function that draws the promotion choice table and transforms the pawn into another piece 
def promote(pos, row, col, color):
    # calculate the position of the rects
    rectDim = 150
    rectRow = None
    rectCol = None
    if pos[0]+rectDim >= height:
        rectRow = pos[0]-rectDim-1
    else:
        rectRow = pos[0]

    if pos[1]+rectDim >= width:
        rectCol = pos[1]-rectDim-1
    else:
        rectCol = pos[1]


    rects = []
    imgs = []
    imgRects = []
    # display the rects 
    for x in [rectRow, rectRow+int(rectDim/2)+1]:
        for y in [rectCol, rectCol+int(rectDim/2)+1]: 
            rects.append(pygame.draw.rect(screen, (255, 255, 255), (x, y, int(rectDim/2), int(rectDim/2))))
    pygame.draw.line(screen, (50, 50, 50), (rectRow+int(rectDim/2), rectCol), (rectRow+int(rectDim/2), rectCol+rectDim))
    pygame.draw.line(screen, (50, 50, 50), (rectRow, rectCol+int(rectDim/2)), (rectRow+rectDim, rectCol+int(rectDim/2)))

    # display the imgs
    for piece in ["q", "r", "n", "b"]:
        imgs.append(pygame.image.load("imgs/"+color[0]+piece+".png"))
        imgRects.append(imgs[len(imgs)-1].get_rect())
        imgRects[len(imgs)-1].center = rects[len(imgs)-1].center
        screen.blit(imgs[len(imgs)-1], imgRects[len(imgs)-1])

    pygame.display.update()

    # transform the pawn into another piece
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if rects[0].collidepoint(event.pos):
                    pieces.Queen(row, col, color)
                    board.getPiece(row, col).draw(screen, width, height)
                    return
                if rects[1].collidepoint(event.pos):
                    pieces.Rook(row, col, color)
                    board.getPiece(row, col).draw(screen, width, height)
                    return
                if rects[2].collidepoint(event.pos):
                    pieces.Knight(row, col, color)
                    board.getPiece(row, col).draw(screen, width, height)
                    return
                if rects[3].collidepoint(event.pos):
                    pieces.Bishop(row, col, color)
                    board.getPiece(row, col).draw(screen, width, height)
                    return


# a method for checking if the game is drawn or won
# a draw can be reached by stalemate (no legal moves for a player but their king is not in check), 
# by repeating the same positon 3 times, 
# by insufficient material for checkmate 
# or if there were no captures/pawn moves in the last 50 moves
def checkEndOfGame(currentBoard):
    global done
    # if the game is done, call the displayEndScreen function
    if (not drawChecks.hasLegalMoves(turn) or not drawChecks.enoughMaterial() or pieces.fiftyMove > 100 or
    board.positionsDict[currentBoard] >= 3):
        done = True
        text = ""
        if board.positionsDict[currentBoard] >= 3:
            text = "Draw by repetition."
        elif pieces.fiftyMove > 100:
            text = "Draw by 50 move rule."
        elif not drawChecks.enoughMaterial():
            text = "Draw by insufficient material."
        elif turn == "w":
            if pieces.whiteKing.isInCheck(pieces.whiteKing.row, pieces.whiteKing.col):
                text = "Black won by checkmate!"
            else:
                text = "Draw by stalemate."
        else:
            if pieces.blackKing.isInCheck(pieces.blackKing.row, pieces.blackKing.col):
                text = "White won by checkmate!"
            else:
                text = "Draw by stalemate."
                
        displayEndScreen(text)


# a function that displays the outcome of the game on the screen, and then restarts the game
def displayEndScreen(text):
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, width, height))
    font = pygame.font.Font("freesansbold.ttf", 30)
    textSurface = font.render(text, True, (0, 0, 0, 0.5))
    textRect = textSurface.get_rect()
    textRect.center = (int(width/2), int(height/2))

    screen.blit(textSurface, textRect)
    pygame.display.update()

    time.sleep(5)


# the infinite game loop
def gameLoop():
    global done
    global turn

    done = False
    turn = "w"
    pieces.fiftyMove = 0

    pieces.initGame()
    currentBoard = board.getString(turn)
    board.positionsDict[currentBoard] = 1
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # if the user presses the mouse
            if event.type == pygame.MOUSEBUTTONDOWN:

                # get the row and column the mouse is located in
                currentRow = math.floor(event.pos[1] / int(height/8))
                currentCol = math.floor(event.pos[0] / int(width/8))
            
                # if there is a piece that the user clicks on and it is its turn, make it the current piece
                piece = board.getPiece(currentRow, currentCol)
                if piece is not None and turn == piece.notation[0]:
                    pieces.currentPiece = piece
                        
            # if the user releases the mouse, try to move the piece and switch the turn if the move is successful
            if event.type == pygame.MOUSEBUTTONUP and pieces.currentPiece is not None:
                nextRow = math.floor(event.pos[1] / int(height/8))
                nextCol = math.floor(event.pos[0] / int(width/8))

                if pieces.currentPiece.move(nextRow, nextCol):
                    # promotion of a pawn
                    if pieces.currentPiece.notation[1] == "p" and pieces.currentPiece.row in [0, 7]:
                        promote(event.pos, pieces.currentPiece.row, pieces.currentPiece.col, turn)

                    if turn == "w":
                        turn = "b"
                    else:
                        turn = "w"

                    # remove the hasJustMovedTwo attribute if the enemy turn passed and they can't capture the pawn en passant anymore
                    for r in board.board:
                        for piece in r:
                            if piece is None or piece.notation != (turn+"p"):
                                continue
                            piece.hasJustMovedTwo = False

                    # update the positions dictionary
                    currentBoard = board.getString(turn)
                    if currentBoard in board.positionsDict:
                        board.positionsDict[currentBoard] += 1
                    else:
                        board.positionsDict[currentBoard] = 1

                # the current piece should be none if the mouse is released
                pieces.currentPiece = None

            # draw the squares of the board
            colors = [(232, 235, 239), (125, 135, 150)]
            for i in range(0, 8):
                for j in range(0, 8):
                    # change the color based on the col+row mod 2
                    pygame.draw.rect(screen, colors[(i+j)%2], (i*int(width/8), j*int(height/8), int(width/8), int(height/8)))
        
            # highlight the square of the king with red if it is in check
            for king in [pieces.whiteKing, pieces.blackKing]:
                if king.isInCheck(king.row, king.col):
                    pygame.draw.rect(screen, (255, 0, 0), (king.col*int(width/8), king.row*int(height/8), int(width/8), int(height/8)))

            # display the pieces in their respective squares
            for row in board.board:
                for piece in row:
                    if piece is None:
                        continue
                    if pieces.currentPiece != piece:
                        piece.draw(screen, width, height)

            # display the current piece at the mouse location      
            if pieces.currentPiece is not None:
                screen.blit(pieces.currentPiece.img, pieces.currentPiece.imgRect)
                pieces.currentPiece.imgRect.center = pygame.mouse.get_pos()

            checkEndOfGame(currentBoard)

            pygame.display.flip()
            pygame.display.update()
        

gameLoop()
