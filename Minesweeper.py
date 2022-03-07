import random
import re
from enum import Enum 

class Levels(Enum):
    BEGINNER = (8, 10)
    INTERMEDIATE = (15, 40)
    ADVANCED = (30, 99)
class Board:
    def __init__(self, board_size, no_of_mines):
        self.board_size = board_size
        self.no_of_mines = no_of_mines

        # create board and plant mines.
        self.board = self.create_board()
        self.assign_values_to_board()

        # keep a set to keep track of locations uncovered. 
        # This is saved as a set of tuple(row, col)
        self.dug = set()
        self.mark = set()

    def create_board(self):
        # create a board for given board_size and no_of_mines.
        # board is list of lists - for 2D array.

        # empty board
        board = [[None for _ in range(self.board_size)]for _ in range(self.board_size)]

        # plant mines
        mines_planted = 0
        while mines_planted < self.no_of_mines:
            cell = random.randint(0, self.board_size ** 2 - 1)
            row = cell // self.board_size
            col =  cell % self.board_size

            if board[row][col] == '*':
                # check if mine is already placed in that cell.
                continue
            # else plan a mine
            board[row][col] = '*' 
            mines_planted += 1

        return board

    def assign_values_to_board(self):
        # assign numbers 0-8 for all empty spaces, which represent number of mines 
        # present in the neighboring cells. 

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == '*':
                    # cell is a bomb, so do nothing.
                    continue
                self.board[row][col] = self.get_neigboring_mines_count(row, col)
    
    def get_neigboring_mines_count(self, row, col):
        # iterate through all neighboring 8 cells and count the number of mines
        # use max, min to make sure not to explore other than these 8 cells.

        neighboring_mine_count = 0

        for r in range(max(0, row - 1), min(self.board_size - 1, row + 1) + 1):
            for c in range(max(0, col - 1), min(self.board_size - 1, col + 1) + 1):
                if r == row and c == col:
                    # our original cell, don't check
                    continue
                if self.board[r][c] == '*':
                    neighboring_mine_count += 1
        return neighboring_mine_count

    def dig(self, row, col):
        # dig the cell.
        # return True if successful dig, False if there is a mine.
        # Case1: hit a mine - game over
        # case2: dig with neighboring mines - finish dig
        # case3: dig with no neighboring mines - recursively dig until neighboring mines. 

        self.dug.add((row, col))

        if self.board[row][col] == '*':
            return False
        elif self.board[row][col] > 0:
            return True
        
        # self.board[row][col] == 0

        for r in range(max(0, row - 1), min(self.board_size - 1, row + 1) + 1):
            for c in range(max(0, col - 1), min(self.board_size - 1, col + 1) + 1):
                if (r, c) in self.dug:
                    # already in set - so do nothing and continue
                    continue 
                # case3 - recurively dig
                self.dig(r, c)
        # if our initial didn't hit a mine, we should't hit a mine here - so return True
        return True

    dx = [1, -1, 1, -1, 0, 0, 1, -1]
    dy = [1, -1, -1, 1, 1, -1, 0, 0]

    def dfs_dig(self, row, col):
        self.dug.add((row, col))
        # print(self.board)
        if len(self.dug) >= (self.board_size) ** 2:
            return True

        if self.board[row][col] == '*':
            return False

        elif self.board[row][col] == 0:
            if (row, col) not in self.dug:
                r = max(0, row - 1)
                c = max(0, col - 1)
                return self.dfs_dig(r, c)

        elif self.board[row][col] > 0:
            for i in range(0, 8):
                r = row + self.dx[i]
                c = col + self.dy[i]
                if self.is_valid_cell(r, c):
                    return self.dfs_dig(r,c)

    def single_point(self, row, col):
        next_set = set() # set s in algorithm

        while self.board[row][col] != '*' and len(self.dug) + self.no_of_mines == (self.board_size) ** 2:
            # no need to get random starting cell cz we are taking that from user.
            next_set.add((row, col))
            for (row,col) in next_set.copy():
                self.dug.add((row, col))
                if self.board[row][col] == '*':
                    return False
                unmarked_neighbors = self.get_unmarked_neighbors(row, col)
                # check if unmarked is all free neighbors i.e., all are zeroes
                if self.is_afn(row, col):
                    for element in unmarked_neighbors:
                        next_set.add((element[0], element[1]))
                elif self.is_amn(row, col):
                    for element in unmarked_neighbors:
                        self.dug.add((element[0], element[1]))
                else:
                    continue

    def double_set_single_point(self, row, col):
        next_set = set()
        next_set.add((row, col))
        q_set = set()

        while self.board[row][col] != '*' and len(self.dug) + self.no_of_mines >= (self.board_size) ** 2:
            if len(next_set) == 0:
                x = (random.randint(0, self.board_size), random.randint(0, self.board_size))
                next_set.add(x)
            while len(next_set) != 0:
                x = next_set.pop()
                if self.is_valid_cell(x[0], x[1]):
                    r = x[0]
                    c = x[1]
                    self.dug.add(x)
                    if self.board[r][c] == '*':
                        return False
                    if self.is_afn(r, c):
                        unmarked_neighbors = self.get_unmarked_neighbors(r, c)
                        next_set = next_set.union(unmarked_neighbors)
                    else:
                        cell = (r, c)
                        q_set = q_set.union({cell})

            for q in q_set.copy():
                r = q[0]
                c = q[1]
                if self.is_amn(r, c):
                    unmarked_neighbors_q = self.get_unmarked_neighbors(r, c)
                    for element in unmarked_neighbors_q:
                        self.dug.add((element[0], element[1]))
                    q_set.remove(q)
            for q in q_set.copy():
                r = q[0]
                c = q[1]
                unmarked_neighbors_q = self.get_unmarked_neighbors(r, c)
                if self.is_afn(r, c):
                    next_set = next_set.union(unmarked_neighbors_q)
                    q_set.remove(r, c)
                

    def get_unmarked_neighbors(self, row, col):
        unmarked_neighbors = set()
        for i in range(0, 8):
            r = row + self.dx[i]
            c = col + self.dy[i]
            if (r, c) not in self.dug:
                unmarked_neighbors.add((r, c))
        return unmarked_neighbors
    
    def is_afn(self, row, col):
    # Checks if the neighbors of a given cell are all free
        count = 0
        for i in range(0, 8):
            r = row + self.dx[i]
            c = col + self.dy[i]
            if self.is_valid_cell(r, c):
                if self.board[r][c] == 0:
                    count += 1
        if count == 8:
            return True
        else:
            return False
    
    def is_amn(self, row, col):
    # Checks if the neighbors of a given cell are all mines
        count = 0
        for i in range(0, 8):
            r = row + self.dx[i]
            c = col + self.dy[i]
            if self.is_valid_cell(r, c):
                if self.board[r][c] != '*' and int(self.board[r][c]) >= 0:
                    count += 1
        if count == 8:
            return True
        else:
            return False

    def is_valid_cell(self, r, c):
        if r >= 0 and r < self.board_size and c >= 0 and c < self.board_size:
            return True
        else: return False
         
    def __str__(self):
        # return a string that displays board.
        display_board = [[None for _ in range(self.board_size)]for _ in range(self.board_size)]
        for row in range(self.board_size):
            for col in range(self.board_size):
                if(row, col) in self.dug:
                    display_board[row][col] = str(self.board[row][col])
                else:
                    display_board[row][col] = ' '

        # string repr of board
        string_rep = ''
        # get max column widths for printing
        widths = []
        for index in range(self.board_size):
            columns = map(lambda x: x[index], display_board)
            widths.append(
                len(
                    max(columns, key = len)
                )
            )

        # print the csv strings
        indices = [i for i in range(self.board_size)]
        indices_row = '   '
        cells = []
        for index, col in enumerate(indices):
            format = '%-' + str(widths[index]) + "s"
            cells.append(format % (col))
        indices_row += '  '.join(cells)
        indices_row += '  \n'
        
        for i in range(len(display_board)):
            row = display_board[i]
            string_rep += f'{i} |'
            cells = []
            for index, col in enumerate(row):
                format = '%-' + str(widths[index]) + "s"
                cells.append(format % (col))
            string_rep += ' |'.join(cells)
            string_rep += ' |\n'

        str_len = int(len(string_rep) / self.board_size)
        string_rep = indices_row + '-'*str_len + '\n' + string_rep + '-'*str_len
        return string_rep

# play the game
def play(board_size, no_of_mines, algorithm):
    # 1. Create board and place mines.

    board = Board(board_size, no_of_mines)
    # 2. Display board and take row and col input from user.
    # 3a. If location is mine - display game over and end game.
    # 3b. If location is not a mine, display all the cells until there is a mine next
    # to a cell.
    # 4. Repeat steps 2 and 3 until there are no cells to unfold and display 
    # victory message.
    is_successful = True
    while len(board.dug) < board.board_size ** 2 - no_of_mines:
        print(board)
        # use regex to split input at comma and spaces and get row and col.
        cell = re.split(',(\\s)*', input("Enter row, col: "))
        row, col = int(cell[0]), int(cell[-1])
        if row < 0 or row >= board_size or col < 0 or col >= board_size:
            print("Invalid cell. Try again.")
            continue
        is_successful = False
        # if cell is valid
        if algorithm == 1:
            is_successful = board.dig(row, col)
        if algorithm == 2:
            is_successful = board.dfs_dig(row, col)
        if algorithm == 3:
            is_successful = board.single_point(row, col)
        if algorithm == 4:
            is_successful = board.double_set_single_point(row, col)

        if not is_successful:
            # dug a mine - game over
            break
    # 2 ways to d loop if is_successful = True
    if is_successful:
        print("You Won!!")
        
    else: 
        print("Game Over!!")
        # print the board
        board.dug = [(r,c) for r in range(board_size) for c in range(board_size)]
        print(board)

if __name__== '__main__':
    print("b - beginner")
    print("i - intermediate")
    print("a - advanced")

    level = input("Choose your level: ")

    print("1. Play human")
    print("2. Run dfs algorithm")
    print("3. Run single point algorithm")
    print("4. Play double set sinle point algorithm")

    algoritm = input("Choose your algorithm: ")

    if level == 'b':
        if int(algoritm) == 1 or int(algoritm) == 2 or int(algoritm) == 3 or int(algoritm) == 4:
            play(Levels.BEGINNER.value[0],Levels.BEGINNER.value[1], int(algoritm))
        else:
            print("Invalid algorithm.")

    elif level == 'i':
        if int(algoritm) == 1 or int(algoritm) == 2 or int(algoritm) == 3 or int(algoritm) == 4:
            play(Levels.INTERMEDIATE.value[0],Levels.INTERMEDIATE.value[1], int(algoritm))
        else:
            print("Invalid algorithm.")

    elif level == 'a':
        if int(algoritm) == 1 or int(algoritm) == 2 or int(algoritm) == 3 or int(algoritm) == 4:
            play(Levels.ADVANCED.value[0],Levels.ADVANCED.value[1], int(algoritm))
        else:
            print("Invalid algorithm.")
        
    else:
        print("Invalid entry. Try again")