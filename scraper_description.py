import re

import pandas as pd
import praw
from prawcore import PrawcoreException

from Profile import ID
from Profile import PASSWORD
from Profile import SECRET
from Profile import USERNAME
from Profile import USER_AGENT

POPULAR_THRESHOLD = 300000
SUBSCRIBER_LIMIT = 1000
DEPTH_RESET_THRESHOLD = 20000

r = praw.Reddit(client_id=ID,
                client_secret=SECRET,
                password=PASSWORD,
                user_agent=USER_AGENT,
                username=USERNAME)

processed_subs = set()
skipped_subreddits = set()
subreddit_data = []


def process():
    data = pd.read_csv("subreddits.csv")
    for index, row in data.iterrows():
        processed_subs.add(row.subreddit)


def process_subreddit(this_sub, subreddit=None, depth=0):
    if depth > 1 or this_sub in processed_subs or (this_sub in skipped_subreddits and depth > 0):
        return

    if subreddit is None:
        try:
            subreddit = r.subreddit(this_sub)
            if subreddit.subscribers < SUBSCRIBER_LIMIT:
                return
        except PrawcoreException:
            return

    if subreddit.subscribers > DEPTH_RESET_THRESHOLD:
        depth = 0

    processed_subs.add(this_sub)
    print("start", this_sub)

    subreddit_data.append({"subreddit": this_sub, "description": subreddit.description, "submit_text": subreddit.submit_text,
                           "subscribers": subreddit.subscribers, "normed_subscribers": max(1.0, pow(subreddit.subscribers, 0.5) / 100),
                           "category": subreddit.advertiser_category, "over_18": subreddit.over18})

    try:
        descriptions = subreddit.description.split('/r/')
        iter_descriptions = iter(descriptions)
        next(iter_descriptions)
        for description in iter_descriptions:
            that_sub = re.split('[^a-zA-Z0-9_]', description)[0].lower()
            if that_sub == "" or this_sub == that_sub:
                continue
            process_subreddit(that_sub, depth=depth + 1)
    except AttributeError:
        print("no description")

    try:
        submit_texts = subreddit.submit_text.split('/r/')
        iter_submit_texts = iter(submit_texts)
        next(iter_submit_texts)
        for submit_text in iter_submit_texts:
            that_sub = re.split('[^a-zA-Z0-9_]', submit_text)[0].lower()
            if that_sub == "" or this_sub == that_sub:
                continue
            process_subreddit(that_sub, depth=depth + 1)
    except AttributeError:
        print("no submit text")


# process()

# let's us skip all these if they appear on the tree of another subreddit
print("analyzing skippable subreddits")
subreddits = r.subreddits.popular(limit=None)
while True:
    try:
        next_sub = subreddits.next()
        skipped_subreddits.add(next_sub.display_name.lower())
    except StopIteration:
        break

print("starting")
subreddits = r.subreddits.popular(limit=None)
while True:
    try:
        next_sub = subreddits.next()
    except StopIteration:
        break

    process_subreddit(next_sub.display_name.lower(), next_sub)

pd.DataFrame(subreddit_data).to_csv("new subreddits.csv")
