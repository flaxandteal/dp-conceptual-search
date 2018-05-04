from server.app import create_app

app = create_app()


def run():
    app.run(host='0.0.0.0', port=5050)


if __name__ == "__main__":
    app.run()
