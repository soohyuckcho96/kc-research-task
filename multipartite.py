from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from graphmodel.mpgraph import MPGraph
from constant import *
from function import *

bp = Blueprint('multipartite', __name__, url_prefix='/mp')

@bp.route('/', methods=('GET', 'POST'))
def multipartite():
    if request.method == 'POST':
        source = request.form['source']
        N = int(request.form['num'])
        error = None

        if not source:
            error = "The text is empty"
        else:
            filtered_tokens = mp_filter(source)
            candidate_list, offset_dict = get_candidates(filtered_tokens)
            print(candidate_list)
            print(offset_dict)
            topic_group_dict, first_occurence = group_by_topics(candidate_list)
            print(topic_group_dict)
            print(first_occurence)
            k = len(topic_group_dict)
            topic_assign_dict = topic_assignment(candidate_list, topic_group_dict)
            graph = MPGraph(offset_dict, topic_assign_dict, first_occurence)
            iter_cnt = graph.calculate_textrank()
            keyphrases, keyphrases_score = graph.get_keyphrases(N)
            kw_score = combine_and_sort(keyphrases, keyphrases_score)

            session.clear()
            session['k'] = k
            session['iter_cnt'] = iter_cnt
            session['kw_score'] = kw_score
            session['final_kw'] = keyphrases

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('multipartite.multipartite'))

    return render_template('multipartite/multipartite.html')