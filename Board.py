import numpy as np
import pygame
import time


class Board:
    # shown array constants
    HIDDEN = 0
    SHOWN = 1

    # flags array constants
    # NO_FLAG = 0
    FLAGGED = 1

    # board for display constants
    TILE_EMPTY = 0
    # TWO-EIGHT = 2-8
    TILE_MINE = 9
    TILE_BLOCKED = 10
    TILE_FLAG = 11
    LOSING_MINE_RED = 13

    NEW_GAME_BUTTON = 12

    # list of tiles images. displayed according to index (value in board_for_display array)
    tiles = [pygame.image.load("empty.png"), pygame.image.load("one.png"), pygame.image.load("two.png"),
             pygame.image.load("three.png"), pygame.image.load("four.png"), pygame.image.load("five.png"),
             pygame.image.load("six.png"), pygame.image.load("seven.png"), pygame.image.load("eight.png"),
             pygame.image.load("mine.png"), pygame.image.load("block.png"), pygame.image.load("flagged.png"),
             pygame.image.load("new_game_unpressed.png"), pygame.image.load("mine_red.png")]

    def __init__(self, size_index, num_of_tiles_x, num_of_tiles_y, num_of_mines, tile_width=16, tile_height=16):
        pygame.init()
        self.size_index = size_index  # 0=small, 1=medium, 2=large
        self.num_of_tiles_x = num_of_tiles_x
        self.num_of_tiles_y = num_of_tiles_y
        self.board_shape = (num_of_tiles_y, num_of_tiles_x)
        self.num_of_mines = num_of_mines
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.delta_from_left_x = 0
        self.delta_from_top_y = 30
        self.window_width = 0
        self.window_height = 0
        self.window = self.window_init()
        self.board_init()

    def board_init(self):
        self.hit_mine = False
        self.game_over = False
        self.win = False
        self.add_score = False
        self.game_started = False
        self.game_start_time = 0
        self.time = 0
        self.clock_font = pygame.font.SysFont("comicsans", 30)
        self.shown_array = np.zeros(self.board_shape, dtype=int)
        self.flags_array = np.zeros(self.board_shape, dtype=int)
        self.mines_array = np.zeros(self.board_shape, dtype=int)
        self.neighbours_array = np.zeros(self.board_shape, dtype=int)
        self.board_array = np.zeros(self.board_shape, dtype=int)
        self.board_for_display = np.zeros(self.board_shape, dtype=int)
        self.new_button_icon = self.tiles[self.NEW_GAME_BUTTON]

    def window_init(self):
        self.window_width = self.num_of_tiles_x * self.tile_width + self.delta_from_left_x
        self.window_height = self.num_of_tiles_y * self.tile_width + self.delta_from_top_y
        window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Minesweeper")
        return window

    def place_objects_in_array(self):
        # function shuffles an array in order to randomly generate locations of objects in the array
        num_of_elements = self.num_of_tiles_x * self.num_of_tiles_y
        ones_array = np.ones(self.num_of_mines, dtype=int)
        zeros_array = np.zeros(num_of_elements - self.num_of_mines, dtype=int)
        joined_array = np.concatenate((ones_array, zeros_array))
        np.random.shuffle(joined_array)
        self.mines_array = joined_array.reshape(self.board_shape)
        return self.mines_array  # TODO: remove return, not necessary

    def count_num_of_touching_mines(self):
        # function receives an array with mines locations, calculates how many mines touch each empty cell
        padded_mines_array = np.pad(self.mines_array, (1, 1))
        for y in range(1, self.num_of_tiles_y + 1):
            for x in range(1, self.num_of_tiles_x + 1):
                if padded_mines_array[y][x] == 0:
                    self.neighbours_array[y - 1][x - 1] = np.sum(
                        padded_mines_array[y - 1:y + 2, x - 1:x + 2])  # sum elements around curr position
        self.board_array = self.neighbours_array + self.TILE_MINE * self.mines_array

    def pixel_xy_to_tile_xy(self, pixel_x, pixel_y):
        tile_x = (pixel_x - self.delta_from_left_x) // self.tile_width
        tile_y = (pixel_y - self.delta_from_top_y) // self.tile_height
        return tile_x, tile_y

    def is_valid_input(self, tile_x, tile_y, left_click, right_click):
        """
        function checks whether the input is valid - click should be on a closed tile, left click opens tile, right
        click toggles flag display
        """
        if left_click and right_click:  # TODO: add functionality for incorrectly marked flags(lose)
            if self.shown_array[tile_y][tile_x] == self.SHOWN:
                padded_flags_array = np.pad(self.flags_array, (1, 1))
                padded_tile_x = tile_x + 1
                padded_tile_y = tile_y + 1
                num_of_flags_in_sub_array = np.sum(padded_flags_array[padded_tile_y - 1:padded_tile_y + 2,
                                                   padded_tile_x - 1:padded_tile_x + 2])
                if self.board_array[tile_y][tile_x] == num_of_flags_in_sub_array:
                    return True
                else:
                    return False
        if tile_x < 0 or tile_y < 0:
            return False
        if self.shown_array[tile_y][tile_x] == self.SHOWN:
            return False
        if left_click and not right_click:
            if self.flags_array[tile_y][tile_x] == self.FLAGGED:
                return False
            else:
                return True
        if right_click and not left_click:
            return True

    def flood_fill(self, tile_x, tile_y, left_and_right_click):
        # flood fill algorithm - https://en.wikipedia.org/wiki/Flood_fill
        # func is being called only if the opened tile is empty
        flood_fill_queue = []
        if left_and_right_click:
            y_start = max(tile_y - 1, 0)
            y_end = min(tile_y + 2, self.num_of_tiles_y)
            x_start = max(tile_x - 1, 0)
            x_end = min(tile_x + 2, self.num_of_tiles_x)
            for curr_tile_y in range(y_start, y_end):  # TODO: switch to numpy operation
                for curr_tile_x in range(x_start, x_end):
                    self.shown_array[curr_tile_y][curr_tile_x] = self.SHOWN
                    flood_fill_queue.append((curr_tile_y, curr_tile_x))
        else:
            self.shown_array[tile_y][tile_x] = self.SHOWN
            flood_fill_queue = [(tile_y, tile_x)]
        while len(flood_fill_queue) != 0:
            curr_pos = flood_fill_queue.pop(0)
            curr_y = curr_pos[0]
            curr_x = curr_pos[1]
            if self.board_array[curr_y][curr_x] == self.TILE_EMPTY:
                for neighbour_y in range(curr_y - 1, curr_y + 2):
                    for neighbour_x in range(curr_x - 1, curr_x + 2):
                        if (neighbour_y <= (self.num_of_tiles_y - 1) and neighbour_y >= 0) and \
                                (neighbour_x <= (self.num_of_tiles_x - 1) and neighbour_x >= 0):
                            if self.shown_array[neighbour_y][neighbour_x] == self.HIDDEN:
                                flood_fill_queue.append((neighbour_y, neighbour_x))
                                self.shown_array[neighbour_y][
                                    neighbour_x] = self.SHOWN  # all neighbours change to shown
        return self.shown_array

    def update_game_state(self, tile_x, tile_y, left_click, right_click):
        # function updates game state upon receiving valid input
        if self.is_valid_input(tile_x, tile_y, left_click, right_click):  # shown_array[tile_y][tile_x] == self.HIDDEN
            if left_click and right_click:
                padded_flags_array = np.pad(self.flags_array, (1, 1))
                padded_mines_array = np.pad(self.mines_array, (1, 1))
                padded_tile_x = tile_x + 1
                padded_tile_y = tile_y + 1
                if (padded_flags_array[padded_tile_y - 1:padded_tile_y + 2, padded_tile_x - 1:padded_tile_x + 2]
                        == padded_mines_array[padded_tile_y - 1:padded_tile_y + 2, padded_tile_x - 1:padded_tile_x + 2]).all():
                    y_start = max(tile_y - 1, 0)
                    y_end = min(tile_y + 2, self.num_of_tiles_y)
                    x_start = max(tile_x - 1, 0)
                    x_end = min(tile_x + 2, self.num_of_tiles_x)
                    for curr_tile_y in range(y_start, y_end):  # TODO: switch to numpy operation
                        for curr_tile_x in range(x_start, x_end):
                            self.shown_array[curr_tile_y][curr_tile_x] = self.SHOWN
                    self.flood_fill(tile_x, tile_y, True)
                else:
                    self.hit_mine = True
            elif left_click and self.board_array[tile_y][tile_x] != self.TILE_EMPTY:
                self.shown_array[tile_y][tile_x] = self.SHOWN
                if self.board_array[tile_y][tile_x] == self.TILE_MINE:
                    self.hit_mine = True
                    self.board_array[tile_y][tile_x] = self.LOSING_MINE_RED
            elif left_click and self.board_array[tile_y][tile_x] == self.TILE_EMPTY:
                self.flood_fill(tile_x, tile_y, False)
            elif right_click:  # right click
                self.flags_array[tile_y][tile_x] = self.FLAGGED - self.flags_array[tile_y][tile_x]  # toggle flag on/off

    def update_board_for_display(self):
        """
        Function updates board for display - the appropriate sprite index in tiles list is updated in board_for_display,
        based on the shown array
        """
        for display_tile_y in range(self.num_of_tiles_y):
            for display_tile_x in range(self.num_of_tiles_x):
                curr_tile_y = display_tile_y
                curr_tile_x = display_tile_x

                # updating flags
                if self.flags_array[curr_tile_y][curr_tile_x] == self.FLAGGED:
                    self.board_for_display[curr_tile_y][curr_tile_x] = self.TILE_FLAG

                # updating mines, in case of losing
                elif self.hit_mine and self.board_array[curr_tile_y][curr_tile_x] == self.TILE_MINE:
                    self.board_for_display[curr_tile_y][curr_tile_x] = self.board_array[curr_tile_y][curr_tile_x]

                # updating blocks (hidden tiles)
                elif self.shown_array[curr_tile_y][curr_tile_x] == self.HIDDEN:
                    self.board_for_display[curr_tile_y][curr_tile_x] = self.TILE_BLOCKED

                # updating numbers
                else:  # tile has been opened
                    self.board_for_display[curr_tile_y][curr_tile_x] = self.board_array[curr_tile_y][curr_tile_x]

    def display_game_board(self):
        # background
        background_color = (0, 0, 0)
        self.window.fill(background_color)

        # display new game button
        self.window.blit(self.new_button_icon,
                         ((self.window_width - self.new_button_icon.get_width()) / 2, 2))  # TODO: remove magic number

        # display clock
        clock_text = self.clock_font.render('{0:03d}'.format(self.time), False, (255, 255, 255))
        self.window.blit(clock_text, (self.window_width - (clock_text.get_width() + 5), 5))  # TODO: remove magic number

        # display board
        for tile_y in range(self.num_of_tiles_y):
            tile_pos_y = tile_y * self.tile_height + self.delta_from_top_y
            for tile_x in range(self.num_of_tiles_x):
                tile_pos_x = tile_x * self.tile_width
                curr_elem = self.board_for_display[tile_y][tile_x]
                self.window.blit(self.tiles[curr_elem], (tile_pos_x, tile_pos_y))

    def update_clock(self):
        if self.game_started and self.time < 999 and not self.game_over:
            # print(self.is_game_over())
            curr_time = time.time()
            time_from_start = int(curr_time - self.game_start_time)
            self.time = time_from_start

    def is_game_over(self):
        font = pygame.font.SysFont("comicsans", 40)
        if self.hit_mine:
            self.game_over = True  # TODO: check if this is used, if not - remove
            lose_text = font.render("You lose", True, (255, 0, 0))
            self.window.blit(lose_text, ((self.window_width - lose_text.get_width()) // 2, self.window_height // 2))
        if (self.flags_array == self.mines_array).all():
            self.game_over = True  # TODO: check if this is used, if not - remove
            win_text = font.render("You win", True, (255, 0, 0))
            self.window.blit(win_text, ((self.window_width - win_text.get_width()) // 2, self.window_height // 2))
            if not self.win:
                self.win = True
                self.add_score = True

    def is_mouse_over_new_game_button(self, mouse_position):
        # function decides whether the mouse is located over the new game button
        new_game_button_x = (self.window_width - self.new_button_icon.get_width()) // 2
        new_game_button_y = 2
        new_game_button_width = new_game_button_x + self.new_button_icon.get_width()
        new_game_button_height = new_game_button_y + self.new_button_icon.get_height()
        if mouse_position[0] > new_game_button_x and mouse_position[0] < new_game_button_width:
            if mouse_position[1] > new_game_button_y and mouse_position[1] < new_game_button_height:
                return True
        else:
            return False
