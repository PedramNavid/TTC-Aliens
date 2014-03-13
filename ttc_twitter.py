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
apikey = config['apikey']
apisecret = config['apisecret']
tokenkey = config['tokenkey']
tokensecret = config['tokensecret']

api = twitter.Api(consumer_key=apikey, consumer_secret=apisecret,
                  access_token_key=tokenkey,
                  access_token_secret=tokensecret)


def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        filename='log.txt',
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',)
    if not hasattr(sys, 'frozen'):

        console = logging.StreamHandler(sys.stderr)
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s',
            '%H:%M:%S',)
        console.setFormatter(formatter)
        logging.getLogger('ttc').addHandler(console)


class Bot():
    """ A simple front-end to the Twitter API that reads tweets from a source account
    These are then fed to Writer which tweets them, occasionally adding
    reference to aliens.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_status(user, since=None):
        try:
            statuses = api.GetUserTimeline(screen_name=user, since_id=since, count=1)
            if statuses:
                return statuses[0].text, statuses[0].id
        except requests.exceptions.ConnectionError:
            return
        except twitter.TwitterError:
            return
            
    @staticmethod
    def post(text):
        status = api.PostUpdate(text)
        return status.text


def _get_transit_notice(transit_name):
    """ Gets the latest tweet from a transit twitter account. Stores ID so that future runs
     do not tweet the same status twice. This is called from post_transit_notice and should not be used
     directly
    """
    reader = Bot()
    try:
        last_id = pickle.load(open("lastid.p", "rb"))
        console.debug('Last ID Found: ' + str(last_id))
    except IOError:
        console.info('No last Transit Tweet ID found. Assuming first run.')
        last_id = None
    result = reader.get_status(transit_name, last_id)
    if result:
        transit_status, transit_id = result
        console.info('Got new status: ' + transit_status + ' WITH ID: ' + str(transit_id))
        if transit_id != last_id:
            pickle.dump(transit_id, open("lastid.p", "wb"))
            return transit_status
    return None


def post_transit_notice(transit_name):
    """ Gets the latest transit notice for a source twitter account 'transit_name' and
     posts a new update to authenticated account, with a chance of alienification.
    """
    writer = Bot()
    notice = _get_transit_notice(transit_name)
    if notice:
        result = writer.post(alienify(notice))
        console.info('Posting Notice. Result: ' + result)


def _get_alien_text(max_length):
    """ Picks a random alien phrase, with a defined maximum phrase length
    """
    alien_phrases = ['due to aliens',
                     'due to a collision with a UFO',
                     'due to an alien abduction',
                     'due to alien invasion']
    min_length = min([len(x) for x in alien_phrases])
    if max_length < min_length:
        console.info('Tried to alienify but tweet was too long. Skpping.')
        return None  # max length is too short
    while True:
        alien_str = alien_phrases[random.randint(0, len(alien_phrases)-1)]
        if len(alien_str) <= max_length:
            console.debug('Find alien text' + alien_str)
            return alien_str
    return None


def _strip_text(text, sub):
    """Strips part of a text if 'sub' is found, otherwise returns None
    """
    found = text.find(sub)
    if found < 3:
        # Ignore if sub is found at beginning of text, or not found at all
        return None
    return text[0:found]


def alienify(text, sub="due to", hash_tag=" #TTC", max_length=140, chance=50):
    """Randomly alienifies a text if a substring is found in the text. Max_length
    is 140 by default (twitter limit). Chance is odds of this happening is 2% (1/50).
    """
    stripped = _strip_text(text, sub)
    if stripped:
        # Remove text, potentially add aliens
        alien_random = random.randint(1, chance)
        if alien_random == 1:
            console.info('Alien encountered. Attempting to alienify tweet.')
            phrase_max = max_length - len(stripped)
            phrase = _get_alien_text(phrase_max)
            if phrase is not None:
                return stripped + phrase + hash_tag
    return text


if __name__ == '__main__':
    init_logging()
    console = logging.getLogger('ttc')
    console.debug('Starting program')
    while True:
        post_transit_notice('TTCNotices')
        time.sleep(10)

