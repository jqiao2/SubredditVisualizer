import pandas as pd
import praw

# Make your own profile file with all these variables for oauth 2
from Profile import ID
from Profile import PASSWORD
from Profile import SECRET
from Profile import USERNAME
from Profile import USER_AGENT

# Reddit agent
r = praw.Reddit(client_id=ID, client_secret=SECRET, password=PASSWORD,
                user_agent=USER_AGENT, username=USERNAME)

subreddits = r.subreddits.popular(limit=None)

subreddit_list = []
for i in range(10000):
    try:
        subreddit = subreddits.next()
    except StopIteration:
        break

    row = {"Subreddit": subreddit.display_name.lower(), "Subscribers": subreddit.subscribers,
           "Category": subreddit.advertiser_category, "Over_18": subreddit.over18}
    subreddit_list.append(row)

pd.DataFrame(subreddit_list, columns=["Subreddit", "Subscribers", "Category", "Over_18"]).to_csv("subreddits.csv")
