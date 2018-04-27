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
processed_subreddits = set()
subreddits = r.subreddits.popular(limit=None)


def process_subreddit(subreddit, depth=0):
    if depth > 2:
        return

    this_subreddit = subreddit.display_name.lower()
    if this_subreddit in processed_subreddits or subreddit.subscribers < 1000:
        return
    else:
        processed_subreddits.add(this_subreddit)

    descriptions = subreddit.description.split('/r/')
    iter_descriptions = iter(descriptions)
    next(iter_descriptions)
    for description in iter_descriptions:
        referenced_subreddit = re.split('[^a-zA-Z0-9_]', description)[0].lower()
        if referenced_subreddit == "" or this_subreddit == referenced_subreddit:
            continue
        subreddit_edges[tuple(sorted((this_subreddit, referenced_subreddit)))] += 1

        # process_subreddit(r.subreddit(referenced_subreddit), depth + 1)

    submit_texts = subreddit.submit_text.split('/r/')
    iter_submit_texts = iter(submit_texts)
    next(iter_submit_texts)
    for submit_text in iter_submit_texts:
        referenced_subreddit = re.split('[^a-zA-Z0-9_]', submit_text)[0].lower()
        if referenced_subreddit == "" or this_subreddit == referenced_subreddit:
            continue
        subreddit_edges[tuple(sorted((this_subreddit, referenced_subreddit)))] += 1

        # process_subreddit(r.subreddit(referenced_subreddit), depth + 1)

    print("analyzed", this_subreddit)


# for _ in range(1000):
while True:
    try:
        next_sub = subreddits.next()
    except StopIteration:
        break

    process_subreddit(next_sub)

stream = streamer.Streamer(streamer.GephiWS(workspace="workspace1"))


def add_node(subreddit):
    try:
        size = data.loc[subreddit].norm_subs
        category = data.loc[subreddit].Category
        nsfw = data.loc[subreddit].Over_18
    except KeyError:
        size = 1
        category = ""
        nsfw = False

    if nsfw:
        red, green, blue = 0, 0, 1
    else:
        test_string = abs(hash(category))
        red = 1 - test_string % 524288 / 524288.0
        test_string = test_string / 524288
        green = 1 - test_string % 524288 / 524288.0
        test_string = test_string / 524288
        blue = 1 - test_string % 524288 / 524288.0

    return graph.Node(subreddit, label=subreddit, red=red, green=green, blue=blue, size=size)


for key, value in subreddit_edges.items():
    subreddit_a = add_node(key[0])
    subreddit_b = add_node(key[1])

    connection = graph.Edge(subreddit_a, subreddit_b, directed=False, weight=value)

    stream.add_node(subreddit_a, subreddit_b)
    stream.add_edge(connection)
