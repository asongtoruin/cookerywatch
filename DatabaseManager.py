import sqlite3
import csv
from HelperFunctions import text_to_date, textdate_to_yyyymmdd


class FootballDatabaseManager(object):
    """
    Sets up database for use in managing football database.
    Must be initialised with a link to an sqlite database.
    Methods:
        add_tables(csv)
        Takes a csv file containing the location of football clubs
        which **must** contain the fields "League", "Team" and "Team_nickname"
    """
    def __init__(self, db, csv_file):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT Count(*) FROM sqlite_master WHERE type='table' AND name='Stadia'")
        if self.cur.fetchone()[0] != 1:
            print 'Adding tables'
            self.add_starter_tables(csv_file)

    def close_connection(self):
        self.conn.close()

    def add_starter_tables(self, stadia_source):
        stadia = csv.DictReader(open(stadia_source, 'rb'), delimiter=',')
        self.cur.execute('CREATE TABLE Stadia (League text)')

        for fieldname in stadia.fieldnames:
            if fieldname != 'League':
                if fieldname == 'Lat' or fieldname == 'Long':
                    fieldtype = 'float'
                else:
                    fieldtype = 'text'

                self.cur.execute('ALTER TABLE Stadia ADD COLUMN {} {}'.format(fieldname, fieldtype))

        for row in stadia:
            rowtext = ''
            for fieldname in stadia.fieldnames:
                if fieldname == 'Lat' or fieldname == 'Long':
                    rowtext = '{} {},'.format(rowtext, row[fieldname])
                else:
                    rowtext = '{} "{}",'.format(rowtext, row[fieldname])
            rowtext = rowtext[:-1]

            self.cur.execute('INSERT INTO Stadia VALUES ({})'.format(rowtext))

        self.cur.execute('CREATE TABLE LatestTweet (Team text, Team_nickname text, ArticleLink text, '
                         'TweetLink text, TweetDate text)')
        self.cur.execute('INSERT INTO LatestTweet (Team, Team_nickname) SELECT Team, Team_nickname FROM Stadia')
        self.cur.execute('CREATE TABLE CheckedLinks (ShortLink text, LongLink text)')
        self.conn.commit()

    def get_all_teams(self):
        """
        Returns: all teams and team nicknames
        """
        return self.cur.execute('SELECT Team, Team_nickname FROM Stadia').fetchall()

    def has_link_been_checked(self, short_url):
        """
        Call using the shortened URL

        Returns: Boolean - True if the link has already been checked, False if not
        """
        self.cur.execute('SELECT LongLink FROM CheckedLinks WHERE ShortLink = ?', (short_url,))
        data = self.cur.fetchone()
        if data is None:
            return False
        else:
            return True

    def add_checked_link(self, short_url, long_url):
        """
        Call with Short URL, Long URL
        Adds to the list of checked links
        """
        self.cur.execute('INSERT INTO CheckedLinks VALUES (?,?)', (short_url, long_url))
        self.conn.commit()

    def update_latest_link(self, team, article_link, tweet_link, tweet_date):
        self.cur.execute('SELECT TweetDate FROM LatestTweet WHERE Team=?', (team,))
        current_date = self.cur.fetchone()
        if text_to_date(tweet_date) > text_to_date(current_date[0]):
            self.cur.execute('UPDATE LatestTweet SET ArticleLink=?, TweetLink=?, TweetDate=? WHERE Team=?',
                             (article_link, tweet_link, tweet_date, team))
            self.conn.commit()

    def update_team_count(self, team, tweet_date):
        date_table = '_{}'.format(textdate_to_yyyymmdd(tweet_date))
        self.cur.execute("SELECT Count(*) FROM sqlite_master WHERE type='table' AND name=?", (date_table,))
        if self.cur.fetchone()[0] != 1:
            self.cur.execute('CREATE TABLE {} (Team text, ArticleCount integer DEFAULT 0)'
                             .format(date_table))
            self.cur.execute('INSERT INTO {} (Team) SELECT Team FROM Stadia'
                             .format(date_table))
            self.conn.commit()
        self.cur.execute('SELECT ArticleCount FROM {} WHERE Team=?'.format(date_table), (team,))
        new_count = self.cur.fetchone()[0] + 1
        self.cur.execute('UPDATE {} SET ArticleCount=? WHERE Team=?'.format(date_table), (new_count, team))
        self.conn.commit()

    def check_latest_link(self, team):
        """
        Call using a team name.

        Returns: Article link, tweet link, tweet date
        """
        self.cur.execute('SELECT * FROM LatestTweet WHERE Team=?', (team,))
        data = self.cur.fetchone()
        return data[2], data[3], data[4]

    def export_frequencies_table(self, table_name):
        # first check the table exists
        self.cur.execute("SELECT Count(*) FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if self.cur.fetchone()[0] != 1:
            return None

        self.cur.execute("SELECT {0}.Team AS Team, Stadia.Lat AS Lat, Stadia.Long AS Long, ArticleCount FROM {0} "
                         "INNER JOIN Stadia ON {0}.Team = Stadia.Team ORDER BY ArticleCount DESC".format(table_name))
        return self.cur.fetchall()

    def count_zeroes(self, table_name):
        # first check the table exists
        self.cur.execute("SELECT Count(*) FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if self.cur.fetchone()[0] != 1:
            return None

        self.cur.execute("SELECT Count(*) FROM {0} WHERE ArticleCount=0".format(table_name))
        return self.cur.fetchone()[0]

    def get_all_max_rows(self, table_name):
        self.cur.execute("SELECT Count(*) FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if self.cur.fetchone()[0] != 1:
            return None

        self.cur.execute("SELECT Team, ArticleCount FROM {0} "
                         "WHERE ArticleCount=(SELECT Max(ArticleCount) FROM {0})".format(table_name))
        return self.cur.fetchall()
