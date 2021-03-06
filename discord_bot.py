import discord
import os

import grequests
import requests
import re
import json
from keep_alive import keep_alive

def request_url(name):
    name = name.replace(" ", "+")
    return f"https://api.scryfall.com/cards/search?q={name}&order=eur&dir=asc"

client = discord.Client()

ignore_lands = [
    "Snow-Covered Island",
    "Snow-Covered Swamp",
    "Snow-Covered Forest",
    "Snow-Covered Mountain",
    "Snow-Covered Plains",
    "Island",
    "Swamp",
    "Forest",
    "Mountain",
    "Plains"
]

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "!pdlegal" in message.content:
      entries = message.content.split("\n")
      if len(entries) == 1:
        to_check = re.split(r"\s+", entries[0], 1)
        name = to_check[1]
        url_to_send = request_url(name)
        r = requests.get(url_to_send)
        r = r.json()
        if "not_legal" in r["data"][0]["legalities"]["penny"]:
          await message.channel.send("```\n" + "Not legal!" + "\n```")
        else:
          await message.channel.send("```\n" + "Legal!" + "\n```")
    if "$cicija" in message.content or "$lujo" in message.content:
        # separate the command from the card list
        entries = message.content.split("\n")
        command = entries[0]
        entries = entries[1:]
        total_price = 0
        under_13 = 0
        cards = {}
        to_print = "" # additional messages that might be shown
        try:
            for line in entries:
                if not line[0].isdigit():
                    line = "1 " + line
                amount, name = re.split(r"\s+", line, 1)
                url_to_send = request_url(name)
                cards[url_to_send] = amount, name
            rs = (grequests.get(u) for u in cards.keys())
            responses = grequests.map(rs)
            for resp in responses:
                amount, name = cards[resp.url]
                data = json.loads(resp.content)
                # incorrect file name etc.
                if not resp.status_code == 200:
                    to_print += f"No price in ??? found for card {name}\n"
                    continue
                # full text search can yield multiple results
                # this is a way to exclude the wrong cards
                for card in data["data"]:
                    if len(name) == len(card["name"]):
                        card = card
                        break
                name = card["name"]
                # if normal price exists, good
                if card["prices"]["eur"]:
                    value = float(card["prices"]["eur"])
                # if it doesn't, at least check the foil price
                elif card["prices"]["eur_foil"]:
                    value = float(card["prices"]["eur_foil"])
                else:
                    to_print += f"No price in ??? found for card {name}\n"
                # if the minimal value is found, do some more stuff
                if value:
                    value = round(value, 2)
                    # print the value for each card
                    if "$cicijalist" in command:
                        to_print += f"{name}: {value:.2f} ???\n"
                    # round the prices lower than 0.13 to 0.13
                    if "$lujo" in command and name not in ignore_lands:
                        if value < 0.13:
                            # print the cards that are worth less than 0.13 by default
                            if "$lujolist" in command:
                                to_print += f"Rounded up the price for {name} from {value:.2f} ???\n"
                                under_13 += 1
                            value = 0.13
                    price = value * int(amount)
                    total_price += price
        except Exception as ex:
            print(ex)
        if total_price > 0:
            if to_print:
                await message.channel.send("```\n" + to_print + "\n```")
            if under_13:
                await message.channel.send(f"```\nCards under 0.13??? limit: {under_13}\n```")
            await message.channel.send(f"```\nTotal: {round(total_price, 2):.2f} ???\n```")

keep_alive()
client.run(os.getenv('TOKEN'))
