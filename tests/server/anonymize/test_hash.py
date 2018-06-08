from unittest import TestCase


class TestHash(TestCase):

    def test_defaults(self):
        """
        Tests that the hashing algorithm works with the default salt and substring index
        :return:
        """
        from uuid import uuid1
        from server.anonymize import hash_value

        salt = ''
        substr_index = 0
        value = str(uuid1())

        h = hash_value(value, salt=salt, substr_index=substr_index)

        self.assertIsNotNone(h)
        self.assertEqual(len(h), 128)
        self.assertNotEqual(h, value)
        self.assertFalse(value in h)

    def test_random_salt(self):
        """
        Tests that the hashing algorithm works with a random salt
        :return:
        """
        from uuid import uuid1
        from server.anonymize import hash_value

        salt = str(uuid1())
        substr_index = 0
        value = str(uuid1())

        h = hash_value(value, salt=salt, substr_index=substr_index)

        self.assertIsNotNone(h)
        self.assertEqual(len(h), 128)
        self.assertNotEqual(h, value)
        self.assertFalse(value in h)
        self.assertFalse(salt in h)

    def test_random_salt_and_substr_index(self):
        """
        Tests that the hashing algorithm works with a random salt and substring index
        :return:
        """
        import random
        from uuid import uuid1
        from server.anonymize import hash_value

        salt = str(uuid1())
        substr_index = random.randint(0, 101)  # random int between 0 and 100
        value = str(uuid1())

        h = hash_value(value, salt=salt, substr_index=substr_index)

        self.assertIsNotNone(h)
        self.assertEqual(len(h), 128)
        self.assertNotEqual(h, value)
        self.assertFalse(value in h)
        self.assertFalse(salt in h)
