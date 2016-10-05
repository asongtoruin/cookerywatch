from DatabaseManager import FootballDatabaseManager
from HelperFunctions import read_file_to_long, get_lib_file, write_long_to_file
import api_functions
import tweepy

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

last_check_path = get_lib_file('lastchecked.txt')
last_replied_path = get_lib_file('lastreplied.txt')

last_checked = read_file_to_long(last_check_path)
last_replied = read_file_to_long(last_replied_path)

# check_followers_and_follow(initialise_api)

# get BBCSport tweets using our API, and since the last tweet we checked
# go through the process of adding it to our database
returned_tweets = api_functions.get_user_tweets(initialise_api, 'BBCSport', last_checked)
for BBC_tweet in returned_tweets:
    api_functions.tweet_to_database(BBC_tweet, foot_db)

# if we had any tweets returned, we want to update the last one we checked (to avoid duplication later on)
if returned_tweets:
    write_long_to_file(last_check_path, returned_tweets[0]['id'])

user_mentions = api_functions.get_user_mentions(initialise_api, last_replied)
for tweet in user_mentions:
    print tweet['full_text']
    print tweet['id']
    api_functions.reply_to_tweet(initialise_api, tweet, foot_db)

if user_mentions:
    write_long_to_file(last_check_path, user_mentions[0]['id'])
