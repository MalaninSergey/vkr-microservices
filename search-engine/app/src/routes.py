from modules.hello_world import search_bp


def route(app):
    app.register_blueprint(search_bp)
