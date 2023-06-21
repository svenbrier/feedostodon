# This script checks RSS feeds for new entries and posts them to Mastodon.

import os
import json
import feedparser
import time
from mastodon import Mastodon

# Load the Mastodon access token and instance URL from a JSON file
# The JSON file should contain a dictionary with "access_token" and "instance_url" keys.
mastodon_credentials_path = os.path.abspath("mastodon_credentials.json")
with open(mastodon_credentials_path, "r") as f:
    credentials = json.load(f)
access_token = credentials["access_token"]
instance_url = credentials["instance_url"]

# Create a Mastodon client
mastodon = Mastodon(access_token=access_token, api_base_url=instance_url)

# Load the feed URLs from a JSON file
# The JSON file should be an array of strings representing the feed URLs.
feed_urls_path = os.path.abspath("feed_urls.json")
with open(feed_urls_path, "r") as f:
    feed_urls = json.load(f)

# Load the timestamp for each feed from a JSON file
# The JSON file should be a dictionary mapping feed URLs to timestamps.
# If the file doesn't exist, create an empty dictionary.
try:
    last_checked_times_path = os.path.abspath("last_checked_times.json")
    with open(last_checked_times_path, "r") as f:
        last_checked_times = json.load(f)
except FileNotFoundError:
    last_checked_times = {}

# Check each feed for new entries
for feed_url in feed_urls:
    # Parse the feed
    feed = feedparser.parse(feed_url)

    # Get the number of entries to check
    # If the feed has been checked before, check all entries.
    # Otherwise, check only the first 5 entries.
    num_entries_to_check = 5 if feed_url not in last_checked_times else None

    # Check each entry for new entries
    for i, entry in enumerate(feed.entries):
        # Stop checking entries if we've reached the limit
        if num_entries_to_check is not None and i >= num_entries_to_check:
            break

        entry_time = time.mktime(entry.published_parsed)

        # Check if there are any new entries since the last check
        if feed_url in last_checked_times and \
                entry_time <= last_checked_times[feed_url]:
            continue

        # Do something with the new entry
        # Truncate the summary to 240 characters if it's longer than that.
        entry_summary = (entry.summary[:240] + " ..."
                         if len(entry.summary) > 240 else entry.summary)
        # Create a message with the entry title, summary, and link.
        message = f"{entry.title}\n\n{entry_summary}\n\n{entry.link}"
        # Post the message to Mastodon.
        mastodon.status_post(message)

        # Update the timestamp for the feed in the file
        last_checked_times[feed_url] = entry_time
        with open(last_checked_times_path, "w") as f:
            json.dump(last_checked_times, f)
