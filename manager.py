def test():
    from subprocess import check_output
    print(
        check_output(['nosetests',
                      '-v',
                      '-s',
                      '--exclude-dir=./tests/integration'])
        # '--with-coverage',
        # '--cover-package=server',
        # '--cover-branches',
        # '--cover-erase',
        # '--cover-html',
        # '--cover-html-dir=cover'])
    )


def run(app_host: str='0.0.0.0', app_port: int=5000, app_workers: int=1):
    from server.app import create_app

    # Create the app
    app = create_app()
    # Run the server
    app.run(host=app_host, port=app_port, workers=app_workers)


if __name__ == "__main__":
    import os
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        host = os.getenv("BIND_HOST", '0.0.0.0')
        post = int(os.getenv("BIND_PORT", 5000))
        run(app_host=host, app_port=post)
