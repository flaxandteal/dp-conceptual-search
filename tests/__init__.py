import asyncio
from asyncio import ensure_future
import inspect
import os
import functools


def get_async_test_timeout(default=5):
    """Get the global timeout setting for async tests.
    Returns a float, the timeout in seconds.
    """
    try:
        timeout = float(os.environ.get('ASYNC_TEST_TIMEOUT'))
        return max(timeout, default)
    except (ValueError, TypeError):
        return default


# TODO: Spin off to a PyPI package.
def asyncio_test(func=None, timeout=None):
    """Decorator for coroutine methods of AsyncIOTestCase::
        class MyTestCase(AsyncIOTestCase):
            @asyncio_test
            def test(self):
                # Your test code here....
                pass
    Default timeout is 5 seconds. Override like::
        class MyTestCase(AsyncIOTestCase):
            @asyncio_test(timeout=10)
            def test(self):
                # Your test code here....
                pass
    You can also set the ASYNC_TEST_TIMEOUT environment variable to a number
    of seconds. The final timeout is the ASYNC_TEST_TIMEOUT or the timeout
    in the test (5 seconds or the passed-in timeout), whichever is longest.
    """
    def wrap(f):
        @functools.wraps(f)
        def wrapped(self, *args, **kwargs):
            if timeout is None:
                actual_timeout = get_async_test_timeout()
            else:
                actual_timeout = get_async_test_timeout(timeout)

            coro_exc = None

            def exc_handler(loop, context):
                nonlocal coro_exc
                coro_exc = context['exception']

                # Raise CancelledError from run_until_complete below.
                task.cancel()

            self.loop.set_exception_handler(exc_handler)
            coro = asyncio.coroutine(f)(self, *args, **kwargs)
            coro = asyncio.wait_for(coro, actual_timeout, loop=self.loop)
            task = ensure_future(coro, loop=self.loop)
            try:
                self.loop.run_until_complete(task)
            except BaseException:
                if coro_exc:
                    # Raise the error thrown in on_timeout, with only the
                    # traceback from the coroutine itself, not from
                    # run_until_complete.
                    raise coro_exc from None

                raise

        return wrapped

    if func is not None:
        # Used like:
        #     @gen_test
        #     def f(self):
        #         pass
        if not inspect.isfunction(func):
            msg = ("%r is not a test method. Pass a timeout as"
                   " a keyword argument, like @asyncio_test(timeout=7)")
            raise TypeError(msg % func)
        return wrap(func)
    else:
        # Used like @gen_test(timeout=10)
        return wrap
