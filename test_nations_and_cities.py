"""
OUTDATED
"""
import unittest
import nations_and_cities


class MyTestCase(unittest.TestCase):
    def test_get_next_pop_level(self):
        self.assertEqual(nations_and_cities.get_next_pop_level(5.01), 5.04)  # add assertion here
        self.assertEqual(nations_and_cities.get_next_pop_level(6.96), 6.96)
        self.assertEqual(nations_and_cities.get_next_pop_level(7.99), 8)
        self.assertEqual(nations_and_cities.get_next_pop_level(8.25), 8.28)



if __name__ == '__main__':
    unittest.main()
