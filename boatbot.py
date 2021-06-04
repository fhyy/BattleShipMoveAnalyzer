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
        
async def placeAndCollectNumValidBoatsPerSquareOnLocation(x, y, sizesToPlace, boardState):
    L = await asyncio.gather(
        placeAndCollectNumValidBoatsPerSquare(x, y, True, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquare(x, y, False, sizesToPlace, boardState)
    )
    return L[0] + L[1]

async def placeAndCollectNumValidBoatsPerSquarePerY(x, sizesToPlace, boardState):
    L = await asyncio.gather(
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 0, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 1, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 2, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 3, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 4, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 5, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 6, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 7, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 8, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquareOnLocation(x, 9, sizesToPlace, boardState)
    )
    return L[0] + L[1] + L[2] + L[3] + L[4] + L[5] + L[6] + L[7] + L[8] + L[9]
        
async def placeAndCollectNumValidBoatsPerSquarePerX(sizesToPlace, boardState):
    L = await asyncio.gather(
        placeAndCollectNumValidBoatsPerSquarePerY(0, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquarePerY(1, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquarePerY(2, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquarePerY(3, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquarePerY(4, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquarePerY(5, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquarePerY(6, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquarePerY(7, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquarePerY(8, sizesToPlace, boardState),
        placeAndCollectNumValidBoatsPerSquarePerY(9, sizesToPlace, boardState)
    )
    return L[0] + L[1] + L[2] + L[3] + L[4] + L[5] + L[6] + L[7] + L[8] + L[9]

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
    
    if len(sizesToPlace) == 1:
        if 1 in newBoard:
            return validBoatsPerSquare
        return np.clip(newBoard, 0, 1)
    
    return await placeAndCollectNumValidBoatsPerSquarePerX(sizesToPlace[1:], newBoard)

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