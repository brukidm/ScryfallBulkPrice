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

    if "$cicija" in message.content or "$lujo" in message.content:
        entries = message.content.split("\n")
        command = entries[0]
        entries = entries[1:]
        total_price = 0
        cards = {}
        to_print = ""
        for line in entries:
          try:
            amount, name = re.split(r"\s+", line, 1)
            resp = requests.get(request_url(name))
            data = json.loads(resp.content)
            if not resp.status_code == 200:
              message += f"No price in € found for card {name}\n"
              continue
            for card in data["data"]:
              if len(name) == len(card["name"]):
                card = card
                break
            if card["prices"]["eur"]:
              value = float(card["prices"]["eur"])
            elif card["prices"]["eur_foil"]:
              value = float(card["prices"]["eur_foil"])
            else:
              to_print += f"No price in € found for card {name}\n"
            if value:
              value = round(value, 2)
              if "$cicijalist" in command:
                to_print += f"{name}: {value:.2f} €\n"
              if "$lujo" in command:
                if value < 0.13:
                  if "$lujolist" in command:
                    to_print += f"Rounded up the price for {name} from {value:.2f} €\n"
                  value = 0.13
              price =  value * int(amount)
              cards[name] = (amount, price)
              total_price += price
          except Exception as ex:
            print(ex)
        if total_price > 0:
          if to_print:
            await message.channel.send(to_print)
          await message.channel.send(f"Total: {round(total_price, 2):.2f} €")

keep_alive()
client.run(os.getenv('TOKEN'))
