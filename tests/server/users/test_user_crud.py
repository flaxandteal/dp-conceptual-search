import unittest
from uuid import uuid1

from mockupdb import go, Command, MockupDB


class TestUsers(unittest.TestCase):
    # Generate a test user id
    user_id = str(uuid1())

    def __init__(self, *args, **kwargs):
        super(TestUsers, self).__init__(*args, **kwargs)
        self.response = None

    def setUp(self):
        # create mongo connection to mock server
        self.server = MockupDB(auto_ismaster=True, verbose=True)
        self.server.run()

    def tearDown(self):
        self.server.stop()

    def _run_app(self, queue):
        from server.app import create_app
        import config_core
        from sanic.log import logger

        config_core.MOTOR_URI = "{bind_addr}/{db}".format(
            bind_addr=self.server.uri,
            db="test"
        )

        app = create_app()
        client = app.test_client

        request, response = client.get('/users/find/%s' % self.user_id)

        queue.put(response.json)

    def _start_process(self):
        from multiprocessing import Process, Queue

        q = Queue()

        p = Process(target=self._run_app, args=(q,))
        p.start()
        p.join()

        return q

    def test_find_user(self):
        """
        Tests that we can find a user
        :return:
        """
        # arrange
        user_id = self.user_id

        future = go(self._start_process)

        request = self.server.receives(Command({'find': 'users', 'filter': {
            'user_id': user_id}}))

        request.ok(cursor={'id': 0, 'firstBatch': [
            {'user_id': user_id}
        ]})

        q = future()

        self.assertIsNotNone(q)

        response_body = q.get()
        self.assertIsNotNone(response_body)
        self.assertIn('user_id', response_body)
        self.assertEqual(user_id, response_body['user_id'])


if __name__ == "__main__":
    unittest.main()
