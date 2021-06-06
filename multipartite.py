from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from lexicalgraph import MPGraph
from constant import *
from function import *

bp = Blueprint('multipartite', __name__, url_prefix='/mp')

@bp.route('/', methods=('GET', 'POST'))
def multipartite():
    if request.method == 'POST':
        source = request.form['source']
        N = request.form['num']
        error = None

        if not source:
            error = "The text is empty"
        else:
            filtered_tokens = mp_filter(source)
            # print(filtered_tokens, len(filtered_tokens))
            candidate_list, offset_dict = get_candidates(filtered_tokens)
            # print(candidate_list, len(candidate_list))
            # print(offset_dict, len(offset_dict))
            topic_group_dict, first_occurence = group_by_topics(candidate_list)
            k = len(topic_group_dict)
            # print(topic_group_dict)
            print(first_occurence)
            topic_assign_dict = topic_assignment(candidate_list, topic_group_dict)
            # print(topic_assign_dict)
            graph = MPGraph(offset_dict, topic_assign_dict, first_occurence)
            # iter_cnt = graph.calculate_positionrank()
            # kp_score = {}
            # for i in range(graph.unique_cnt):
            #     kp_score[graph.conversion[i]] = graph.S[i]
            # final_keywords = get_top_n_grams(filtered_tokens, kp_score, k)

            session.clear()
            # session['iter_cnt'] = iter_cnt
            # session['final_kw'] = final_keywords

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('multipartite.multipartite'))

    return render_template('multipartite/multipartite.html')