from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from graphmodel.prgraph import PRGraph
from function import *

bp = Blueprint('positionrank', __name__, url_prefix='/pr')

@bp.route('/', methods=('GET', 'POST'))
def positionrank():
    if request.method == 'POST':
        source = request.form['source']
        w = int(request.form['window'])
        k = int(request.form['num'])
        error = None

        if not source:
            error = "The text is empty"
        else:
            filtered_tokens = pr_filter(source)
            graph = PRGraph(filtered_tokens, w)
            iter_cnt = graph.calculate_positionrank()
            final_keywords = graph.get_top_n_grams(filtered_tokens, k)

            session.clear()
            session['iter_cnt'] = iter_cnt
            session['final_kw'] = final_keywords

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('positionrank.positionrank'))

    return render_template('positionrank/positionrank.html')