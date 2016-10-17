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


def check_tweets(api, db):
    last_check_path = get_lib_file('lastchecked.txt')
    last_checked = read_file_to_long(last_check_path)

    # get BBCSport tweets using our API, and since the last tweet we checked
    # go through the process of adding it to our database
    returned_tweets = get_user_tweets(api, 'BBCSport', last_checked)

    # it's possible for get_user_tweets to return None, if there's an error. Check we can iterate:
    if returned_tweets:
        for BBC_tweet in returned_tweets:
            tweet_to_database(BBC_tweet, db)

    # update the last tweet checked (to avoid duplication later on)
            write_long_to_file(last_check_path, returned_tweets[0]['id'])
    print '+' * 20


def get_user_tweets(api, user_name, since):
    try:
        get_tweets = api.user_timeline(screen_name=user_name, count=200, tweet_mode='extended', since_id=since)
        return [tweet._json for tweet in get_tweets]
    except tweepy.TweepError:
        return None


def tweet_to_database(tweet, db):
    print '-'*20
    print tweet['full_text']
    tweet_date = tweet['created_at']
    print('Created at: ' + tweet['created_at'])

    # "truncated" tweets store the media URLs in a slightly different manner:
    if tweet['truncated']:
        embedded_urls = tweet['extended_tweet']['entities']['urls']
    else:
        embedded_urls = tweet['entities']['urls']

    for linkurl in embedded_urls:
        check_url = linkurl['expanded_url']
        print(check_url)
        if not db.has_link_been_checked(check_url):
            read_article = read_bbc_page(check_url)
            if read_article[3]:
                for team in db.get_all_teams():
                    check_for_team = False
                    # check the nickname first, if it exists
                    if len(team[1]) != 0:
                        check_for_team = find_word(team[1], read_article[2])
                    # check the full name if we haven't found the nickname (or the nickname doesn't exist!)
                    if not check_for_team:
                        check_for_team = find_word(team[0], read_article[2])
                    if check_for_team:
                        db.update_latest_link(team[0], check_url,
                                              'http://twitter.com/bbcsport/statuses/{}'
                                              .format(tweet['id']), tweet_date)
                        print 'FOUND! ' + team[0]
                        db.update_team_count(team[0], tweet_date)

            # add the checked link
            db.add_checked_link(check_url, read_article[0])
        else:
            print 'Already seen'


def reply_to_tweets(api, db):
    last_replied_path = get_lib_file('lastreplied.txt')
    last_replied = read_file_to_long(last_replied_path)

    user_mentions = get_user_mentions(api, last_replied)

    # get_user_mentions can return None - catch
    if user_mentions:
        for tweet in user_mentions:
            reply_to_tweet(api, tweet, db)

        write_long_to_file(last_replied_path, user_mentions[0]['id'])


def get_user_mentions(api, since):
    try:
        get_mentions = api.mentions_timeline(tweet_mode='extended', since_id=since)
        return [tweet._json for tweet in get_mentions]
    except tweepy.TweepError:
        return None


def reply_to_tweet(api, tweet, db):
    reply_to_user = tweet['user']['screen_name']
    team_found = False
    for team in db.get_all_teams():
        check_for_team = False
        # check the nickname first, if it exists
        if len(team[1]) != 0:
            check_for_team = find_word(team[1], tweet['full_text'])
        # check the full name if we haven't found the nickname (or the nickname doesn't exist!)
        if not check_for_team:
            check_for_team = find_word(team[0], tweet['full_text'])
        if check_for_team:
            team_found = True
            reply_text = 'Team: {}\n' \
                         'Last article: {}'.format(team[0],
                                                   db.check_latest_link(team[0])[0])

            api.update_status('@{} {}'.format(reply_to_user, reply_text),
                              in_reply_to_status_id=tweet['id'])

    if not team_found:
        api.update_status('@{} {}'.format(reply_to_user, "I can't find a team here sorry!"),
                          in_reply_to_status_id=tweet['id'])
    print '*'*20
    print('Replied to ' + reply_to_user)
    print '+' * 20


def post_map(api, db):
    yesterday = get_yesterday()
    yesterday_table = '_' + yesterday

    max_teams = db.get_all_max_rows(yesterday_table)
    zero_count = db.count_zeroes(yesterday_table)
    image_filepath = make_map(db.export_frequencies_table(yesterday_table), yesterday)

    if len(max_teams) > 6:
        most_mentions = "6+ teams"
    else:
        most_mentions = ', '.join([team[0] for team in max_teams])

    most_count = max_teams[0][1]
    nice_date = '/'.join([yesterday[-2:], yesterday[4:6], yesterday[:4]])

    tweet_text = '{0}\n' \
                 'Most mentions: {1} ({2})\n' \
                 'Unmentioned teams: {3}'.format(nice_date, most_mentions, most_count, zero_count)

    api.update_with_media(filename=image_filepath, status=tweet_text)

    return None
