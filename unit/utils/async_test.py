"""
Simple class to provide method for running a function asynchronously
"""
from typing import Callable


class AsyncTestCase(object):

    def run_async(self, fn:Callable):
        """
        Execute the callable using an asyncio event loop
        :param fn:
        :return:
        """
        import asyncio

        # Call execute asynchronously and test method calls
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        # Run the async test
        coro = asyncio.coroutine(fn)
        event_loop.run_until_complete(coro())
