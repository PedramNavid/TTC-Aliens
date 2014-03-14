__author__ = 'Pedram'
import twitter
import random
import pickle
import logging
import sys
import time
import requests.exceptions
import controller

config = controller.getConfig()
APIKEY = config['apikey']
APISECRET = config['apisecret']
TOKENKEY = config['tokenkey']
TOKENSECRET = config['tokensecret']
SOURCE_NAME = 'TTCNotices' # Get tweets from this account
MAX_LENGTH = 140 # Used to determine acceptable alien phrases
HASH_TAG = '#TTC' # appends to the end of every tweet. Counts toward length.
SUBSTRING = "due to" # only tweets with this phrase are considered for alienification
CHANCE = 50 # bigger number is less likely, odds are 1/CHANCE, so 50 = 2%, 100 = 1%.
ALIEN_PHRASES = ['due to aliens.',
                 'due to a collision with a UFO.',
                 'due to an alien abduction.',
                 'due to alien invasion.',
                 'due to poisonous Monsanto GMOs.',
                 'due to chemtrail sprayer malfunction',
                 'due to a decline in Spirograph activity',
                 'due to Fukushima radiation',
                 'due to extreme fluoridation',
]

api = twitter.Api(consumer_key=APIKEY, consumer_secret=APISECRET,
                  access_token_key=TOKENKEY,
                  access_token_secret=TOKENSECRET)


def init_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        filename='log.txt',
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',)
    if not hasattr(sys, 'frozen'):
        console = logging.StreamHandler(sys.stderr)
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s',
            '%H:%M:%S',)
        console.setFormatter(formatter)
        logging.getLogger('ttc').addHandler(console)


class Bot():
    """ A simple front-end to the python-twitter API. Can read the latest status, using a since_id
    to only retrieve new updates. Can post status updates and will catch and ignore certain errors.
    Errors should probably be caught and handled elsewhere, but this is how it goes for now
    """
    def __init__(self, source_name):
        self.source_name = source_name

    def get_status(self, since=None):
        try:
            statuses = api.GetUserTimeline(screen_name=self.source_name, since_id=since, count=1)
            if statuses:
                return statuses[0].text, statuses[0].id
        except requests.exceptions.ConnectionError:
            return
        except twitter.TwitterError:
            return

    @staticmethod
    def post(text):
        if len(text)>140:
            console.error('Too many characters: ' + text)
            return
        status = api.PostUpdate(text)
        return status.text


def _get_transit_notice(source_name):
    """ Gets the latest tweet from a transit twitter account. Stores ID so that future runs
     do not tweet the same status twice. This is called from post_transit_notice and should not be used
     directly
    """
    reader = Bot(source_name)
    try:
        last_id = pickle.load(open("lastid.p", "rb"))
        console.debug('Last ID Found: ' + str(last_id))
    except IOError:
        console.info('No last Transit Tweet ID found. Assuming first run.')
        last_id = None
    result = reader.get_status(last_id)
    if result:
        transit_status, transit_id = result
        console.info('Got new status: ' + transit_status + ' WITH ID: ' + str(transit_id))
        if transit_id != last_id:
            pickle.dump(transit_id, open("lastid.p", "wb"))
            return transit_status
    return None


def post_transit_notice():
    """ Gets the latest transit notice for a source twitter account 'transit_name' and
     posts a new update to authenticated account, with a chance of alienification.
    """
    writer = Bot(SOURCE_NAME)
    notice = _get_transit_notice(SOURCE_NAME)
    if notice:
        console.info('Posting Notice. Result: ' + notice)
        writer.post(alienify(notice))


def _get_alien_text(max_length):
    """ Picks a random alien phrase, within a defined maximum phrase length.
    """
    min_length = min([len(x) for x in ALIEN_PHRASES])
    if max_length < min_length:
        console.warn('Tried to alienify but tweet was too long. Skipping this Alien instance.')
        return None
    while True:
        # Pick a random alien phrase
        alien_str = ALIEN_PHRASES[random.randint(0, len(ALIEN_PHRASES)-1)]
        if len(alien_str) <= max_length:
            console.info('Found alien text' + alien_str)
            return alien_str


def _strip_text(text, sub):
    """Strips part of a text if 'sub' is found, otherwise returns None
    """
    found = text.find(sub)
    if found < 3:
        # Ignore if sub is found at beginning of text, or not found at all
        return None
    return text[0:found]


def alienify(text):
    """Randomly alienifies a text if a substring is found in the text. Max_length
    is 140 by default (twitter limit). Chance is odds of this happening is 2% (1/50).
    """
    stripped = _strip_text(text, SUBSTRING)
    if stripped: # returns None if substring not found
        # Remove text, potentially add aliens
        alien_random = random.randint(1, CHANCE)
        if alien_random == 1:
            console.info('Alien encountered. Attempting to alienify tweet.')
            phrase_max = MAX_LENGTH - len(stripped) - len(HASH_TAG)
            console.debug('Looking for valid match for: ' + stripped)
            phrase = _get_alien_text(phrase_max)
            if phrase is not None:
                return stripped + phrase + HASH_TAG
    return text


if __name__ == '__main__':
    init_logging()
    console = logging.getLogger('ttc')
    console.debug('Starting program')
    while True:
        post_transit_notice()
        time.sleep(10)

