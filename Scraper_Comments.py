import codecs
import csv
import json
import re
from collections import defaultdict

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

subreddit_edges = defaultdict(int)
subreddits_subscribers = {}
limit = 2000000
# with codecs.open('sample_data.json','rU','utf-8') as f:
with codecs.open('/Volumes/Jason Deskt/Reddit/RC_2018-02', 'rU', 'utf-8') as f:
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
            referenced_subreddit = re.split('[^a-zA-Z0-9_]', body)[0].lower()
            if referenced_subreddit != "" and this_subreddit is not referenced_subreddit:
                subreddit_tuple = tuple(
                    sorted((this_subreddit, re.split('[^a-zA-Z0-9_]', body)[0].lower())))
                subreddit_edges[subreddit_tuple] += 1
                # if this_subreddit not in subreddits_subscribers:
                #     subreddits_subscribers[this_subreddit] = r.subreddit(
                #         this_subreddit).subscribers
                # if referenced_subreddit not in subreddits_subscribers:
                #     subreddits_subscribers[referenced_subreddit] = r.subreddit(
                #         referenced_subreddit).subscribers

stream = streamer.Streamer(streamer.GephiWS(workspace="workspace1"))
for key, value in subreddit_edges.items():
    subreddit_a = graph.Node(key[0], Label=key[0])
    subreddit_b = graph.Node(key[1], Label=key[1])
    connection = graph.Edge(subreddit_a, subreddit_b, directed=False, weight=value)

    stream.add_node(subreddit_a, subreddit_b)
    stream.add_edge(connection)

with open('edges.csv', 'wb') as f:
    writer = csv.writer(f)
    for key, value in subreddit_edges.items():
        writer.writerow([key[0], key[1], value])
