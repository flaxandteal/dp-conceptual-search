from server.app import create_app

app = create_app()


def run(host, port):
    try:
        app.run(host=host, port=port, workers=1)
    except KeyboardInterrupt:
        print("Here!")


if __name__ == "__main__":
    import os

    host = os.getenv("BIND_HOST", '0.0.0.0')
    post = int(os.getenv("BIND_PORT", 5000))
    run(host, post)
