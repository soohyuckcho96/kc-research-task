from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import math
from lexicalgraph import LexicalGraph
from constant import *
from function import *

# bp = Blueprint('textrank', __name__, url_prefix="/tr")
bp = Blueprint('textrank', __name__)

# @bp.route('/textrank', methods=('GET', 'POST'))
@bp.route('/', methods=('GET', 'POST'))
def textrank():
    if request.method == 'POST':
        source = request.form['source']
        N = int(request.form['window'])
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
                    cur_score = rev_sorted_scores[i][1]
                    word_idx = rev_sorted_scores[i][0]
                    word = graph.conversion[word_idx]
                    potential_keywords.append(word)
                    potential_keywords_score.append(cur_score)
                
                final_keywords = combine_multi_word_keyword(g.potential_keywords, filtered_tokens)

                session['iter_cnt'] = iter_cnt
                session['pot_kw'] = potential_keywords
                session['pot_kw_score'] = potential_keywords_score
                session['final_kw'] = final_keywords

                # print(g.iter_cnt)
                # print(g.potential_keywords)
                # print(g.potential_keywords_score)
                # print(g.final_keywords)

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('textrank.textrank'))

    return render_template('textrank/textrank.html')