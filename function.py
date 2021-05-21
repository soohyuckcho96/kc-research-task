import nltk
from nltk.tokenize import word_tokenize
from constant import *

def syntactic_filter(source, tag):
    annotated_text_token = nltk.pos_tag(word_tokenize(source.lower()))
    filtered_tokens = []
    if tag == 'all':
        for i in range(len(annotated_text_token)):
            token = annotated_text_token[i]
            if token[1] in NOUN_GROUP or token[1] in VERB_GROUP or token[1] in ADJECTIVE_GROUP or token[1] in ADVERB_GROUP:
                new_token = (i, token[0], token[1])
                filtered_tokens.append(new_token)
    elif tag == 'n':
        for i in range(len(annotated_text_token)):
            token = annotated_text_token[i]
            if token[1] in NOUN_GROUP:
                new_token = (i, token[0], token[1])
                filtered_tokens.append(new_token)
    elif tag == 'nv':
        for i in range(len(annotated_text_token)):
            token = annotated_text_token[i]
            if token[1] in NOUN_GROUP or token[1] in VERB_GROUP:
                new_token = (i, token[0], token[1])
                filtered_tokens.append(new_token)
    else: # tag == 'nj'
        for i in range(len(annotated_text_token)):
            token = annotated_text_token[i]
            if token[1] in NOUN_GROUP or token[1] in ADJECTIVE_GROUP:
                new_token = (i, token[0], token[1])
                filtered_tokens.append(new_token)
    return filtered_tokens

def multi_word_keyword(potential_keywords, filtered_tokens):
    relation = [t for t in filtered_tokens if t[1] in potential_keywords]
    keywords = []
    i = 0
    while i < len(relation):
        idx = relation[i][0]
        keyword = relation[i][1]
        flag = True
        j = i + 1
        while flag and j < len(relation):
            next_idx = relation[j][0]
            if next_idx == idx + 1:
                keyword += ' ' + relation[j][1]
                idx = next_idx
                j += 1
            else:
                flag = False
        i = j
        if keyword not in keywords:
            keywords.append(keyword)
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
