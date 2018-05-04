def create_app():
    from sanic import Sanic
    from server.search.routes import search_blueprint

    app = Sanic()
    app.blueprint(search_blueprint)
    return app
