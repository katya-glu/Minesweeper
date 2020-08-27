import pickle


class HighScore:

    def __init__(self, order_high_to_low, score_lines_num, column_width, align_left, filename, scores_db=[]):
        self.order_high_to_low = order_high_to_low
        self.score_lines_num = score_lines_num
        self.column_width = column_width
        self.align_left = align_left
        self.filename = filename
        self.scores_db = scores_db

    # function receives new_score in the form [name, score], inserts it into the score_db in the right order
    def add_score(self, new_score):
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
                if self.align_left[j]:
                    score_string += str(element) + (self.column_width[j] - len(element))*" " + "|"
                else:
                    score_string += (self.column_width[j] - len(element)) * " " + element
            score_string += "\n"

        print(score_string)

    # func saves score_db to file,score_db is a list of lists
    def save_scores_to_file(self):
        with open(self.filename, "wb") as score_file:
            pickle.dump(self.scores_db, score_file)

    # func loads score_db from file as a correct data struct (list of lists)
    def load_scores_from_file(self):
        with open(self.filename, "rb") as score_file:
            self.scores_db = pickle.load(score_file)
            return self.scores_db
