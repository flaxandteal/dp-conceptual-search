import os
from server.app import create_app

app = create_app()


def test():
    from subprocess import check_output
    print(
        check_output(['nosetests',
                      '-v',
                      '-s', ])
        # '--with-coverage',
        # '--cover-package=server',
        # '--cover-branches',
        # '--cover-erase',
        # '--cover-html',
        # '--cover-html-dir=cover'])
    )


def run(host, port):
    try:
        app.run(host=host, port=port, workers=1)
    except KeyboardInterrupt:
        print("Here!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        host = os.getenv("BIND_HOST", '0.0.0.0')
        post = int(os.getenv("BIND_PORT", 5000))
        run(host, post)
