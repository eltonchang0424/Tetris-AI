import cv2
import numpy as np
import pyautogui
from pynput import keyboard
from pynput.keyboard import Key, Controller
import time

import ai
import screenRead

keyboard_input = Controller()
screenshot_path = "C:\\Users\\Elton\\Documents\\workspace\\tetris\\screenshots\\game\\"
start = False
end = False
ss_counter = 1
take_screenshot = False

START_KEY = Key.shift
END_KEY = Key.esc
DROP_KEY = Key.space
ROTATE_KEY = 'z'
SWAP_KEY = 'c'
LEFT_KEY = Key.left
RIGHT_KEY = Key.right

def on_press(key):
    if key == START_KEY:
        global start
        start = True
    if key == END_KEY:
        global end
        end = True
    
def on_release(key):
    if key == START_KEY:
        global start
        start = True
    if key == END_KEY:
        global end
        end = True

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

boards = []
boards.append(np.zeros((20, 10)))

while True:
    if start == True:
        # take screenshot
        ss = pyautogui.screenshot()
        ss = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)
        cv2.imwrite("screenshots\\game\\screenshot_"+str(ss_counter)+".png", ss)
        image_path = "C:\\Users\\Elton\\Documents\\workspace\\tetris\\screenshots\\game\\screenshot_"+str(ss_counter)+".png"
        dead_piece_array, current_piece, next_piece, hold_piece = screenRead.get_board(image_path)
        dead_piece_indexes = []
        for row in range(len(dead_piece_array)):
            if np.any(dead_piece_array[row] != 0):
                dead_piece_indexes.append(row)

        # add dead pieces to previous board state to score
        if len(dead_piece_indexes) > 0:
            dead_pieces = dead_piece_array[dead_piece_indexes[0]:dead_piece_indexes[-1]+1]
            boards[-1] = boards[-1][len(dead_piece_indexes):]
            boards[-1] = np.append(boards[-1], dead_pieces, axis=0)

        if hold_piece == "":
            # score with the dead pieces in play
            swap, moves, board = ai.best_move(boards[-1], current_piece, next_piece)
            # splice off the dead pieces
            if len(dead_piece_indexes) > 0:
                board = board[:-len(dead_piece_indexes)]
            for i in range(len(dead_piece_indexes)):
                board = np.insert(board, 0, 0, axis=0)
            board = ai.refresh_board(board)
            boards.append(board)
        else:
            # score with the dead pieces in play
            swap, moves, board = ai.best_move(boards[-1], current_piece, hold_piece)
            # splice off the dead pieces
            if len(dead_piece_indexes) > 0:
                board = board[:-len(dead_piece_indexes)]
            for i in range(len(dead_piece_indexes)):
                board = np.insert(board, 0, 0, axis=0)
            board = ai.refresh_board(board)
            boards.append(board)
        
        print("screenshot", str(ss_counter))
        print(boards[-1])

        # make the move
        if swap:
            keyboard_input.press(SWAP_KEY)
            keyboard_input.release(SWAP_KEY)
        moves = moves.split()
        for i in range(int(moves[0])):
            time.sleep(0.0005)
            keyboard_input.press(ROTATE_KEY)
            keyboard_input.release(ROTATE_KEY)
        if int(moves[1]) > 0:
            for i in range(abs(int(moves[1]))):
                time.sleep(0.0005)
                keyboard_input.press(RIGHT_KEY)
                keyboard_input.release(RIGHT_KEY)
        elif int(moves[1]) < 0:
            for i in range(abs(int(moves[1]))):
                time.sleep(0.0005)
                keyboard_input.press(LEFT_KEY)
                keyboard_input.release(LEFT_KEY)
        time.sleep(0.0005)
        keyboard_input.press(DROP_KEY)
        keyboard_input.release(DROP_KEY)
        time.sleep(0.03)
        ss_counter += 1

    if end == True:
        break