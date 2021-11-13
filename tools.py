# tools.py
import requests
import json as jjson
import discord
import time
from datetime import datetime
from calendar import timegm

colors = {
    "President": 0x6CAB5C,
    "Senator": 0x947CD3,
    "Minister": 0x85CCFB,
    "Governor": 0xFBFBCC,
    "Federal Deputy": 0xFA8483,
    "State Deputy": 0xFBDB8D,
    "Mayor": 0xDCBBF4,
    "Councilor": 0xC3C3C3,
}


def format_message(asset):
    embedVar = discord.Embed(
        title=f"{asset['name']}",
        url=asset['pool_link'],
        color=colors[asset['type']],
        timestamp=datetime.strptime(asset['soldAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
    )
    attribute_string = ""
    for attribute in asset['attributes']:
        attribute_string += f"{attribute}\n"

    embedVar.add_field(name=f"Price", value=f"₳ {asset['price']}", inline=True)
    embedVar.add_field(name=f"Attributes", value=attribute_string, inline=True)
    embedVar.set_image(url=asset['thumbnail'])
    embedVar.set_footer(text="Brought to you by Gustav#5942")
    return embedVar


def get_assets(settings):
    url = "https://api.cnft.io/market/listings"
    assets = []
    page = 1

    print(f"Getting data from cnft.io", datetime.now())
    while page <= settings["max pages"]:
        params = {
            "project": "Politikoz",
            "page": page,
            "verified": "true",
        }
        if settings["sold"] == "true":
            params["sold"] = "true"

        r = requests.post(url, params).json()

        try:
            if len(r["results"]) == 0:
                print("got all assets")
                break
            for result in r["results"]:
                asset = result['asset']
                new_asset = {
                    'name'          : asset['metadata']['name'],
                    'type'          : asset['metadata']['name'][:-7],
                    'price'         : int(result['price'] / 1e6),
                    'attributes'    : asset['metadata']['attributes'],
                    'thumbnail'     : f"https://ipfs.io/ipfs/{asset['metadata']['image'][7:]}",
                    'cnft_link'     : f"https://cnft.io/token/{result['_id']}",
                    'pool_link'     : f"https://pool.pm/6f80b47342de4b8d534d4fe59d8995471154ff5b416a9e46723440a4.{asset['assetId']}",
                    'listing_type'  : result['type'],
                }

                if settings["sold"] == "true":
                    new_asset['soldAt'] = result['soldAt']
                    utc_time = time.strptime(result['soldAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    epoch_time = timegm(utc_time)
                    new_asset['epoch_time'] = epoch_time 
                assets.append(new_asset)
                #assets.append(result)
            page += 1
        except:
            print('error with asset', new_asset)
            save_to_file([new_asset])
            assets = []
            page += 1

    print(f"Got all data!", datetime.now())
    return assets


def save_to_file(assets):
    with open("politikoz.json", "w+") as fout:
        jjson.dump(assets, fout, indent=4)


def read_from_file():
    with open("politikoz.json", "r") as f:
        assets = jjson.loads(f.read())
    return assets


def get_floor(attributes):
    all_assets = sorted(read_from_file(), key=lambda i: i["price"])
    assets = []
    for asset in all_assets:
        if asset['listing_type'] != 'auction':
            assets.append(asset)

    types = [
        "President",
        "Senator",
        "Minister",
        "Governor",
        "Federal Deputy",
        "State Deputy",
        "Mayor",
        "Councilor",
    ]

    if attributes:
        attributes = [attr.strip() for attr in attributes.split(",")]

    categories = dict()
    if not attributes:
        for typ in types:
            categories[typ.lower()] = []
    else:
        for attribute in attributes:
            if attribute.lower() == "types":
                for typ in types:
                    categories[typ.lower()] = []
            elif attribute.lower() == "attributes":
                for i in range(7):
                    categories[f"{i} Attributes"] = []
            elif attribute[0].isdigit():
                categories[f"{attribute[0]} Attributes"] = []
            else:
                categories[attribute.lower()] = []

    for asset in assets:
        if asset["type"].lower() in (cat.lower() for cat in categories.keys()):
            categories[asset["type"].lower()].append(asset)
        for attribute in attributes:
            if "&" in attribute:
                attrs = [attr.strip() for attr in attribute.split("&")]
                matching = True
                for attr in attrs:
                    if not (
                        attr[0].isdigit()
                        and len(asset["attributes"]) == int(attr[0])
                        or asset["type"].lower() == attr.lower()
                        or attr.lower() in (att.lower() for att in asset["attributes"])
                    ):
                        matching = False
                        break
                if matching:
                    categories[attribute.lower()].append(asset)

            elif attribute.lower() == "types":
                categories[asset["type"].lower()].append(asset)
            elif attribute.lower() == "attributes":
                for i in range(7):
                    if len(asset["attributes"]) == i:
                        categories[f"{i} Attributes"].append(asset)
            elif attribute[0].isdigit() and len(asset["attributes"]) == int(
                attribute[0]
            ):
                categories[f"{attribute[0]} Attributes"].append(asset)

            elif attribute.lower() in (attr.lower() for attr in asset["attributes"]):
                categories[attribute.lower()].append(asset)


    category_string = ""
    price_string = ""
    name_string = ""

    for cat in categories:
        category_string += f"{cat.title()} \u200b \u200b \u200b \u200b\n"
        if len(categories[cat]) > 0:
            floor = categories[cat][0]
            price_string += f"₳ {floor['price']} \u200b \u200b \u200b \u200b\n"
            name_string += f"[{floor['name']}]({floor['cnft_link']})\n"
        else:
            price_string += "none available\n"
            name_string += "\u200b \u200b\n"

    embedVar = discord.Embed(
        color=0x000000,
        timestamp=datetime.utcnow()
    )

    embedVar.add_field(name="Current Floor", value=category_string, inline=True)
    embedVar.add_field(name="\u200b", value=price_string, inline=True)
    embedVar.add_field(name="\u200b", value=name_string, inline=True)
    embedVar.set_footer(text="Brought to you by Gustav#5942")
    return embedVar



if __name__ == "__main__":
    settings_all_assets = {
        'max pages': 1,
        'sold' : 'false'
    }
    assets = get_assets(settings_all_assets)
    save_to_file(assets)
