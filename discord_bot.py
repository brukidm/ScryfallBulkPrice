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

    if "$cicija" in message.content or "$lujo" in message.content:
        # separate the command from the card list
        entries = message.content.split("\n")
        command = entries[0]
        entries = entries[1:]
        total_price = 0
        under_13 = 0
        cards = {}
        to_print = "" # additional messages that might be shown
        for line in entries:
            try:
                if not line[0].isdigit():
                    line = "1 " + line
                amount, name = re.split(r"\s+", line, 1)
                resp = requests.get(request_url(name))
                data = json.loads(resp.content)
                # incorrect file name etc.
                if not resp.status_code == 200:
                    to_print += f"No price in € found for card {name}\n"
                    continue
                # full text search can yield multiple results
                # this is a way to exclude the wrong cards
                for card in data["data"]:
                    if len(name) == len(card["name"]):
                        card = card
                        break
                # if normal price exists, good
                if card["prices"]["eur"]:
                    value = float(card["prices"]["eur"])
                # if it doesn't, at least check the foil price
                elif card["prices"]["eur_foil"]:
                    value = float(card["prices"]["eur_foil"])
                else:
                    to_print += f"No price in € found for card {name}\n"
                # if the minimal value is found, do some more stuff
                if value:
                    value = round(value, 2)
                    # print the value for each card
                    if "$cicijalist" in command:
                        to_print += f"{name}: {value:.2f} €\n"
                    # round the prices lower than 0.13 to 0.13
                    if "$lujo" in command and name not in ignore_lands:
                        if value < 0.13:
                            # print the cards that are worth less than 0.13 by default
                            if "$lujolist" in command:
                                to_print += f"Rounded up the price for {name} from {value:.2f} €\n"
                                under_13 += 1
                            value = 0.13
                    price = value * int(amount)
                    cards[name] = (amount, price)
                    total_price += price
            except Exception as ex:
                print(ex)
            if total_price > 0:
                if to_print:
                    await message.channel.send(to_print)
                if under_13:
                    await message.channel.send(f"Cards under 0.13€ limit: {under_13}")
                await message.channel.send(f"Total: {round(total_price, 2):.2f} €")

keep_alive()
client.run(os.getenv('TOKEN'))
