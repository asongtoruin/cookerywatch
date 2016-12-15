from HelperFunctions import *
import tweepy


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


def reply_to_tweets(api):
    last_replied_path = get_lib_file('lastreplied.txt')
    last_replied = read_file_to_long(last_replied_path)

    user_mentions = get_user_mentions(api, last_replied)

    # get_user_mentions can return None - catch
    if user_mentions:
        # TODO - set up reading tweets to the account and setting pi light colour accordingly.
        return


def get_user_mentions(api, since):
    try:
        get_mentions = api.mentions_timeline(tweet_mode='extended', since_id=since)
        return [tweet._json for tweet in get_mentions]
    except tweepy.TweepError:
        return None


def post_map(api):
    image_filepath = ''

    tweet_text = '{0}\n' \
                 'Most mentions: {1} ({2})\n' \
                 'Unmentioned teams: {3}'.format(nice_date, most_mentions, most_count, zero_count)

    # TODO - fix tweeting to send out picamera image

    api.update_with_media(filename=image_filepath, status=tweet_text)

    return None
