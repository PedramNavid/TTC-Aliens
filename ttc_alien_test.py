import unittest
import ttc_twitter
import logging

#noinspection PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember,PyProtectedMember
class BotTests(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.WARN)
        self.tweet ="Customers on Line 1 YUS. Service has been suspended between Davisville and Union stations \
due to power off at Wellesley.#TTC"
        self.substring = 'due to'
        self.maxlength = 140
        self.hashtag = '#TTC'

        self.chance=1
        self.bot = ttc_twitter.Bot(source_name='test', substring=self.substring, maxlength=self.maxlength,
                              hashtag=self.hashtag, chance=self.chance)

    def test_stripped_string(self):
        stripped = "Customers on Line 1 YUS. Service has been suspended between Davisville and Union stations "
        self.assertEqual(stripped, self.bot._strip_text(self.tweet, self.substring))

    def test_stripped_notfound(self):
        my_string = "the substring is not found in this text"
        self.assertIsNone(self.bot._strip_text(my_string, self.substring))

    def test_stripped_beginning(self):
        my_string = "Due to some garbage on tracks everything is broken. "
        self.assertIsNone(self.bot._strip_text(my_string, self.substring))

    def test_stripped_caps(self):
        # shouldn't occur but if it does let's ignore it.
        my_string = "There is a problem on the TTC Due to garbage."
        self.assertIsNone(self.bot._strip_text(my_string, self.substring))

    def test_get_alien_min_length(self):
        self.assertLess(self.bot._get_shortest_alien_phrase(), self.maxlength)

    def test_alien_max_length(self):
        shortest = self.bot._get_shortest_alien_phrase()
        longest = self.maxlength
        for i in range(100): # should be enough to get one of every phrase
            for max_length in range(shortest,longest):
                self.assertLessEqual(len(self.bot._get_alien_text(max_length)), self.maxlength)
        self.assertRaises(ttc_twitter.TwitterBotError, self.bot._get_alien_text, shortest-1)

    def test_alienify_chance(self):
        for i in range(100):
            self.assertNotEqual(self.tweet, self.bot.alienify(self.tweet))

    def test_alienify_handles_long_tweets(self):
        test_string = 'i like apples' * 50 + ' due to some strange reason'
        self.assertEquals(self.bot.alienify(test_string), test_string)






def main():
    unittest.main()

if __name__ == '__main__':
    main()