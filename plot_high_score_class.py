import pickle
from tkinter import *

class HighScore:

    def __init__(self, order_high_to_low, score_lines_num, column_width, align_left, filename, scores_db=[]):
        self.order_high_to_low = order_high_to_low
        self.score_lines_num = score_lines_num
        self.column_width = column_width
        self.align_left = align_left
        self.filename = filename
        self.scores_db = scores_db

        # UI attributes
        self.font = "Calibri 28"
        self.rank_label_width = 2
        self.name_label_width = 10
        self.score_label_width = 4
        self.label_height = 1
        self.background_color = "black"
        self.foreground_color = "white"
        self.pad_value = 1
        self.window_open = False

        # name entered by user
        self.player_name = None

    def add_score(self, new_score):
        # function receives new_score in the form [name, score], inserts it into the score_db in the right order
        scores_db = self.scores_db
        # add to empty list
        if not scores_db:
            scores_db.insert(0, new_score)
            return scores_db

        if self.order_high_to_low:
            # lowest score, add to end of list
            if new_score[-1] < scores_db[-1][-1]:
                scores_db.append(new_score)
                return scores_db

            # search for insertion location
            for i in range(len(scores_db)):
                curr_row = scores_db[i]
                if new_score[-1] >= curr_row[-1]:
                    scores_db.insert(i, new_score)
                    break
                else:
                    continue

        # list is ordered from low to high
        else:
            # lowest score, add to end of list
            if new_score[-1] > scores_db[-1][-1]:
                scores_db.append(new_score)
                return scores_db

            # search for insertion location
            for i in range(len(scores_db)):
                curr_row = scores_db[i]
                if new_score[-1] <= curr_row[-1]:
                    scores_db.insert(i, new_score)
                    break
                else:
                    continue

        # score_lines_num is the max number of high score lines, an argument to the function
        if len(scores_db) > self.score_lines_num:
            scores_db.pop()

        return scores_db

    def print_scores(self):
        if not self.scores_db:
            print("Empty list")
            return
        score_string = ""
        for i in range(len(self.scores_db)):
            curr_row = self.scores_db[i]
            score_string += "{0:02d} |".format(i+1)
            for j in range(len(curr_row)):
                element = str(curr_row[j])
                element = element[:self.column_width[j]]   # truncate string according to column_width
                if self.align_left[j]:
                    score_string += str(element) + (self.column_width[j] - len(element))*" " + "|"
                else:
                    score_string += (self.column_width[j] - len(element)) * " " + element
            score_string += "\n"

        print(score_string)

    def display_high_scores_window(self): # TODO: add empty high scores string
        # function creates a list for display in Tkinter window
        self.window_open = True
        high_scores_window = Toplevel()
        high_scores_window.title("High scores")

        for i in range(len(self.scores_db)):
            curr_row = self.scores_db[i]
            # RANK
            rank = "{0:02d}".format(i+1)
            rank_label = Label(high_scores_window, text=rank, bg=self.background_color, fg=self.foreground_color, font=self.font,
                               width=self.rank_label_width, height=self.label_height)
            rank_label.grid(row=i+1, column=0, padx=self.pad_value, pady=self.pad_value)

            for j in range(len(curr_row)):
                element = str(curr_row[j])
                if j == 0:
                    # NAME
                    name_label = Label(high_scores_window, text=str(element), bg=self.background_color, fg=self.foreground_color, font=self.font,
                                       width=self.name_label_width, height=self.label_height, anchor=W)
                    name_label.grid(row=i+1, column=j+1, sticky=W, padx=self.pad_value, pady=self.pad_value)
                else:
                    # SCORE
                    score_label = Label(high_scores_window, text=str(element), bg=self.background_color, fg=self.foreground_color, font=self.font,
                                        width=self.score_label_width, height=self.label_height, anchor=E)
                    score_label.grid(row=i+1, column=j+1, sticky=E, padx=self.pad_value, pady=self.pad_value)

        high_scores_window.mainloop()
        self.window_open = False

    def is_window_open(self):
        return self.window_open

    def get_user_name(self):
        # new window to get name for high scores
        name_req_window = Tk()
        player_name = Entry(name_req_window, width=50)
        player_name.pack()
        player_name.insert(0, "Enter your name: ")

        def get_user_name_str():
            self.player_name = player_name.get()
            my_label = Label(name_req_window, text=str(self.player_name))
            my_label.pack()

        get_user_name_button = Button(name_req_window, text="OK", command=get_user_name_str)
        get_user_name_button.pack()

        name_req_window.mainloop()

    # func saves score_db to file,score_db is a list of lists
    def save_scores_to_file(self):
        with open(self.filename, "wb") as score_file:
            pickle.dump(self.scores_db, score_file)

    # func loads score_db from file as a correct data struct (list of lists)
    def load_scores_from_file(self):
        with open(self.filename, "rb") as score_file:
            self.scores_db = pickle.load(score_file)
            return self.scores_db
