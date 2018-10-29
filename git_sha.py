from dp4py_config.utils import git_sha


def print_sha():
    """
    Method to print git commit sha to stdout
    :return:
    """
    print(git_sha())


if __name__ == "__main__":
    print_sha()
