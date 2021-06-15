from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from graphmodel.trgraph import TRGraph
from constant import *
from function import *

bp = Blueprint('textrank', __name__)

@bp.route('/', methods=('GET', 'POST'))
def textrank():
    if request.method == 'POST':
        source = request.form['source']
        N = int(request.form['window'])
        tag = request.form['tag']
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
                filtered_tokens = tr_filter(source, tag)
                graph = TRGraph(filtered_tokens, N)
                iter_cnt = graph.calculate_textrank()
                keywords, keywords_score = graph.get_keywords()
                final_keywords = remove_duplicate(multi_word_keyword(keywords, filtered_tokens))
                kw_score = combine_and_sort(keywords, keywords_score)

                session.clear()
                session['iter_cnt'] = iter_cnt
                session['kw_score'] = kw_score
                session['final_kw'] = final_keywords

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('textrank.textrank'))

    return render_template('textrank/textrank.html')