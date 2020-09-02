import plot_high_score_class
import numpy as np
import board_class
import pygame
pygame.init()


# Main
# Create an instance of the HighScore class
#high_scores = plot_high_score_class.HighScore(True, 10, [10, 5], [True, False], "high_scores.pkl")

game_board = board_class.Board(8,8,10)
game_board.place_objects_in_array()
game_board.count_num_of_touching_mines()
LEFT = 1
RIGHT = 3
run = True
while run:
    left_click = False
    right_click = False
    for event in pygame.event.get():
        mouse_position = pygame.mouse.get_pos()

        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT and game_board.is_mouse_over_new_game_button(mouse_position):
            game_board.place_objects_in_array()
            game_board.count_num_of_touching_mines()
            game_board.shown_array = np.zeros((game_board.num_of_tiles_y, game_board.num_of_tiles_x), dtype=int)
            game_board.flags_array = np.zeros((game_board.num_of_tiles_y, game_board.num_of_tiles_x), dtype=int)
            game_board.hit_mine = False  #TODO: should there be any more from init?

        elif game_board.hit_mine:
            pass

        elif event.type == pygame.MOUSEBUTTONUP and (event.button == LEFT or event.button == RIGHT):
            if event.button == LEFT:
                left_click = True
            elif event.button == RIGHT:
                right_click = True
            pixel_xy = event.pos
            pixel_x = event.pos[0]
            pixel_y = event.pos[1]
            tile_xy = game_board.pixel_xy_to_tile_xy(pixel_x, pixel_y)
            tile_x = tile_xy[0]
            tile_y = tile_xy[1]
            game_board.update_game_state(tile_x, tile_y, left_click, right_click)


    game_board.update_board_for_display()
    game_board.display_game_board()
    game_board.is_game_over()
    game_board.draw_new_game_button()
    pygame.display.update()


pygame.quit()

