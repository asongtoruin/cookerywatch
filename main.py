from HelperFunctions import *
import raspberry_functions as rasp
import api_functions
import tweepy
import schedule
import time

rasp.initialise_lights()

# store in files - values kept secret if you back up to e.g. GitHub
keys = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']
keys_vals = ['', '', '', '']

for i in range(len(keys)):
    with open(get_lib_file('{}.txt'.format(keys[i]))) as f:
        keys_vals[i] = f.read()

# do the auth dance
auth = tweepy.OAuthHandler(keys_vals[0], keys_vals[1])
auth.set_access_token(keys_vals[2], keys_vals[3])

initialise_api = tweepy.API(auth)

api_functions.check_followers_and_follow(api=initialise_api)
api_functions.react_to_tweets(api=initialise_api)
api_functions.take_and_post_image(api=initialise_api)

schedule.every(10).minutes.do(api_functions.take_and_post_image, api=initialise_api)
schedule.every(5).minutes.do(api_functions.react_to_tweets, api=initialise_api)
schedule.every(15).minutes.do(api_functions.check_followers_and_follow, api=initialise_api)

while True:
    schedule.run_pending()
    time.sleep(1)
