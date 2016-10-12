import urllib2
import re
from dateutil.parser import parse
from bs4 import BeautifulSoup
import os
import sys


# function to read a BBC sport page. Returns headline, full URL and body text
def read_bbc_page(url):
    """
    Returns text and information about a BBC Sport page

    Input: url (can be a shortened URL)
    Output: full URL (i.e. un-shortened), title of the article, text of the article body
    """

    # initialise variables
    full_url = ''
    article_title = ''
    body_text = ''
    football_article = False

    # open the URL - check we get an OK response
    try:
        resp = urllib2.urlopen(url)
    except urllib2.HTTPError, urllib2.URLError:
        return url, article_title, body_text, football_article

    if 200 <= resp.getcode() < 300:
        # this gives us the full URL - useful when hidden behind a URL shortener
        full_url = resp.url

        # check if it's a football article
        if full_url.find('football') > 0:
            football_article = True
            print 'Football!!'
            # make the soup! (parse the document)
            soup = BeautifulSoup(resp, 'html.parser')

            # print the text of the title
            article_title = soup.title.get_text()

            # this seems to be the indicator of the first paragraph of BBC sport stories - tag p, class introduction
            first_p = soup.find("p", class_="sp-story-body__introduction")

            # check in case of video page
            if first_p is None:
                first_p = soup.find("p", class_="sp-media-asset__smp-message")

            # initialise - if we don't find anything, we'll still return an empty string
            body_text = ''

            # catch for if there's no use of p
            if first_p is not None:
                # store this introductory paragraph, to be added to later
                body_text = first_p.get_text()

                # find_next lets us loop to the next use of the tag p - note this is relative to first_p,
                # as we are searching after it
                next_p = first_p.find_next("p")

                # initialise loop - "Share this with" seems to be the first non-body use of the tag p, but in case it
                # is missing allow the check as to whether we have looped through all instances of the tag
                while next_p.get_text() != 'Share this with' and next_p.get_text() is not None:
                    body_text = body_text + '\n' + next_p.get_text()

                    # note - our find_next applies to next_p this time, allowing us to loop through the document
                    next_p = next_p.find_next("p")

    # once we're done, return info
    return full_url, article_title, body_text, football_article


def find_word(word, text_to_search):
    """
    Checks if a word exists in text using regex (thus, matched as an entire word rather than within a word)

    Inputs: word to find, text to search in
    Outputs: Boolean True if the word is found at leats once, False if it is not found at all.
    """
    regexp = re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE)
    foundword = re.search(regexp, text_to_search)
    if foundword is not None:
        return True
    else:
        return False


def text_to_date(datestring):
    if datestring:
        # dt = datetime.datetime.strptime(datestring, '%a %b %d %H:%M:$S +0000 %Y')
        return parse(datestring)
    else:
        return parse('22 Apr 18:52:00 +0000 1991')


def textdate_to_yyyymmdd(datestring):
    return parse(datestring).strftime('%Y%m%d')


def read_file_to_long(fpath):
    # If our file exists, it'll have a value in it.
    # Use this to determine which tweets to check after
    if os.path.isfile(fpath):
        with open(fpath, 'rb') as file:
            return long(file.read())
    # If it doesn't, set to "None" to avoid conflicts when it is used as an argument.
    else:
        return None


def get_lib_file(filename):
    return os.path.join(sys.path[0], 'lib', filename)


def write_long_to_file(fpath, val):
    with open(fpath, 'wb') as file:
        file.write(str(val))
