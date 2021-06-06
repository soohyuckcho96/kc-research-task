from collections import Counter
import math

##################################################
## TextRank ##
##################################################
class TRGraph(object):
    def __init__(self, filtered_tokens, N):
        self.total_cnt = len(filtered_tokens)
        words = [t[1] for t in filtered_tokens]
        unique_words = list(Counter(words))
        self.unique_cnt = len(unique_words)
        self.T = self.unique_cnt // 3
        self.conversion = {unique_words[i] : i for i in range(self.unique_cnt)}
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
                    if token[0] + N <= next_token[0]:
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
        flags = [False for _ in range(self.unique_cnt)]
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

##################################################
## PositionRank ##
##################################################
class PRGraph(object):
    def __init__(self, filtered_tokens, w):
        self.total_cnt = len(filtered_tokens)
        words = [t[1] for t in filtered_tokens]
        unique_words = list(Counter(words))
        self.unique_cnt = len(unique_words)
        self.conversion = {unique_words[i] : i for i in range(self.unique_cnt)}
        self.S = [1 / self.unique_cnt for _ in range(self.unique_cnt)]
        self.E = {self.conversion[v] : [] for v in unique_words}
        self.M = [[0 for _ in range(self.unique_cnt)] for _ in range(self.unique_cnt)]
        self.alpha = 0.85
        self.threshold = 0.001

        for i in range(self.total_cnt):
            token = filtered_tokens[i]
            for j in range(w):
                if i + j + 1 >= self.total_cnt:
                    break
                else:
                    next_token = filtered_tokens[i + j + 1]
                    if token[0] + w <= next_token[0]:
                        break
                    else:
                        idx = self.conversion[token[1]]
                        next_idx = self.conversion[next_token[1]]
                        if next_idx not in self.E[idx]:
                            self.E[idx].append(next_idx)
                            self.E[next_idx].append(idx)
                        self.M[idx][next_idx] += 1
                        self.M[next_idx][idx] += 1
        
        # self.M_tilde = [[0 for j in range(self.unique_cnt)] for i in range(self.unique_cnt)]
        # for i in range(self.unique_cnt):
        #     row_sum = sum(self.M[i])
        #     if row_sum != 0:
        #         for j in range(self.unique_cnt):
        #             self.M_tilde[i][j] = self.M[i][j] / row_sum
        
        self.p_tilde = [0 for _ in range(self.unique_cnt)]
        for i in range(self.total_cnt):
            token = filtered_tokens[i]
            idx = self.conversion[token[1]]
            self.p_tilde[idx] += 1 / token[0]
        row_sum = sum(self.p_tilde)
        for i in range(self.unique_cnt):
            self.p_tilde[i] /= row_sum

        self.conversion = {val : key for key, val in self.conversion.items()}
    
    def score_of(self, i):
        temp = 0
        for j in self.E[i]:
            temp += self.M[i][j] / sum(self.M[j])
        return (1 - self.alpha) * self.p_tilde[i] + self.alpha * temp * self.S[i]

    def calculate_positionrank(self):
        flags = [False for _ in range(self.unique_cnt)]
        i = 0
        iter_cnt = 0
        while not all(flags) and iter_cnt < 100:
            prev_score = self.S[i]
            curr_score = self.score_of(i)
            self.S[i] = curr_score
            if abs(prev_score - curr_score) < self.threshold:
                flags[i] = True
            i = (i + 1) % self.unique_cnt
            if i == 0:
                iter_cnt += 1
        return iter_cnt

##################################################
## Multipartite ##
##################################################
class MPGraph(object):
    def __init__(self, offset_dict, topic_assign_dict, first_occurence):
        self.unique_cnt = len(offset_dict)
        unique_words = list(offset_dict.keys())
        self.conversion = {unique_words[i] : i for i in range(self.unique_cnt)}
        self.V = {self.conversion[v] : 1 for v in unique_words}
        self.M = [[0 for _ in range(self.unique_cnt)] for _ in range(self.unique_cnt)]
        self.alpha = 1.1
        self.damping_factor = 0.85
        self.threshold = 0.0001

        for i in range(self.unique_cnt):
            word_i = unique_words[i]
            for j in range(i + 1, self.unique_cnt):
                word_j = unique_words[j]
                if topic_assign_dict[word_i] != topic_assign_dict[word_j]:
                    weight = 0
                    for p_i in offset_dict[word_i]:
                        for p_j in offset_dict[word_j]:
                            weight += 1 / abs(p_i - p_j)
                    self.M[i][j] = weight
                    self.M[j][i] = weight

        for i in range(len(first_occurence)):
            word_i = first_occurence[i]
            i_idx = self.conversion[word_i]
            for j in range(len(first_occurence)):
                if i == j:
                    continue
                word_j = first_occurence[j]
                j_idx = self.conversion[word_j]
                p_i = offset_dict[word_i][0]
                temp = 0
                for k in range(self.unique_cnt):
                    word_k = unique_words[k]
                    if topic_assign_dict[word_j] == topic_assign_dict[word_k] and word_j != word_k:
                        temp += self.M[k][i_idx]
                self.M[i_idx][j_idx] += self.alpha * math.exp(1 / p_i) * temp