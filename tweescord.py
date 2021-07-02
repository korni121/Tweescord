import asyncio
import config
import requests
import socket
import time
import tweepy
import urllib3
from discord.ext import commands

# TWITTER API

# method to filter out retweets


def from_creator(status):
    if hasattr(status, 'retweeted_status'):
        return False
    elif status.in_reply_to_status_id is not None:
        return False
    elif status.in_reply_to_screen_name is not None:
        return False
    elif status.in_reply_to_user_id is not None:
        return False
    else:
        return True

# StreamListener class


class MyStreamListener(tweepy.StreamListener):

    def __init__(self, api):
        super().__init__(api)
        self.api = api

    def on_status(self, status):
        name = status.user.name
        text = status.text
        id = status.id
        if from_creator(status):
            send_fut = asyncio.run_coroutine_threadsafe(post_tweet(name, text, id), bot.loop)
            send_fut.result()

    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            return False

    def on_exception(self, exception):
        while True:
            print(exception)
            print("snoozing...")
            time.sleep(10)
            main()


# main method creating stream listener object


def main():
    # list with IDs of people you want to follow
    following = ["44196397",    # Elon Musk
                 "783214",      # Twitter
                 "50393960",    # Bill Gates
                 "10228272",    # Youtube
                 "11348282"]    # NASA
    try:
        auth = tweepy.OAuthHandler(config.api_key, config.api_secret)
        auth.set_access_token(config.access_token, config.access_token_secret)

        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        listener = MyStreamListener(api)
        stream = tweepy.Stream(api.auth, listener, timeout=60)
        stream.filter(follow=following, is_async=True)

    except(requests.exceptions.RequestException, socket.timeout, socket.error,
           urllib3.exceptions.ReadTimeoutError, urllib3.exceptions.SSLError,
           urllib3.exceptions.TimeoutError, RuntimeError) as err:
        print(f"Ooops! Something went wrong.{err}")
        print(err.__doc__)


# DISCORD BOT

bot = commands.Bot(command_prefix="$")


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
# placeholder command
async def hello(ctx):
    await ctx.send('Hello!')


@bot.event
async def post_tweet(name, text, id):
    # here goes your channel id
    channel = bot.get_channel(844366850804809738)
    await channel.send(f"New tweet!\nFrom {name}:\n{text}\n"
                       f"https://twitter.com/twitter/statuses/{id}")

if __name__ == '__main__':
    main()
    bot.run(config.dc_token)
