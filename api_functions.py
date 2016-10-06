from HelperFunctions import read_bbc_page, find_word, read_file_to_long, write_long_to_file, get_lib_file
import tweepy


def check_followers_and_follow(api):
    for follower in tweepy.Cursor(api.followers).items():
        follower_json = follower._json
        check_user = follower_json['screen_name']
        follow_info = api.show_friendship(source_screen_name=api.me().name,
                                          target_screen_name=check_user)

        # if the bot isn't following someone, follow them!
        if not follow_info[1].followed_by and not follow_info[1].following_received:
            print 'start following ' + check_user
            api.create_friendship(screen_name=check_user)


def check_tweets(api, db):
    last_check_path = get_lib_file('lastchecked.txt')
    last_checked = read_file_to_long(last_check_path)

    # get BBCSport tweets using our API, and since the last tweet we checked
    # go through the process of adding it to our database
    returned_tweets = get_user_tweets(api, 'BBCSport', last_checked)
    for BBC_tweet in returned_tweets:
        tweet_to_database(BBC_tweet, db)

    # if we had any tweets returned, we want to update the last one we checked (to avoid duplication later on)
    if returned_tweets:
        write_long_to_file(last_check_path, returned_tweets[0]['id'])


def get_user_tweets(api, user_name, since):
    tweets = []
    for tweet in api.user_timeline(screen_name=user_name, count=200, tweet_mode='extended', since_id=since):
        tweets.append(tweet._json)
    return tweets


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
    for tweet in user_mentions:
        reply_to_tweet(api, tweet, db)

    if user_mentions:
        write_long_to_file(last_replied_path, user_mentions[0]['id'])


# update later - does this work with private users? Test with since_id=781536232333508608L, see if Jade's tweet appears
def get_user_mentions(api, since):
    tweets = []
    for tweet in api.mentions_timeline(tweet_mode='extended', since_id=since):
        tweets.append(tweet._json)
    return tweets


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
    print('Replied to ' + reply_to_user)
