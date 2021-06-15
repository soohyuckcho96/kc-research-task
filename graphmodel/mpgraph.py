import math

class MPGraph(object):
    def __init__(self, offset_dict, topic_assign_dict, first_occurence):
        self.unique_cnt = len(offset_dict)
        unique_words = list(offset_dict.keys())
        self.conversion = {unique_words[i] : i for i in range(self.unique_cnt)}
        self.S = {self.conversion[v] : 1 for v in unique_words}
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
        
        self.conversion = {val : key for key, val in self.conversion.items()}

    def score_of(self, i):
        temp = 0
        for j in range(self.unique_cnt):
            if self.M[j][i] != 0:
                temp += self.M[i][j] * self.S[j] / sum(self.M[j])
        return (1 - self.damping_factor) + self.damping_factor * temp

    def calculate_textrank(self):
        flags = [False for _ in range(self.unique_cnt)]
        i = 0
        iter_cnt = 0
        while not all(flags):
            prev_score = self.S[i]
            curr_score = self.score_of(i)
            self.S[i] = curr_score
            if abs(prev_score - curr_score) < self.threshold:
                flags[i] = True
            i = (i + 1) % self.unique_cnt
            if i == 0:
                iter_cnt += 1
        return iter_cnt

    def get_keyphrases(self, N):
        kw = list(sorted(self.S.items(), key=lambda x : x[1], reverse=True)[:N])
        keywords = []
        keywords_score = []
        for t in kw:
            keywords.append(self.conversion[t[0]])
            keywords_score.append(round(t[1], 4))
        return keywords, keywords_score