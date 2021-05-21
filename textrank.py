from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
import math

# from graph import LexcicalGralph

# bp = Blueprint('textrank', __name__, url_prefix="/tr")
bp = Blueprint('textrank', __name__)

MIN_TEXT_LIMIT = 50
MAX_TEXT_LIMIT = 350

NOUN_GROUP = ['NN', 'NNS', 'NNP', 'NNPS']
PRONOUN_GROUP = ['PRP', 'PRP$', 'WP', 'WP$']
VERB_GROUP = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
ADJECTIVE_GROUP = ['JJ', 'JJR', 'JJS']
ADVERB_GROUP = ['RB', 'RBR', 'RBS', 'WRB']
PREPOSITION_GROUP = ['IN']
CONJUNCTION_GROUP = ['CC', 'IN']
INTERJECTION_GROUP = ['UH']

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

def syntactic_filter(source, tag1=NOUN_GROUP, tag2=ADJECTIVE_GROUP):
    annotated_text_token = nltk.pos_tag(word_tokenize(source.lower()))
    filtered_tokens = []
    for i in range(len(annotated_text_token)):
        token = annotated_text_token[i]
        if token[1] in tag1 or token[1] in tag2:
            new_token = (i, token[0], token[1])
            filtered_tokens.append(new_token)
    return filtered_tokens

# @bp.route('/textrank', methods=('GET', 'POST'))
@bp.route('/', methods=('GET', 'POST'))
def textrank():
    if request.method == 'POST':
        source = request.form['source']
        N = request.form['window']
        error = None

        if not source:
            error = "The text is empty"
        else:
            word_cnt = len(source.split())
            if word_cnt < MIN_TEXT_LIMIT:
                error = "The text is too short"
            elif word_cnt > MAX_TEXT_LIMIT:
                error = "The text is too long"
            else:
                filtered_tokens = syntactic_filter(source)
                graph = LexicalGraph(filtered_tokens, N)
                iter_cnt = graph.calculate_textrank()
                rev_sorted_scores = sorted(graph.V.items(), key=lambda x : x[1], reverse=True)

                potential_keywords = []
                potential_keywords_score = []
                cur_score = math.inf
                for i in range(graph.T):
                    # if cur_score == rev_sorted_scores[i][1]:
                    #     break
                    # else:
                    cur_score = rev_sorted_scores[i][1]
                    word = graph.conversion[rev_sorted_scores[i][0]]
                    potential_keywords.append(word)
                    potential_keywords_score.append(cur_score)
                print(potential_keywords, potential_keywords_score)

        
        if error is not None:
            flash(error)
        else:
            return redirect(url_for('textrank.textrank'))

    return render_template('textrank/textrank.html')

# @bp.route('/result')
# def result():
#     return render_template('textrank/result.html')