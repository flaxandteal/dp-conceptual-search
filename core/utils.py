class ServiceUnavailableException(Exception):
    def __init__(self, *args, **kwargs):
        super(ServiceUnavailableException, self).__init__(*args, **kwargs)


def service_is_available(host: str, port: int):
    """
    Simple wrapper for below function which returns a boolean
    :param host:
    :param port:
    :return:
    """
    try:
        throw_if_service_unavailable(host, port)
    except ServiceUnavailableException:
        return False
    return True


def check_for_connection_error(host: str, port: int):
    """

    :param host:
    :param port:
    :return:
    """
    try:
        throw_if_service_unavailable(host, port)
        return None
    except ServiceUnavailableException as err:
        return err


def throw_if_service_unavailable(host: str, port: int):
    """
    Simple function to test a connection to mongoDB is possible
    :param host:
    :param port:
    :return:
    """
    import socket

    sock = None
    try:
        sock = socket.create_connection((host, port), timeout=1)
    except socket.error as err:
        raise ServiceUnavailableException(
            "Unable to connect to service at {host}:{port} due to {err}" .format(
                host=host, port=port, err=err))
    finally:
        if sock is not None:
            sock.close()
