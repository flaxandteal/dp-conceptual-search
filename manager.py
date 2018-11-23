import os
import sys
from subprocess import check_output

from dp_conceptual_search.app.app import create_app
from dp4py_sanic.api.protocol.ons_http_protocol import ONSHttpProtocol


def test():
    """
    Launches unit tests
    :return:
    """
    print(
        check_output(['nosetests',
                      '-v',
                      '-s',
                      'unit/',
                      '--exclude-dir=./unit/integration',
                      '--exclude-dir=./unit/regression'])
    )


def run(app_host: str='0.0.0.0', app_port: int=5000, app_workers: int=1):
    """
    Runs the Sanic api on the given host and port address.
    :param app_host:
    :param app_port:
    :param app_workers: Number of worker threads to use (defaults to 1)
    :return:
    """
    # Create the app
    app = create_app()
    # Run the api with our custom HttpProtocol (for more control over access log)
    app.run(host=app_host, port=app_port, workers=app_workers, protocol=ONSHttpProtocol)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        host = os.getenv("BIND_HOST", '0.0.0.0')
        port = int(os.getenv("BIND_PORT", 5000))
        workers = int(os.getenv("SANIC_WORKERS", 1))
        run(app_host=host, app_port=port, app_workers=workers)
