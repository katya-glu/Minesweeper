from plot_high_score_class import HighScore
from tkinter import *
from tkinter import messagebox
from Board import Board
import pygame
import time
pygame.init()


# board size constants
num_of_tiles_x_small_board = 8
num_of_tiles_y_small_board = 8
num_of_mines_small_board = 8

num_of_tiles_x_medium_board = 13
num_of_tiles_y_medium_board = 15
num_of_mines_medium_board = 40

num_of_tiles_x_large_board = 30
num_of_tiles_y_large_board = 16
num_of_mines_large_board = 99


def get_board_size(size_str):
    # function gets size_str from open_opening_window func in game_class file
    board_shape_dict = {
        "Small":  (num_of_tiles_x_small_board, num_of_tiles_y_small_board, num_of_mines_small_board),
        "Medium": (num_of_tiles_x_medium_board, num_of_tiles_y_medium_board, num_of_mines_medium_board),
        "Large":  (num_of_tiles_x_large_board, num_of_tiles_y_large_board, num_of_mines_large_board)
                       }

    for key in board_shape_dict:
        if size_str == key:
            return board_shape_dict[key]

def open_opening_window():   # TODO: add comments
    # Create an instance of the HighScore class
    high_scores = HighScore(True, 10, [10, 5], [True, False], "high_scores.pkl")

    opening_window = Tk()
    opening_window.title("Opening window")

    MODES = [("Small", "Small"), ("Medium","Medium"), ("Large", "Large")]
    board_size = StringVar()
    board_size.set("Small")

    for mode, size in MODES:
        Radiobutton(opening_window, text=mode, variable=board_size, value=size).pack()

    def start_new_game():
        board_size_str = board_size.get()
        size_index = 0
        for mode in MODES:
            if board_size_str == mode[0]:
                size_index = MODES.index(mode)

        board_size_and_num_of_mines = get_board_size(board_size_str)
        num_of_tiles_x = board_size_and_num_of_mines[0]
        num_of_tiles_y = board_size_and_num_of_mines[1]
        num_of_mines = board_size_and_num_of_mines[2]
        opening_window.destroy()
        main(size_index, num_of_tiles_x, num_of_tiles_y, num_of_mines)
        open_opening_window()

    def open_high_scores():
        if not high_scores.is_window_open():
            high_scores.load_scores_from_file()
            high_scores.display_high_scores_window()

    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            opening_window.destroy()

    start_game_button = Button(opening_window, text="Start game", command=start_new_game)
    start_game_button.pack()

    high_scores_button = Button(opening_window, text="High scores", command=open_high_scores)
    high_scores_button.pack()

    opening_window.protocol("WM_DELETE_WINDOW", on_closing)
    opening_window.mainloop()

def add_high_score(game_board, score, size_index):
    high_scores = HighScore(False, 10, [10, 5], [True, False], "high_scores.pkl")
    high_scores.add_new_high_score(score, size_index)
    game_board.add_score = False

def main(size_index, num_of_tiles_x, num_of_tiles_y, num_of_mines):  # TODO: add comments
    game_board = Board(size_index, num_of_tiles_x, num_of_tiles_y, num_of_mines)
    game_board.place_objects_in_array()
    game_board.count_num_of_touching_mines()
    left_pressed = False
    right_pressed = False
    LEFT = 1
    RIGHT = 3
    run = True
    while run:
        left_released = False
        right_released = False
        for event in pygame.event.get():
            mouse_position = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT and game_board.is_mouse_over_new_game_button(mouse_position):
                game_board.board_init()
                game_board.place_objects_in_array()
                game_board.count_num_of_touching_mines()
                left_pressed = False
                right_pressed = False

            # if player hits a mine (loses), the game board freezes, not allowing further tile opening
            elif game_board.hit_mine:
                pass

            # detection of mouse button press, for implementation of right and left click in the future
            elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == LEFT or event.button == RIGHT):
                if event.button == LEFT:
                    left_pressed = True
                if event.button == RIGHT:
                    right_pressed = True


            elif event.type == pygame.MOUSEBUTTONUP and (event.button == LEFT or event.button == RIGHT):
                """
                detection of mouse button release, game state will be updated once mouse button is released. Preparation for 
                left and right click in the future
                """
                if left_pressed and not right_pressed:
                    left_released = True
                    #print("only left released")
                if right_pressed and not left_pressed:
                    right_released = True
                    #print("only right released")
                if right_pressed and left_pressed:
                    left_released = True
                    right_released = True
                    #print("both released")

                pixel_x = event.pos[0]
                pixel_y = event.pos[1]
                tile_xy = game_board.pixel_xy_to_tile_xy(pixel_x, pixel_y)
                tile_x = tile_xy[0]
                tile_y = tile_xy[1]

                # game state is updated according to the pressed button
                if (left_released or right_released):
                    if not game_board.game_started and left_released and not right_released:
                        game_board.game_start_time = time.time()
                        game_board.game_started = True
                    game_board.update_game_state(tile_x, tile_y, left_released, right_released)
                    left_pressed = False
                    right_pressed = False


        game_board.update_board_for_display()
        game_board.display_game_board()
        if game_board.add_score:        # TODO: fix bug - when pygame and highscore windows are open, if X is pressed in pygame win, all windows get stuck.
            # TODO: Detect click outside window from display HS func
            add_high_score(game_board, game_board.time, game_board.size_index)
        game_board.is_game_over()
        game_board.update_clock()
        pygame.display.update()


    pygame.quit()


open_opening_window()














