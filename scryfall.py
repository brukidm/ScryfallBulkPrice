import requests
import re
import json

def request_url(name):
    name = name.replace(" ", "+")
    return f"https://api.scryfall.com/cards/named?fuzzy={name}&prices=eur"

with open(r"buylist.txt") as f:
    lines = f.read().split('\n')
    total_price = 0
    cards = {}
    for line in lines:
        amount, name = re.split(r"\s+", line, 1)
        resp = requests.get(request_url(name))
        data = json.loads(resp.content)
        if not resp.status_code == 200:
            print(f"Card {name} doesn't exist.")
            continue
        if data["prices"]["eur"]:
            price = float(data["prices"]["eur"]) * int(amount)
            cards[name] = (amount, price)
            total_price += price
        else:
            print(f"Price not found for {name}.")
    for name, value in cards.items():
        print(f'{value[0]} {name}: {round(value[1], 2)}€')
    print("Total: ", total_price, "€")