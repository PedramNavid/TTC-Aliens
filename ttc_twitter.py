__author__ = 'Pedram'
import twitter
import random
import pickle
import logging
import sys
import time
import requests.exceptions
import controller

config = controller.get_config()

APIKEY = config['apikey']
APISECRET = config['apisecret']
TOKENKEY = config['tokenkey']
TOKENSECRET = config['tokensecret']
SOURCE_NAME = 'TTCNotices' # Get tweets from this account
MAX_LENGTH = 140 # Used to determine acceptable alien phrases
HASH_TAG = '#TTC' # appends to the end of every tweet. Counts toward length.
SUBSTRING = "due to" # only tweets with this phrase are considered for alienification
CHANCE = 30 # bigger number is less likely, odds are 1/CHANCE, so 50 = 2%, 100 = 1%.
ALIEN_PHRASES = ['due to aliens.',
                 'due to a collision with a UFO.',
                 'due to an alien abduction.',
                 'due to alien invasion.',
                 'due to poisonous Monsanto GMOs.',
                 'due to chemtrail sprayer malfunction',
                 'due to a decline in Spirograph activity',
                 'due to Fukushima radiation',
                 'due to extreme fluoridation',
                 'due to fabricated fraud',
                 'due to questionable birth certificates',
                 'due to Rothschilds interference',
                 'due to geoengineering',
                 'due to HAARPA',
                 'due to reptilians',
                 'due to Russian interference',
                 'due to vaccination attempts'

]


def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        filename='log.txt',
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',)
    if not hasattr(sys, 'frozen'):
        logger = logging.StreamHandler(sys.stderr)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s',
            '%H:%M:%S',)
        logger.setFormatter(formatter)
        logging.getLogger('ttc').addHandler(logger)


class TwitterBotError(Exception):
    pass


class TwitterInterface():
    """ A simple front-end to the python-twitter API. Can read the latest status, using a since_id
    to only retrieve new updates. Can post status updates and will catch and ignore certain errors.
    Errors should probably be caught and handled elsewhere, but this is how it goes for now
    """
    def __init__(self):
        self.api = twitter.Api(consumer_key=APIKEY, consumer_secret=APISECRET,
                  access_token_key=TOKENKEY,
                  access_token_secret=TOKENSECRET)

    def get_status(self, account_name, since=None):
        try:
            statuses = self.api.GetUserTimeline(screen_name=account_name, since_id=since, count=1,
                                                exclude_replies=True)
            if statuses:
                return statuses[0].text, statuses[0].id
        except requests.exceptions.ConnectionError as e:
            raise TwitterBotError('Could not connect to Twitter. Received error: ',  e)
        except twitter.TwitterError as e:
            raise TwitterBotError('Could not read status. Received error: ', e)

    def post_status(self, text):
        if len(text)>MAX_LENGTH:
            logging.error('Too many characters: ' + text)
            raise TwitterBotError('Too many characters in text. Got %s, should be %s.', len(text), MAX_LENGTH)
        status = self.api.PostUpdate(text)
        return status.text

class Bot():
    """ Bot integrates front-end behavior with the TwitterInterface. Ensures status updates
    are not repeated, alienifies texts with the aid of utility functions, etc. This is
    the main class to call outside this module.
    """
    def __init__(self, source_name=SOURCE_NAME, substring=SUBSTRING, maxlength=MAX_LENGTH,
                 hashtag=HASH_TAG, chance=CHANCE):
        self.interface = TwitterInterface()
        self.source_name=source_name
        self.substring=substring
        self.maxlength=maxlength
        self.hashtag=hashtag
        self.chance=chance


    def qualify_phrase(self, text, sub):
        """ Qualifies a phrase for alienification using a set of rules.
        """

        q1 = text.find(sub) != -1   # sub must be in text
        q2 = text.find(sub) > 1     # sub must not be beginning of text
        return q1 and q2

    @staticmethod
    def _strip_text(text, sub):
        """Strips part of a text if 'sub' is found, otherwise returns None
        """
        found = text.find(sub)
        return text[0:found]

    @staticmethod
    def _get_shortest_alien_phrase():
        """ Finds shortest alien phrase
        """
        return min([len(x) for x in ALIEN_PHRASES])


    def _get_alien_text(self, tweet_length):
        """ Picks a random alien phrase that will fit within a tweet_length
        """
        min_length = self._get_shortest_alien_phrase()
        if tweet_length < min_length:
            raise TwitterBotError ('Cannot alienify tweet with length: ', tweet_length)
        while True:
            # Todo: this can be more efficient. Should trim list before randomizing
            # Pick a random alien phrase
            alien_str = ALIEN_PHRASES[random.randint(0, len(ALIEN_PHRASES)-1)]
            if len(alien_str) <= tweet_length:
                logging.info('Found alien text' + alien_str)
                return alien_str



    def get_latest(self):
        """ Gets the latest tweet from a transit twitter account. Stores ID so that future runs
         do not tweet the same status twice.
        """
        try:
            last_id = pickle.load(open("lastid.p", "rb"))
            logging.debug('Last ID Found: ' + str(last_id))
        except IOError:
            logging.info('No last Transit Tweet ID found. Assuming first run.')
            last_id = None
        try:
            result = self.interface.get_status(self.source_name, last_id)
            if result:
                transit_status, transit_id = result
                logging.info('Got new status: ' + transit_status + ' WITH ID: ' + str(transit_id))
                if transit_id != last_id:
                    pickle.dump(transit_id, open("lastid.p", "wb"))
                return transit_status
        except TwitterBotError as e:
            logging.error('Error reading latest status: ', e)


    def post_latest(self):
        """ Gets the latest transit notice for a source twitter account 'transit_name' and
         posts a new update to authenticated account, with a chance of alienification.
        """
        notice = self.get_latest()
        if notice:
            logging.info('Attempting to post Notice: ' + notice)
            try:
                self.interface.post_status(self.alienify(notice))
            except TwitterBotError as e:
                logging.error('Error posting latest status: ', e )
            except Twitter.TwitterError as e:
                logging.error('Error posting latest status: ', e )


    def alienify(self, text):
        """Randomly alienifies a text if a substring is found in the text. Max_length
        is 140 by default (twitter limit). Chance is odds of this happening is 2% (1/50).
        """
        if self.qualify_phrase(text, self.substring):
            stripped = self._strip_text(text, self.substring)
            allowed_max = self.maxlength - (len(stripped) + len(self.hashtag)) # TODO: Move this to qualify_phrase
            if allowed_max >= self._get_shortest_alien_phrase():
                # Remove text, potentially add aliens
                alien_random = random.randint(1, self.chance)
                if alien_random == 1:
                    logging.info('Alien encountered. Attempting to alienify tweet.')
                    logging.debug('Looking for valid match for: ' + stripped)
                    try:
                        phrase = self._get_alien_text(allowed_max)
                        return stripped + phrase + HASH_TAG
                    except TwitterBotError:
                        logging.warning('Tried to alienify but tweet was too long. Skipping this Alien instance.')
        return text


if __name__ == '__main__':
    init_logging()
    logging = logging.getLogger('ttc')
    logging.debug('Starting program')
    bot = Bot()
    while True:
        bot.post_latest()
        time.sleep(10)

