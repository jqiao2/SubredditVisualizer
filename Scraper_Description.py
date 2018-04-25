import re
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

subreddit_dict = {}

subreddits = r.subreddits.popular(limit=200)

for _ in range(100):
    try:
        subreddit = subreddits.next()
    except StopIteration:
        break
    pprint(vars(subreddit))

    descriptions = subreddit.description.split('/r/')
    iter_descriptions = iter(descriptions)
    next(iter_descriptions)
    subreddit_edges = defaultdict(int)
    for description in iter_descriptions:
        subreddit_edges[re.split('[^a-zA-Z0-9_]', description)[0].lower()] += 1
    subreddit_dict[subreddit.display_name] = subreddit_edges

print(subreddit_dict)
