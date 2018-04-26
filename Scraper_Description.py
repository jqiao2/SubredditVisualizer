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
subreddits = r.subreddits.popular(limit=2000000)
for _ in range(1000):
    try:
        subreddit = subreddits.next()
    except StopIteration:
        break
    this_subreddit = subreddit.display_name.lower()

    descriptions = subreddit.description.split('/r/')
    iter_descriptions = iter(descriptions)
    next(iter_descriptions)
    for description in iter_descriptions:
        referenced_subreddit = re.split('[^a-zA-Z0-9_]', description)[0].lower()
        if referenced_subreddit == "" or this_subreddit == referenced_subreddit:
            continue
        subreddit_edges[tuple(sorted((this_subreddit, referenced_subreddit)))] += 1

    submit_texts = subreddit.submit_text.split('/r/')
    iter_submit_texts = iter(submit_texts)
    next(iter_submit_texts)
    for submit_text in iter_submit_texts:
        referenced_subreddit = re.split('[^a-zA-Z0-9_]', submit_text)[0].lower()
        if referenced_subreddit == "" or this_subreddit == referenced_subreddit:
            continue
        subreddit_edges[tuple(sorted((this_subreddit, referenced_subreddit)))] += 1

    print("analyzed", this_subreddit)

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
