import unittest
import initiation


class MyTestCase(unittest.TestCase):
    def test_start_production(self):
        self.assertEqual(initiation.start_production("Supplies"), 2100)
        self.assertEqual(initiation.start_production("Components"), 1800)
        self.assertEqual(initiation.start_production("Fuel"), 2100)
        self.assertEqual(initiation.start_production("Electronics"), 1500)
        self.assertEqual(initiation.start_production("Rare Materials"), 1200)
        self.assertEqual(initiation.start_production("Blabla"), None)
        self.assertEqual(initiation.start_production(None), None)


if __name__ == '__main__':
    unittest.main()
