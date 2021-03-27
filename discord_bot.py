import discord
import os

import requests
import re
import json
from keep_alive import keep_alive

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
        to_print = ""
        for line in entries:
            amount, name = re.split(r"\s+", line, 1)
            resp = requests.get(request_url(name))
            data = json.loads(resp.content)
            if not resp.status_code == 200:
                message += f"No price in € found for card {name}\n"
                continue
            if data["data"][0]["prices"]["eur"]:
                value = float(data["data"][0]["prices"]["eur"])
                value = round(value, 2)
                if "round" in command:
                  if value < 0.13:
                    value = 0.13
                price =  value * int(amount)
                to_print += f"{name}: {price}€\n"
                cards[name] = (amount, price)
                total_price += price
            else:
              message += f"No price in € found for card {name}\n"
        if total_price > 0:
          await message.channel.send(to_print)
          await message.channel.send(f"Total: {round(total_price, 2)} €")

keep_alive()
client.run(os.getenv('TOKEN'))
