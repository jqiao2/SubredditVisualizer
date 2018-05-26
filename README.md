# SubredditVisualizer

This visualizer uses [PRAW](https://github.com/praw-dev/praw), [GephiStreamer](https://github.com/totetmatt/GephiStreamer), and [Sigma](https://github.com/jacomyal/sigma.js/), written in Python/JS, and utilizes [Gephi](https://github.com/gephi/gephi).

This subreddit visualizer attempts to map (almost) all subreddits on reddit.com using description and submit text mentions as a way of connecting subreddits.

Plans on creating a comment-mentions version is in the works.

Below is the workflow on creating the final product:

1. scraper_description.py pulls subreddit information using Reddit's API (specifically: subreddit name, description, submit text, subscriber count, advertise category, and its over18 boolean) and saves them to "new subreddits.csv." It will recursively pull information on subreddits that show up in another subreddit's description or submit text and finishes when the subreddit's subscriber count is below DEPTH_RESET_THRESHOLD (default: 20000).

2. data_grapher.py processes the text (description and submit text) to find mentions of subreddits. It creates edges weighted by number of mentions between nodes (subreddits) and streams them to a Gephi server using GephiStreamer.

3. All nodes not part of the biggest connected component are removed (This is to prevent little components thrown to the side that you cannot see.) and ForceAtlas2 is run on the remaining graph.
