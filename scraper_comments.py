import codecs
import json
import re
from collections import defaultdict

import pandas as pd
import praw
from gephistreamer import graph
from gephistreamer import streamer

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

data = pd.read_csv("normed_subs.csv", index_col=1)

subreddit_edges = defaultdict(int)
limit = 2000000
# with codecs.open('sample_data.json','rU','utf-8') as f:
with codecs.open('/Volumes/Jason Deskt/Reddit/RC_2018-02', 'rU', 'utf-8') as f:
    for index, line in enumerate(f):
        if index == limit:
            break

        post = json.loads(line)
        bodies = post['body'].split('/r/')

        # filter out bots and giant copy-paste comments with subreddits
        author = post['author'].lower()
        if author.endswith('bot') or author.endswith('bot_') or len(bodies) > 10:
            continue

        iter_bodies = iter(bodies)
        next(iter_bodies)
        for body in iter_bodies:
            this_subreddit = post['subreddit'].lower()
            referenced_subreddit = re.split('[^a-zA-Z0-9_]', body)[0].lower()
            if referenced_subreddit == "" or this_subreddit == referenced_subreddit:
                continue

            # blacklist /r/imagesofnetwork because of its spam
            if this_subreddit.startswith("imagesof"):
                continue

            subreddit_tuple = tuple(sorted((this_subreddit, re.split('[^a-zA-Z0-9_]', body)[0].lower())))
            subreddit_edges[subreddit_tuple] += 1

            # if this_subreddit not in subreddits_subscribers:
            #     subreddits_subscribers[this_subreddit] = r.subreddit(this_subreddit).subscribers
            # if referenced_subreddit not in subreddits_subscribers:
            #     subreddits_subscribers[referenced_subreddit] = r.subreddit(referenced_subreddit).subscribers

stream = streamer.Streamer(streamer.GephiWS(workspace="workspace1"))
for key, value in subreddit_edges.items():
    try:
        size_a = data.loc[key[0]].norm_subs
    except KeyError:
        size_a = 1
    try:
        size_b = data.loc[key[1]].norm_subs
    except KeyError:
        size_b = 1

    subreddit_a = graph.Node(key[0], Label=key[0], size=size_a)
    subreddit_b = graph.Node(key[1], Label=key[1], size=size_b)

    connection = graph.Edge(subreddit_a, subreddit_b, directed=False, weight=value)

    stream.add_node(subreddit_a, subreddit_b)
    stream.add_edge(connection)
