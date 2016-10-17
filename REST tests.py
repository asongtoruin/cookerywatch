from DatabaseManager import FootballDatabaseManager
from HelperFunctions import *
import api_functions
import tweepy
import schedule
import time

# store in files - values kept secret if you back up to e.g. GitHub
keys = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']
keys_vals = ['', '', '', '']

for i in range(len(keys)):
    with open(get_lib_file('{}.txt'.format(keys[i]))) as f:
        keys_vals[i] = f.read()

# do the auth dance
# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)

auth = tweepy.OAuthHandler(keys_vals[0], keys_vals[1])
auth.set_access_token(keys_vals[2], keys_vals[3])

initialise_api = tweepy.API(auth)

# initialise our database
foot_db = FootballDatabaseManager(get_lib_file('Footbot.db'),
                                  get_lib_file('Stadia_located.csv'))

api_functions.check_followers_and_follow(api=initialise_api)
api_functions.check_tweets(api=initialise_api, db=foot_db)
api_functions.reply_to_tweets(api=initialise_api, db=foot_db)

schedule.every(10).minutes.do(api_functions.check_followers_and_follow, api=initialise_api)
schedule.every(10).minutes.do(api_functions.check_tweets, api=initialise_api, db=foot_db)
schedule.every(10).minutes.do(api_functions.reply_to_tweets, api=initialise_api, db=foot_db)

# uncomment when mapping is set up:
# schedule.every().day.at("09:00").do(api_functions.post_map, api=initialise_api, db=foot_db)

while True:
    schedule.run_pending()
    time.sleep(1)
