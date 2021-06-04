from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from lexicalgraph import PRGraph
from constant import *
from function import *

bp = Blueprint('positionrank', __name__, url_prefix='/pr')

@bp.route('/', methods=('GET', 'POST'))
def positionrank():
    if request.method == 'POST':
        source = request.form['source']
        N = int(request.form['window'])
        k = int(request.form['num'])
        error = None

        if not source:
            error = "The text is empty"
        else:
            word_cnt = len(source.split())
            # if word_cnt < MIN_TEXT_LIMIT:
            #     error = "The text is too short"
            # elif word_cnt > MAX_TEXT_LIMIT:
            #     error = "The text is too long"
            # else:
            # filtered_tokens = syntactic_filter(source)
            filtered_tokens = pr_filter(source)
            print(filtered_tokens)
            graph = PRGraph(filtered_tokens, N, k)
            # iter_cnt = graph.calculate_textrank()
            # rev_sorted_scores = sorted(graph.V.items(), key=lambda x : x[1], reverse=True)
            # potential_keywords, potential_keywords_score = graph.get_potentials(rev_sorted_scores)                
            # final_keywords = remove_duplicate(multi_word_keyword(potential_keywords, filtered_tokens))
            # kw_score = combine_and_sort(potential_keywords, potential_keywords_score)

            # session.clear()
            # session['iter_cnt'] = iter_cnt
            # session['kw_score'] = kw_score
            # session['final_kw'] = final_keywords

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('positionrank.positionrank'))

    return render_template('positionrank/positionrank.html')