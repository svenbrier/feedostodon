# This script checks RSS feeds for new entries and posts them to Mastodon.

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
    Strips HTML tags from a string.

    :param html_string: The HTML string to strip tags from.
    :return: The input string with all HTML tags removed.
    """
    # Create a BeautifulSoup object from the HTML string
    soup = BeautifulSoup(html_string, 'html.parser')
    # Get the text content of the HTML, with spaces between tags
    stripped_text = soup.get_text(separator=' ')
    # Remove extra spaces
    stripped_text = re.sub(' +', ' ', stripped_text)
    # Return the stripped text
    return stripped_text


# Change the working directory to the directory of this script
os.chdir(sys.path[0])

# Load the Mastodon access token and instance URL from a JSON file
# The JSON file should contain a dictionary with "access_token"
# and "instance_url" keys.
with open("mastodon_credentials.json", "r") as f:
    credentials = json.load(f)
access_token = credentials["access_token"]
instance_url = credentials["instance_url"]

# Create a Mastodon client
mastodon = Mastodon(access_token=access_token, api_base_url=instance_url)

# Load the feed URLs from a JSON file
# The JSON file should be an array of strings representing the feed URLs.
with open("feed_urls.json", "r") as f:
    feed_urls = json.load(f)

# Load the timestamp for each feed from a JSON file
# The JSON file should be a dictionary mapping feed URLs to timestamps.
# If the file doesn't exist, create an empty dictionary.
try:
    with open("last_checked_times.json", "r") as f:
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
        message = (f"{strip_html_tags(entry.title)}\n\n"
                   f"{strip_html_tags(entry_summary)}\n\n"
                   f"{entry.link}")
        # Post the message to Mastodon.
        mastodon.status_post(message)

        # Update the timestamp for the feed in the file
        last_checked_times[feed_url] = entry_time
        with open("last_checked_times.json", "w") as f:
            json.dump(last_checked_times, f)
