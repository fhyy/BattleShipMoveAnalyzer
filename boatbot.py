import asyncio
import sys
import math
import numpy as np

currentBoard = np.zeros((10,10), dtype=np.int32)
shipSizes = []

def readBoard():
    global currentBoard
    global shipSizes
    print("Reading board")
    if len(sys.argv) <= 1:
        print("You must input boardstate and ship sizes")
        exit(1)
    if len(sys.argv) <= 2:
        print("You must input ship sizes")
        exit(1)
    boardString = sys.argv[1]
    shipSizeString = sys.argv[2]
    print(boardString)
    print(shipSizeString)

    board = boardString
    if len(board) != 100:
        print("Board is not correct size (10x10 = 100) != " + str(len(board)))
        exit(1)

    for i in range(len(board)):
        if board[i] == 'B':
            currentBoard.itemset(i,1)
        elif board[i] == 'X':
            currentBoard.itemset(i,-1)
        else:
            currentBoard.itemset(i,0)

    for size in shipSizeString.split(","):
        shipSizes.append(int(size))

    printBoard(currentBoard)

def printBoard(board):
    print("Board")
    for y in range(10):
        for x in range(10):
            val = board.item(y,x)
            if val < 0:
                print(str(val), end = '')
            else:
                print(" " + str(val), end = '')
        print('')


async def placeAndCollectNumValidBoatsPerSquare(x, y, horizontal, sizesToPlace, boardState):
    newBoard = boardState.copy()
    validBoatsPerSquare = np.zeros((10,10), dtype=np.int32)

    if len(sizesToPlace) == 0:
        if 1 in boardState:
            return validBoatsPerSquare
        return np.clip(boardState, 0, 1)
    
    couldPlace = True
    if horizontal:
        if x > 10-sizesToPlace[0]:
            couldPlace = False
        else:
            for dx in range(sizesToPlace[0]):
                if newBoard.item(y,x+dx) != 0 and newBoard.item(y,x+dx) != 1:
                    couldPlace = False
                    break
                newBoard.itemset(y,x+dx,sizesToPlace[0])
    else:
        if y > 10-sizesToPlace[0]:
            couldPlace = False
        else:
            for dy in range(sizesToPlace[0]):
                if newBoard.item(y+dy,x) != 0 and newBoard.item(y+dy,x) != 1:
                    couldPlace = False
                    break
                newBoard.itemset(y+dy,x,sizesToPlace[0])
    
    
    if not couldPlace:
        return validBoatsPerSquare
    
    for nextX in range(10):
        for nextY in range(10):
            L = await asyncio.gather(
                placeAndCollectNumValidBoatsPerSquare(nextX, nextY, True, sizesToPlace[1:], newBoard),
                placeAndCollectNumValidBoatsPerSquare(nextX, nextY, False, sizesToPlace[1:], newBoard)
            )
            validBoatsPerSquare = validBoatsPerSquare + L[0] + L[1]

    return validBoatsPerSquare

def printIndex(index):
    print(str(index%10) + " - " + str(index//10))

async def main():
    readBoard()

    results = np.zeros((10,10), dtype=np.int32)
    for nextX in range(10):
        for nextY in range(10):
            print(str(nextX) + " - " + str(nextY))
            printBoard(results)
            L = await asyncio.gather(
                placeAndCollectNumValidBoatsPerSquare(nextX, nextY, True, shipSizes, currentBoard),
                placeAndCollectNumValidBoatsPerSquare(nextX, nextY, False, shipSizes, currentBoard)
            )
            results = results + L[0] + L[1]
        
    filteredResults = results - np.multiply(results, currentBoard)
    printBoard(filteredResults)

    maxIndices = np.argmax(filteredResults)

    print(str(maxIndices))

    if isinstance(maxIndices, list):
        for index in maxIndices:
            printIndex(index)
    else:
        printIndex(maxIndices)
            

loop = asyncio.get_event_loop()
loop.run_until_complete(main())