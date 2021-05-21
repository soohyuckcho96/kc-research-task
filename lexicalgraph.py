from collections import Counter
import math

class LexicalGraph(object):
    def __init__(self, filtered_tokens, N):
        self.total_cnt = len(filtered_tokens)
        words = [t[1] for t in filtered_tokens]
        unique_words = list(Counter(words))
        self.unique_cnt = len(unique_words)
        self.T = self.unique_cnt // 3
        self.conversion = {unique_words[i] : i for i in range(len(unique_words))}
        self.V = {self.conversion[v] : 1 for v in unique_words}
        self.E = {self.conversion[v] : [] for v in unique_words}
        self.jump_factor = 0.85
        self.threshold = 0.0001

        for i in range(self.total_cnt):
            token = filtered_tokens[i]
            for j in range(N):
                if i + j + 1 >= self.total_cnt:
                    break
                else:
                    next_token = filtered_tokens[i + j + 1]
                    if token[0] + N < next_token[0]:
                        break
                    else:
                        idx = self.conversion[token[1]]
                        next_idx = self.conversion[next_token[1]]
                        if next_idx not in self.E[idx]:
                            self.E[idx].append(next_idx)
                            self.E[next_idx].append(idx)

        self.conversion = {v : k for k, v in self.conversion.items()}
        
    def score_of(self, word):
        neighbor_list = self.E[word]
        temp = 0
        for neighbor in neighbor_list:
            temp += self.V[neighbor] / len(self.E[neighbor])
        return (1 - self.jump_factor) + self.jump_factor * temp

    def calculate_textrank(self):
        flags = [False for i in range(self.unique_cnt)]
        i = 0
        iter_cnt = 0
        while not all(flags):
            prev_score = self.V[i]
            curr_score = self.score_of(i)
            self.V[i] = curr_score
            if abs(prev_score - curr_score) < self.threshold:
                flags[i] = True
            i = (i + 1) % self.unique_cnt
            if i == 0:
                iter_cnt += 1
        return iter_cnt

    def get_potentials(self, rev_sorted_scores):
        potential_keywords = []
        potential_keywords_score = []
        cur_score = math.inf
        for i in range(self.T):
            cur_score = rev_sorted_scores[i][1]
            word = self.conversion[rev_sorted_scores[i][0]]
            potential_keywords.append(word)
            potential_keywords_score.append(round(cur_score, 4))
        return potential_keywords, potential_keywords_score