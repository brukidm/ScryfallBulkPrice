import discord
import os

import requests
import re
import json

def request_url(name):
    name = name.replace(" ", "+")
    return f"https://api.scryfall.com/cards/search?q={name}&order=eur&dir=asc"

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$bulkprice'):
        entries = message.content.split("\n")
        command = entries[0]
        entries = entries[1:]
        total_price = 0
        cards = {}
        for line in entries:
            amount, name = re.split(r"\s+", line, 1)
            resp = requests.get(request_url(name))
            data = json.loads(resp.content)
            if not resp.status_code == 200:
                continue
            if data["data"][0]["prices"]["eur"]:
                value = float(data["data"][0]["prices"]["eur"])
                if "round" in command:
                  if value < 0.13:
                    value = 0.13
                price =  value * int(amount)
                cards[name] = (amount, price)
                total_price += price
        if total_price > 0:
          await message.channel.send(f"Total: {total_price} €")

client.run(os.getenv('TOKEN'))
