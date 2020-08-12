import cv2
import numpy as np
import ai

# board dimensions
ROW_LENGTH = 10
COLUMN_LENGTH = 20

# piece colors
pieces = {
    "i_piece": np.array([215, 155, 15]),
    "o_piece": np.array([2, 159, 227]),
    "t_piece": np.array([138, 41, 175]),
    "j_piece": np.array([198, 65, 33]),
    "l_piece": np.array([2, 91, 227]),
    "s_piece": np.array([1, 177, 89]),
    "z_piece": np.array([55, 15, 215]),
    "dead_piece": np.array([153, 153, 153]),
    "empty": np.array([0, 0, 0])
}

# detect board
board_image = cv2.imread("C:\\Users\\Elton\\Documents\\workspace\\tetris\\screenshots\\setup\\initial_board.png")
board_color = np.array([57, 57, 57])
board_mask = cv2.inRange(board_image, board_color, board_color)

# create virtual board
board = np.zeros((COLUMN_LENGTH, ROW_LENGTH))
image_x, image_y, _ = board_image.shape
virtual_board = np.zeros((image_x, image_y, 3), dtype=np.uint8)

contours, _ = cv2.findContours(board_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# make sure to get the board and not misc elements in image
contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
board_contour = contours[0]
(board_x, board_y, board_width, board_height) = cv2.boundingRect(board_contour)
cv2.drawContours(virtual_board, [board_contour], -1, (255,255,255), 5)

# hold, next, current piece detecting box
hold_next_current_image = cv2.imread("C:\\Users\\Elton\\Documents\\workspace\\tetris\\screenshots\\setup\\hold_next_current.png")
next_color = np.array([0, 0, 255])
hold_color = np.array([0, 255, 0])
current_color = np.array([255, 0, 0])
next_mask = cv2.inRange(hold_next_current_image, next_color, next_color)
hold_mask = cv2.inRange(hold_next_current_image, hold_color, hold_color)
current_mask = cv2.inRange(hold_next_current_image, current_color, current_color)
contours, _ = cv2.findContours(next_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
next_contour = contours[0]
cv2.drawContours(virtual_board, [next_contour], -1, (255,255,255), 5)
contours, _ = cv2.findContours(hold_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
hold_contour = contours[0]
cv2.drawContours(virtual_board, [hold_contour], -1, (255,255,255), 5)
contours, _ = cv2.findContours(current_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
current_contour = contours[0]
cv2.drawContours(virtual_board, [current_contour], -1, (255,255,255), 5)


# cell dimensions
block_width = int(board_width/ROW_LENGTH)
block_height = int(board_height/COLUMN_LENGTH)

# turns image into array
def get_board(image_path):
    board = np.zeros((COLUMN_LENGTH, ROW_LENGTH))
    image = cv2.imread(image_path)

    # crop image
    image = image[:700, :1000]

    hold_piece = ""
    next_piece = ""
    current_piece = ""

    # create mask for each piece
    for piece_name in pieces:
        # get piece contour
        piece_color = pieces[piece_name]
        mask = cv2.inRange(image, piece_color, piece_color)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            # cant get dead pieces without reading the screen
            if piece_name == "dead_piece":
                cv2.drawContours(virtual_board, [contour], -2, (0, 0, 255), 2)
                # check if each spot in board array is in piece contour
                for i in range(COLUMN_LENGTH):
                    for j in range(ROW_LENGTH):
                        block_x = block_width*j
                        block_y = block_height*i
                        if piece_name != "empty":
                            cv2.rectangle(virtual_board, (board_x+block_x, board_y+block_y), (board_x+block_x+block_width, board_y+block_y+block_height), (255,255,255), 1)
                            # if middle of each cell in contour
                            if cv2.pointPolygonTest(contour, (board_x+block_x+(block_width/2), board_y+block_y+(block_height/2)), False) >= 0:
                                board[i][j] = 1
                        else:
                            # rewrite black squares on board
                            (contour_x, contour_y, contour_width, contour_height) = cv2.boundingRect(contour)
                            if cv2.pointPolygonTest(board_contour, (contour_x+(contour_width/2), contour_y+(contour_height/2)), False) > 0 and cv2.contourArea(contour) < 1000:
                                if cv2.pointPolygonTest(contour, (board_x+block_x+(block_width/2), board_y+block_y+(block_height/2)), False) >= 0:
                                    board[i][j] = 0
            # detect holding, next, current piece
            if piece_name != "empty" and piece_name != "dead_piece":
                (contour_x, contour_y, contour_width, contour_height) = cv2.boundingRect(contour)
                if cv2.pointPolygonTest(hold_contour, (contour_x, contour_y), False) > 0:
                    hold_piece = piece_name
                if cv2.pointPolygonTest(next_contour, (contour_x, contour_y), False) > 0:
                    next_piece = piece_name
                if cv2.pointPolygonTest(current_contour, (contour_x, contour_y), False) > 0:
                    current_piece = piece_name

    board[0] = np.zeros((1, ROW_LENGTH))
    for i in range(4):
        board = np.insert(board, 0, 0, axis=0)

    return (board, current_piece, next_piece, hold_piece)

# board, current_piece, next_piece, hold_piece = get_board("C:\\Users\\Elton\\Documents\\workspace\\tetris\\screenshots\\game\\screenshot_104.png")
# dead_piece_indexes = []
# for row in range(len(board)):
#     if np.any(board[row] != 0):
#         dead_piece_indexes.append(row)
# dead_pieces = board[dead_piece_indexes[0]:dead_piece_indexes[-1]+1]
# board = np.zeros((20,10))
# board[-1] = [1, 0, 0, 1, 1, 1, 1, 0, 0, 1]
# board[-2] = [1, 0, 0, 1, 1, 1, 1, 0, 0, 1]
# board = board[len(dead_piece_indexes):]
# board = np.append(board, dead_pieces, axis=0)
# print(board[:-len(dead_piece_indexes)])
# print(ai.best_move(board, current_piece, hold_piece))