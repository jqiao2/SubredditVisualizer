import re
from collections import defaultdict

import pandas as pd
from gephistreamer import graph
from gephistreamer import streamer

data = pd.read_csv("new subreddits.csv", index_col=6)

subreddit_edges = defaultdict(int)


def process_text(text, this_sub):
    if type(text) != str:
        return
    iter_text = iter(text.split('/r/'))
    next(iter_text)
    for text in iter_text:
        that_sub = re.split('[^a-zA-Z0-9_]', text)[0].lower()
        if that_sub == "" or this_sub == that_sub:
            continue
        subreddit_edges[tuple(sorted((this_sub, that_sub)))] += 1


for this_subreddit, row in data.iterrows():
    process_text(row['description'], this_subreddit)
    process_text(row['submit_text'], this_subreddit)

stream = streamer.Streamer(streamer.GephiWS(workspace="workspace1"))


def add_node(subreddit):
    try:
        size = data.loc[subreddit].normed_subscribers
        category = data.loc[subreddit].category
        nsfw = data.loc[subreddit].over_18
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
