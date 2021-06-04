import os

from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='textrank-soohyuckcho',
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    import textrank
    app.register_blueprint(textrank.bp)
    app.add_url_rule('/', endpoint='textrank')

    import positionrank
    app.register_blueprint(positionrank.bp)

    return app