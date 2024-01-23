import os
import re
import sys
import json
import time
import feedparser
from mastodon import Mastodon
from bs4 import BeautifulSoup

def strip_html_tags(html_string):
    """
    Strips HTML tags from a given HTML string using BeautifulSoup.

    :param html_string: The HTML string to strip tags from.
    :return: A string with all HTML tags removed.
    """
    soup = BeautifulSoup(html_string, 'html.parser')
    stripped_text = soup.get_text(separator=' ')
    stripped_text = re.sub(' +', ' ', stripped_text)
    return stripped_text

# Change the working directory to the directory of this script
# This ensures that all file paths are relative to this script's location
os.chdir(sys.path[0])

# Load Mastodon credentials from a JSON file
# The JSON file should contain the client_id, client_secret, and access_token
with open("mastodon_credentials.json", "r") as f:
    credentials = json.load(f)
    client_id = credentials["client_id"]
    client_secret = credentials["client_secret"]
    access_token = credentials["access_token"]
    api_base_url = credentials["api_base_url"]

# Create a Mastodon client instance with the loaded credentials
# This allows the script to interact with the Mastodon API
mastodon = Mastodon(
    client_id=client_id,
    client_secret=client_secret,
    access_token=access_token,
    api_base_url=api_base_url
)

# Load RSS feed URLs from a JSON file
# The JSON file should be an array of strings, each string being a feed URL
with open("feed_urls.json", "r") as f:
    feed_urls = json.load(f)

# Load the last checked times for each feed from a JSON file
# The file maps feed URLs to timestamps indicating the last time the feed was checked
try:
    with open("last_checked_times.json", "r") as f:
        last_checked_times = json.load(f)
except FileNotFoundError:
    last_checked_times = {}

# Check each feed for new entries
for feed_url in feed_urls:
    feed = feedparser.parse(feed_url)
    # Determine the number of entries to check
    num_entries_to_check = 5 if feed_url not in last_checked_times else None

    for i, entry in enumerate(feed.entries):
        # Limit the number of entries to check if necessary
        if num_entries_to_check is not None and i >= num_entries_to_check:
            break

        # Convert the entry publish time to a timestamp
        entry_time = time.mktime(entry.published_parsed)

        # Skip entries that were already checked
        if feed_url in last_checked_times and entry_time <= last_checked_times[feed_url]:
            continue

        # Prepare the message to be posted on Mastodon
        # Truncate the summary if it's too long and strip HTML tags
        entry_summary = (entry.summary[:240] + " ..." if len(entry.summary) > 240 else entry.summary)
        message = (f"{strip_html_tags(entry.title)}\n\n"
                   f"{strip_html_tags(entry_summary)}\n\n"
                   f"{entry.link}")

        # Post the message to Mastodon
        mastodon.status_post(message)

        # Update the last checked time for this feed
        last_checked_times[feed_url] = entry_time
        with open("last_checked_times.json", "w") as f:
            json.dump(last_checked_times, f)

