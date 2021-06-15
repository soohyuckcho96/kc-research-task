from collections import Counter

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

    def get_top_n_grams(self, filtered_tokens, k):
        kp_score = {}
        for i in range(self.unique_cnt):
            kp_score[self.conversion[i]] = self.S[i]
        kw = {}
        i = 0
        while i < len(filtered_tokens):
            token = filtered_tokens[i]
            curr_idx = token[0]
            curr_word = token[1]
            curr_score = kp_score[curr_word]
            j = i + 1
            while j < len(filtered_tokens) and j < i + 3:
                next_token = filtered_tokens[j]
                next_idx = next_token[0]
                if curr_idx + 1 != next_idx:
                    break
                else:
                    curr_idx = next_idx
                    curr_word += ' ' + next_token[1]
                    curr_score += kp_score[next_token[1]]
                    j += 1
            i = j
            if curr_word not in kw:
                kw[curr_word] = curr_score
        kw = list(sorted(kw.items(), key=lambda x : x[1], reverse=True)[:k])
        final_keywords = []
        for t in kw:
            final_keywords.append(t[0])
        return final_keywords