import codecs
import json
import re
from gephistreamer import graph
from gephistreamer import streamer
from collections import defaultdict
from pprint import pprint

import praw

from Profile import ID
from Profile import PASSWORD
from Profile import SECRET
from Profile import USERNAME
from Profile import USER_AGENT

r = praw.Reddit(client_id=ID,
                client_secret=SECRET,
                password=PASSWORD,
                user_agent=USER_AGENT,
                username=USERNAME)

subreddit_edges = defaultdict(int)
subreddits = {}
# Limit is just for testing purposes
limit = 1000
# with codecs.open('/Volumes/Jason Deskt/Reddit/RC_2018-02','rU','utf-8') as f:
with codecs.open('sample_data.json', 'rU', 'utf-8') as f:
    for index, line in enumerate(f):
        if index == limit:
            break
        post = json.loads(line)
        bodies = post['body'].split('/r/')

        # filter out giant copy-paste comments with subreddits
        if len(bodies) > 20:
            continue

        iter_bodies = iter(bodies)
        next(iter_bodies)
        for body in iter_bodies:
            this_subreddit = post['subreddit'].lower()
            if this_subreddit not in subreddits:
                subreddits[this_subreddit] = r.subreddit(this_subreddit).subscribers

            referenced_subreddit = re.split('[^a-zA-Z0-9_]', body)[0].lower()
            if referenced_subreddit not in subreddits:
                subreddits[referenced_subreddit] = r.subreddit(referenced_subreddit).subscribers

            if referenced_subreddit != "" and referenced_subreddit != this_subreddit:
                subreddit_tuple = tuple(
                    sorted((this_subreddit, re.split('[^a-zA-Z0-9_]', body)[0].lower())))
                subreddit_edges[subreddit_tuple] += 1
pprint(subreddit_edges)
pprint(subreddits)
