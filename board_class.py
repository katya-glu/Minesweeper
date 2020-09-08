import numpy as np
import pygame
pygame.init()


class Board:
    mine_value = 9

    tiles = [pygame.image.load("empty.png"), pygame.image.load("one.png"), pygame.image.load("two.png"),
             pygame.image.load("three.png"), pygame.image.load("four.png"), pygame.image.load("five.png"),
             pygame.image.load("six.png"), pygame.image.load("seven.png"), pygame.image.load("eight.png"),
             pygame.image.load("mine.png"), pygame.image.load("block.png"), pygame.image.load("flagged.png"),
             pygame.image.load("new_game_unpressed.png")]

    def __init__(self, num_of_tiles_x=8, num_of_tiles_y=8, tile_width=16, tile_height=16, num_of_mines=10):
        self.num_of_tiles_x = num_of_tiles_x
        self.num_of_tiles_y = num_of_tiles_y
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
        self.shown_array = np.zeros((self.num_of_tiles_y, self.num_of_tiles_x), dtype=int)
        self.flags_array = np.zeros((self.num_of_tiles_y, self.num_of_tiles_x), dtype=int)
        self.mines_array = np.zeros((self.num_of_tiles_y, self.num_of_tiles_x), dtype=int)
        self.neighbours_array = np.zeros((self.num_of_tiles_y, self.num_of_tiles_x), dtype=int)
        self.board_array = np.zeros((self.num_of_tiles_y, self.num_of_tiles_x), dtype=int)
        self.board_for_display = np.zeros((self.num_of_tiles_y, self.num_of_tiles_x), dtype=int)
        self.new_button_icon = self.tiles[12]


    def window_init(self):
        self.window_width = self.num_of_tiles_x * self.tile_width + self.delta_from_left_x
        self.window_height = self.num_of_tiles_y * self.tile_width + self.delta_from_top_y
        window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Minesweeper")
        return window



    # function shuffles an array in order to randomly generate locations of objects in the array
    def place_objects_in_array(self):
        num_of_elements = self.num_of_tiles_x * self.num_of_tiles_y
        ones_array = np.ones(self.num_of_mines, dtype=int)
        zeros_array = np.zeros(num_of_elements - self.num_of_mines, dtype=int)
        joined_array = np.concatenate((ones_array, zeros_array))
        np.random.shuffle(joined_array)
        self.mines_array = joined_array.reshape(self.num_of_tiles_y, self.num_of_tiles_x)
        return self.mines_array

    # function receives an array with mines locations, calculates how many mines touch each empty cell
    def count_num_of_touching_mines(self):
        padded_mines_array = np.pad(self.mines_array, (1, 1))
        for y in range(1, self.num_of_tiles_y + 1):
            for x in range(1, self.num_of_tiles_x + 1):
                if padded_mines_array[y][x] == 0:
                    self.neighbours_array[y - 1][x - 1] = np.sum(
                        padded_mines_array[y - 1:y + 2, x - 1:x + 2])  # sum elements around curr position
        self.board_array = self.neighbours_array + self.mine_value * self.mines_array

    def pixel_xy_to_tile_xy(self, pixel_x, pixel_y):
        tile_x = (pixel_x - self.delta_from_left_x) // self.tile_width
        tile_y = (pixel_y - self.delta_from_top_y) // self.tile_height
        return tile_x, tile_y

    # function checks whether the input is valid - click should be on a closed tile, left click opens tile, right click
    # toggles flag display
    def is_valid_input(self, tile_x, tile_y, left_click, right_click):
        if left_click and right_click:
            return True
        if tile_x < 0 or tile_y < 0:
            return False
        if self.shown_array[tile_y][tile_x] == 1:
            return False
        if left_click:
            if self.flags_array[tile_y][tile_x] == 1:
                return False
            else:
                return True
        if right_click:
            return True

    # flood fill algorithm
    def flood_fill(self, tile_x, tile_y):
        self.shown_array[tile_y][tile_x] = 1
        flood_fill_queue = [(tile_y, tile_x)]
        while len(flood_fill_queue) != 0:
            curr_pos = flood_fill_queue.pop(0)
            curr_y = curr_pos[0]
            curr_x = curr_pos[1]
            if self.board_array[curr_y][curr_x] == 0:
                for neighbour_y in range(curr_y - 1, curr_y + 2):
                    for neighbour_x in range(curr_x - 1, curr_x + 2):
                        if (neighbour_y <= (self.num_of_tiles_y - 1) and neighbour_y >= 0) and \
                                (neighbour_x <= (self.num_of_tiles_x - 1) and neighbour_x >= 0):
                            if self.shown_array[neighbour_y][neighbour_x] == 0:
                                flood_fill_queue.append((neighbour_y, neighbour_x))
                                self.shown_array[neighbour_y][neighbour_x] = 1          # all neighbours change to shown
        return self.shown_array

    # function updates game state upon receiving valid input
    def update_game_state(self, tile_x, tile_y, left_click, right_click):
        if self.is_valid_input(tile_x, tile_y, left_click, right_click): # shown_array[tile_y][tile_x] != 1
            if left_click and right_click:
                print('left and right click: not implemented')
                pass
            elif left_click and self.board_array[tile_y][tile_x] != 0:
                self.shown_array[tile_y][tile_x] = 1
                if self.board_array[tile_y][tile_x] == 9:
                    self.hit_mine = True
            elif left_click and self.board_array[tile_y][tile_x] == 0:
                self.flood_fill(tile_x, tile_y)
            elif right_click:                                                        # right click
                self.flags_array[tile_y][tile_x] = 1 - self.flags_array[tile_y][tile_x]     # toggle flag on/off



    """
    Function updates board for display - the appropriate sprite index in tiles list is updated in board_for_display,
    based on the shown array
    """
    def update_board_for_display(self):
        for display_tile_y in range(self.num_of_tiles_y):
            for display_tile_x in range(self.num_of_tiles_x):
                curr_tile_y = display_tile_y
                curr_tile_x = display_tile_x
                if self.hit_mine and self.board_array[curr_tile_y][curr_tile_x] == 9:
                    self.board_for_display[curr_tile_y][curr_tile_x] = self.board_array[curr_tile_y][curr_tile_x]
                else:
                    if self.flags_array[curr_tile_y][curr_tile_x] == 1:
                        self.board_for_display[curr_tile_y][curr_tile_x] = 11
                    else:                                                # no flag at tile
                        if self.shown_array[curr_tile_y][curr_tile_x] == 0:
                            self.board_for_display[curr_tile_y][curr_tile_x] = 10
                        else:                                            # tile has been opened
                            self.board_for_display[curr_tile_y][curr_tile_x] = self.board_array[curr_tile_y][curr_tile_x]

    def display_game_board(self):
        for tile_y in range(self.num_of_tiles_y):
            tile_pos_y = tile_y * self.tile_height + self.delta_from_top_y
            for tile_x in range(self.num_of_tiles_x):
                tile_pos_x = tile_x * self.tile_width
                curr_elem = self.board_for_display[tile_y][tile_x]
                self.window.blit(self.tiles[curr_elem], (tile_pos_x, tile_pos_y))

    def is_game_over(self):
        font = pygame.font.SysFont("comicsans", 40)
        if self.hit_mine:
            self.game_over = True
            lose_text = font.render("You lose", True, (255, 0, 0))
            self.window.blit(lose_text, ((self.window_width - lose_text.get_width())//2, self.window_height//2))
        if (self.flags_array == self.mines_array).all():
            self.game_over = True
            self.win = True
            win_text = font.render("You win", True, (255, 0, 0))
            self.window.blit(win_text, ((self.window_width - win_text.get_width()) // 2, self.window_height // 2))

    # function draws new game button in the window
    def draw_new_game_button(self):
        self.window.blit(self.new_button_icon, ((self.window_width - self.new_button_icon.get_width())/2, 2))

    def is_mouse_over_new_game_button(self, mouse_position):
        new_game_button_x = (self.window_width - self.new_button_icon.get_width())//2
        new_game_button_y = 2
        new_game_button_width = new_game_button_x + self.new_button_icon.get_width()
        new_game_button_height = new_game_button_y + self.new_button_icon.get_height()
        if mouse_position[0] > new_game_button_x and mouse_position[0] < new_game_button_width:
            if mouse_position[1] > new_game_button_y and mouse_position[1] < new_game_button_height:
                return True
        else:
            return False
