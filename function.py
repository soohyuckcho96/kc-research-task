import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
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
            filtered_tokens.append((i, token[0]))
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
        if token[1] in NOUN_GROUP + ADJECTIVE_GROUP:
            new_token = (i + 1, token[0])
            filtered_tokens.append(new_token)
    return filtered_tokens

##################################################
## Multipartite ##
##################################################
def mp_filter(source):
    ps = PorterStemmer()
    annotated_text_token = nltk.pos_tag(word_tokenize(source.lower()))
    filtered_tokens = []
    for i in range(len(annotated_text_token)):
        token = annotated_text_token[i]
        if token[1] in NOUN_GROUP + ADJECTIVE_GROUP:
            new_token = (i, token[0], ps.stem(token[0]), token[1])
            filtered_tokens.append(new_token)
    return filtered_tokens

def get_candidates(filtered_tokens):
    candidate_list = []
    offset_dict = {}
    i = 0
    while i < len(filtered_tokens):
        token = filtered_tokens[i]
        curr_idx = token[0]
        curr_word = token[1]
        curr_topic = token[2]
        curr_pos = token[3]
        j = i + 1
        while j < len(filtered_tokens):
            next_token = filtered_tokens[j]
            next_idx = next_token[0]
            if curr_idx + 1 != next_idx:
                break
            else:
                curr_idx = next_idx
                curr_word += ' ' + next_token[1]
                curr_topic += ' ' + next_token[2]
                curr_pos = next_token[3]
                j += 1
        i = j
        if curr_pos in NOUN_GROUP:
            candidate_list.append((curr_idx, curr_word, curr_topic))
            if curr_word not in offset_dict:
                offset_dict[curr_word] = [curr_idx]
            else:
                offset_dict[curr_word].append(curr_idx)
    return candidate_list, offset_dict

def is_similar(target, abbr_group, topic):
    target_split = target.split()
    topic_split = topic.split()
    target_set = set(target_split)
    topic_set = set(topic_split)
    wrt_target = len(list(target_set & topic_set)) / len(target_split) > TOPIC_SIMILARITY
    wrt_topic = len(list(target_set & topic_set)) / len(topic_split) > TOPIC_SIMILARITY
    has_abbr = False
    for a in abbr_group:
        has_abbr = a in topic_split
    return wrt_target or wrt_topic or has_abbr

def get_abbreviation(text):
    abbr = ''
    for x in text.split():
        abbr += x[0]
    return abbr

def group_by_topics(candidate_list):
    topic_group_dict = {}
    first_occurence = {}
    topic_idx = 0
    flags = [False for _ in range(len(candidate_list))]
    while not all(flags):
        start_idx = min([i for i, x in enumerate(flags) if not x])
        word = candidate_list[start_idx][1]
        target = candidate_list[start_idx][2]
        topic_group = [target]
        abbr_group = []
        if len(target.split()) > 1:
            abbr_group.append(get_abbreviation(target))
        flags[start_idx] = True
        for i in range(start_idx + 1, len(candidate_list)):
            topic = candidate_list[i][2]
            if not flags[i] and is_similar(target, abbr_group, topic):
                if topic not in topic_group:
                    topic_group.append(topic)
                    if len(topic.split()) > 1:
                        abbr_group.append(get_abbreviation(topic))
                flags[i] = True
        topic_group_dict[topic_idx] = topic_group
        if topic_idx not in first_occurence:
            first_occurence[topic_idx] = word
        topic_idx += 1
    return topic_group_dict, first_occurence

def topic_assignment(candidate_list, topic_group_dict):
    topic_idx_dict = {}
    for i in range(len(topic_group_dict)):
        for j in range(len(topic_group_dict[i])):
            topic_idx_dict[topic_group_dict[i][j]] = i

    topic_assign_dict = {}
    for token in candidate_list:
        if token[1] not in topic_assign_dict:
            topic_assign_dict[token[1]] = topic_idx_dict[token[2]]

    return topic_assign_dict
