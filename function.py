import nltk
from nltk.tokenize import word_tokenize
from constant import *

def syntactic_filter(source, tag1=NOUN_GROUP, tag2=ADJECTIVE_GROUP):
    annotated_text_token = nltk.pos_tag(word_tokenize(source.lower()))
    filtered_tokens = []
    for i in range(len(annotated_text_token)):
        token = annotated_text_token[i]
        if token[1] in tag1 or token[1] in tag2:
            new_token = (i, token[0], token[1])
            filtered_tokens.append(new_token)
    return filtered_tokens

def combine_multi_word_keyword(potential_keywords, filtered_tokens):
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