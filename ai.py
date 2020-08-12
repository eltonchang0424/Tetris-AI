import numpy as np
import math

# scoring weights
LINE_WEIGHT = .760666
HEIGHT_WEIGHT = -0.51006
BUMP_WEIGHT = -0.184483
HOLE_WEIGHT = -0.35663
HOLE_DEPTH_WEIGHT = -0.35663

# board dimensions
ROW_LENGTH = 10
COLUMN_LENGTH = 20

board = np.zeros((COLUMN_LENGTH, ROW_LENGTH))
pieces = {
    "i_piece": np.array([[0, 0, 0, 0],
                         [1, 1, 1, 1],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]]),
    "o_piece": np.array([[1, 1],
                         [1, 1]]),
    "t_piece": np.array([[0, 1, 0],
                         [1, 1, 1],
                         [0, 0, 0]]),
    "j_piece": np.array([[1, 0, 0],
                         [1, 1, 1],
                         [0, 0, 0]]),
    "l_piece": np.array([[0, 0, 1],
                         [1, 1, 1],
                         [0, 0, 0]]),
    "s_piece": np.array([[0, 1, 1],
                         [1, 1, 0],
                         [0, 0, 0]]),
    "z_piece": np.array([[1, 1, 0],
                         [0, 1, 1],
                         [0, 0, 0]])
}

# returns all states of board and inputs to reach that state of piece dropped
def drop_piece(board, piece_name):
    states = []
    piece = pieces[piece_name]

    for rot_count in range(4):
        # keep track of the moves to reach board state
        rots = str(rot_count)
        temp_piece = np.rot90(piece, rot_count)

        # original x position of each piece
        origin_x = int(ROW_LENGTH/2 - math.ceil(len(temp_piece)/2))

        # find piece width and height to know playable locations
        piece_length = np.count_nonzero(np.sum(temp_piece, axis=0))
        piece_height = np.count_nonzero(np.sum(temp_piece, axis=1))

        # go over all possible starting positions
        for z in range(ROW_LENGTH-piece_length+1):
            not_collided = True
            col_offset_add = 0
            # starting top left position of each piece
            piece_x = z
            piece_y = 0
            while not_collided:
                temp_board = np.copy(board)
                # check each potential spot the piece could move down in
                # offset to get rid of rows/cols of zeroes before the piece
                row_offset = 0
                for i in range(len(temp_piece)):
                    if np.count_nonzero(temp_piece[i]) == 0:
                        row_offset += 1
                    col_offset = 0
                    found_col_offset = False
                    for j in range(len(temp_piece)):
                        if not found_col_offset and np.count_nonzero(np.rot90(temp_piece, 3)[j]) == 0:
                            col_offset += 1
                        elif not found_col_offset and np.count_nonzero(np.rot90(temp_piece, 3)[j]) != 0:
                            found_col_offset = True
                        if not_collided:
                            if temp_piece[i][j] != 0:
                                # check if reached bottom of board or if the position of where a piece is is occupied
                                if piece_y+piece_height-1 == len(temp_board)-1 or temp_board[i+piece_y-row_offset+1][j+piece_x-col_offset] != 0:
                                    # collision detected
                                    not_collided = False
                                    # write the piece on the board
                                    row_offset = 0
                                    for x in range(len(temp_piece)):
                                        if np.count_nonzero(temp_piece[x]) == 0:
                                            row_offset += 1
                                        col_offset = 0
                                        found_col_offset = False
                                        for y in range(len(temp_piece)):
                                            if not found_col_offset and np.count_nonzero(np.rot90(temp_piece, 3)[y]) == 0:
                                                col_offset += 1
                                                col_offset_add = col_offset
                                            elif not found_col_offset and np.count_nonzero(np.rot90(temp_piece, 3)[y]) != 0:
                                                col_offset_add = col_offset
                                                found_col_offset = True
                                            if temp_piece[x][y] != 0:
                                                temp_board[piece_y+x-row_offset][piece_x+y-col_offset] = temp_piece[i][j]
                                    moves = " " + str(z-origin_x-col_offset_add)
                                    # add to results if not already in
                                    exists = False
                                    for s in states:
                                        if np.array_equal(s[0],temp_board):
                                            exists = True
                                    if not exists:
                                        states.append([temp_board, rots+moves])
                # keep track of the moves to reach board state
                piece_y += 1
    return states
                    
# minimize holes, minimize height, minimize bumpiness, maximize lines
def score_board(board):
    score = 0
    height = 0
    heights = []
    lines = 0
    bump = 0
    holes = 0
    hole_index = []
    hole_depth = 0

    # sum up all the heights of each col
    for col in np.rot90(board, 3):
        h = 0
        for i in range(COLUMN_LENGTH):
            if col[i] != 0:
                h = i+1
        heights.append(h)
        height += h

    # count number of lines cleared
    for row in board:
        if np.all(row != 0):
            lines += 1

    # quantify "bumpiness"
    for i in range(len(heights)-1):
        bump += abs(heights[i]-heights[i+1])
    #bump += abs(heights[-1]-heights[0])

    # count number of holes
    for col in np.rot90(board, 3):
        for i in range(COLUMN_LENGTH-1):
            if col[i] == 0 and col[i+1] != 0:
                holes += 1 
                hole_index.append(i)
    
    # quantify hole depth
    # for col in np.rot90(board, 3):
    #     for index in hole_index:
    #         for i in range(index+1, COLUMN_LENGTH):
    #             if col[i] == 1:
    #                 hole_depth += 1

    score = LINE_WEIGHT*lines+HEIGHT_WEIGHT*height+HOLE_WEIGHT*holes+BUMP_WEIGHT*bump
    return (score, lines)

# clears the lines on board
def refresh_board(board):
    row = len(board)-1
    while row != -1:
        if np.all(board[row] != 0):
            temp_board = np.insert(board, 0, 0, axis=0)
            board[:row+1] = temp_board[:row+1]
            row += 1
        row -= 1
    return board

# finds the best move to make, returns whether to switch to hold piece and corresponding moves
def best_move(board, piece_name, hold_piece_name):
    piece_moves = drop_piece(board, piece_name)
    
    hold_piece_moves = drop_piece(board, hold_piece_name)

    # find best move for each piece
    piece_score = []
    hold_score = []
    for move in piece_moves:
        piece_score.append([score_board(move[0]), move])
    for move in hold_piece_moves:
        hold_score.append([score_board(move[0]), move])
    
    # debugging
    # for p in piece_score:
    #     print(p)

    max_piece_score = sorted(piece_score, key = lambda x: x[0][0], reverse=True)[0]
    max_hold_score = sorted(hold_score, key = lambda x: x[0][0], reverse=True)[0]
    
    # # if best move is i piece, check that it clears at least 1 line otherwise play other piece
    # if max_piece_score[0][0] < max_hold_score[0][0]:
    #     if hold_piece_name == "i_piece":
    #         if max_hold_score[0][1] > 0:
    #             return (True, max_hold_score[1][1], max_hold_score[1][0])
    #         else:
    #             return (False, max_piece_score[1][1], max_piece_score[1][0])
    #     else:
    #         return (True, max_hold_score[1][1], max_hold_score[1][0])
    # else:
    #     if piece_name == "i_piece":
    #         if max_piece_score[0][1] > 0:
    #             return (False, max_piece_score[1][1], max_piece_score[1][0])
    #         else:
    #             return (True, max_hold_score[1][1], max_hold_score[1][0])
    #     else:
    #         return (False, max_piece_score[1][1], max_piece_score[1][0])

    if max_piece_score[0][0] < max_hold_score[0][0]:
        return (True, max_hold_score[1][1], max_hold_score[1][0])
    return (False, max_piece_score[1][1], max_piece_score[1][0])
