from HelperFunctions import * 
import tweepy 
import re 
from raspberry_functions import *
import random

def check_followers_and_follow(api):
    try:
        followers = tweepy.Cursor(api.followers).items()
    except tweepy.TweepError:
        return None

    for follower in followers:
        follower_json = follower._json
        check_user = follower_json['screen_name']
        try:
            follow_info = api.show_friendship(source_screen_name=api.me().name,
                                              target_screen_name=check_user)
        except tweepy.TweepError:
            return None

        # if the bot isn't following someone, follow them!
        if not follow_info[1].followed_by and not follow_info[1].following_received:
            print 'start following ' + check_user
            api.create_friendship(screen_name=check_user)
    print '+' * 20


def react_to_tweets(api):
    last_replied_path = get_lib_file('lastreplied.txt')
    last_replied = read_file_to_long(last_replied_path)

    user_mentions = get_user_mentions(api, last_replied)

    # get_user_mentions can return None - catch
    if user_mentions:
        for tweet in user_mentions:
            # TODO - set up reading tweets to the account and setting pi light colour accordingly.
            main = tweet['full_text']
            provided_colours = colours_from_text(main)
            set_light = random.choice(range(2, 8))
            change_light(set_light, *provided_colours)
            reply_to_tweet(api, tweet, set_light, provided_colours)

        write_long_to_file(last_replied_path, user_mentions[0]['id'])
        return


def get_user_mentions(api, since):
    try:
        get_mentions = api.mentions_timeline(tweet_mode='extended', since_id=since)
        return [tweet._json for tweet in get_mentions]
    except tweepy.TweepError:
        return None


def post_image(api, image_filepath, tweet_text):
    # TODO - fix tweeting to send out picamera image
    api.update_with_media(filename=image_filepath, status=tweet_text)
    return None


def reply_to_tweet(api, tweet, pixel, colours):
    reply_to_user = tweet['user']['screen_name']
    reply_text = 'Changed light number {}! Merry Christmas, nerd'.format(pixel)
    out_image = colour_block(*colours)
    api.update_with_media(status='@{} {}'.format(reply_to_user, reply_text), in_reply_to_status_id=tweet['id'], filename=out_image)
    print '*'*20
    print('Replied to ' + reply_to_user)
    print '+' * 20
