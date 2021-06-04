import nltk
from nltk.tokenize import word_tokenize
from constant import *

##################################################
## TextRank ##
##################################################
def tr_filter(source, tag):
    annotated_text_token = nltk.pos_tag(word_tokenize(source.lower()))
    filtered_tokens = []
    pos_group = []
    if tag == 'all':
        pos_group = NOUN_GROUP + VERB_GROUP + ADJECTIVE_GROUP + ADVERB_GROUP
    elif tag == 'n':
        pos_group = NOUN_GROUP
    elif tag == 'nv':
        pos_group = NOUN_GROUP + VERB_GROUP
    else: # tag == 'nj'
        pos_group = NOUN_GROUP + ADJECTIVE_GROUP
    for i in range(len(annotated_text_token)):
        token = annotated_text_token[i]
        if token[1] in pos_group:
            filtered_tokens.append((i, token[0], token[1]))
    return filtered_tokens

def multi_word_keyword(potential_keywords, filtered_tokens):
    relation = [t for t in filtered_tokens if t[1] in potential_keywords]
    keywords = []
    i = 0
    while i < len(relation):
        idx = relation[i][0]
        keyword = relation[i][1]
        j = i + 1
        while j < len(relation):
            next_idx = relation[j][0]
            if next_idx != idx + 1:
                break
            else:
                keyword += ' ' + relation[j][1]
                idx = next_idx
                j += 1
        i = j
        if keyword not in keywords:
            keywords.append(keyword)
    return keywords

def remove_duplicate(keywords):
    single = []
    multi = []
    for kw in keywords:
        if len(kw.split()) > 1:
            multi.append(kw)
        else:
            single.append(kw)
    for s in single:
        for m in multi:
            if s in m:
                keywords.remove(s)
                break
    return keywords

def combine_and_sort(potential_keywords, potential_keywords_score):
    min_val = min(potential_keywords_score)
    max_val = max(potential_keywords_score)
    def f(x):
        return 2 * (x - min_val) / (max_val - min_val) + 1

    kw_score = []
    for i in range(len(potential_keywords)):
        kw = potential_keywords[i]
        score = potential_keywords_score[i]
        ts = round(f(score), 2)
        kw_score.append((kw, score, ts))
    return sorted(kw_score, key=lambda x : x[0])

##################################################
## PositionRank ##
##################################################
def pr_filter(source):
    annotated_text_token = nltk.pos_tag(word_tokenize(source.lower()))
    filtered_tokens = []
    for i in range(len(annotated_text_token)):
        token = annotated_text_token[i]
        if token[1] in NOUN_GROUP or token[1] in ADJECTIVE_GROUP:
            new_token = (i + 1, token[0], token[1])
            filtered_tokens.append(new_token)
    return filtered_tokens

def get_top_n_grams(filtered_tokens, kp_score, k):
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

##################################################
## Multipartite ##
##################################################
