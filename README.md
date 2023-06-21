# feedostodon

This script checks a list of RSS feeds for new entries and posts them to a Mastodon account using the Mastodon API.

## Installation

1. Clone this repository to your local machine.
2. Create a virtual environment and activate it.
3. Install the required packages using `pip install -r requirements.txt`.
4. Create a Mastodon account and obtain an access token.
5. Create a `mastodon_credentials.json` file with the following format:

```json
{
    "access_token": "your_access_token_here",
    "instance_url": "https://your.instance.url"
}
```

6. Create a `feed_urls.json` file with a list of RSS feed URLs to check.

```json
[
    "https://example-one.com/feed",
    "https://example-two.com/rss"
]
```

7. Run the script using `python main.py`.

## Usage

The script will check each feed for new entries and post them to the Mastodon account specified in `mastodon_credentials.json`. The script will remember the last time it checked each feed in `last_checked_times.json` and only post new entries.

## License

This script is licensed under the MIT License. See `LICENSE` for more information.
