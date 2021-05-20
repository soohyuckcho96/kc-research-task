from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('textrank', __name__, url_prefix="/tr")

@bp.route('/textrank', methods=('GET', 'POST'))
def textrank():
    if request.method == 'POST':
        source = request.form['source']
        error = None

        if not source:
            error = "The text is empty"
        elif len(source) > 500:
            error = "The text is too long"
        # algorithms
        if error is not None:
            flash(error)
        else:
            return redirect(url_for('textrank.textrank'))

    return render_template('textrank/textrank.html')

# @bp.route('/result')
# def result():
#     return render_template('textrank/result.html')