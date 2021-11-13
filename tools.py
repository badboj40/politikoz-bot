# tools.py
import requests
import json as jjson
import discord
import time

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
    poolpm_link = f"https://pool.pm/6f80b47342de4b8d534d4fe59d8995471154ff5b416a9e46723440a4.Politikoz{asset['name'][-5:]}"
    date_and_time = time.strftime(
        "%Y-%m-%d %H:%M:%S UTC", time.localtime(asset["dateSold"] / 1e3)
    )
    image_url = f"https://ipfs.io/ipfs/{asset['thumbnail'][7:]}"

    embedVar = discord.Embed(
        title=f"{asset['name']}",
        url=poolpm_link,
        color=colors[asset["type"]],
        description=date_and_time,
    )

    embedVar.set_author(
        name="Politikoz",
        url="https://politikoz.io/",
        icon_url="https://politikoz.io/static/media/logo.73866ab2.png",
    )

    embedVar.set_image(url=image_url)
    embedVar.add_field(name="Price", value=f"{asset['price']} ₳")
    embedVar.set_footer(text="Brought to you by Gustav#5942")
    return embedVar


def get_assets(settings):
    url = "https://api.cnft.io/market/listings"
    assets = []
    page = 1

    while True:
        print(f"Getting page: {page}")
        if page > settings["max pages"]:
            break
        params = {
            "project": "Politikoz",
            "sort": settings["sort"],
            "page": page,
            "verified": "true",
        }
        if settings["sold"] == "true":
            params["sold"] = "true"

        r = requests.post(url, params).json()

        try:
            if len(r["assets"]) == 0:
                print("got all assets")
                break
            for asset in r["assets"]:
                new_asset = dict()
                new_asset["nameId"] = asset["nameId"]
                new_asset["name"] = asset["metadata"]["name"]
                new_asset["type"] = asset["metadata"]["name"][:-7]
                new_asset["price"] = int(asset["price"] / 1e6)
                new_asset["attributes"] = asset["metadata"]["tags"][1]["attributes"]
                new_asset["thumbnail"] = asset["metadata"]["image"]
                new_asset["link"] = f"https://cnft.io/token.php?id={asset['id']}"
                if settings["sold"] == "true":
                    new_asset["dateSold"] = asset["dateSold"]
                assets.append(new_asset)
            page += 1
        except:
            assets = []
            page = 1
    return assets


def save_to_file(assets):
    with open("politikoz.json", "w+") as fout:
        jjson.dump(assets, fout)


def read_from_file():
    with open("politikoz.json", "r") as f:
        assets = jjson.loads(f.read())
    return assets


def get_floor(attributes):
    assets = sorted(read_from_file(), key=lambda i: i["price"])
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

    longest_name = 0
    for cat in categories.keys():
        if len(cat) > longest_name:
            longest_name = len(cat)

    floor_prices = "Current floor prices:\n```"
    for cat in categories:
        catt = cat.title() + ":"
        if len(categories[cat]) > 0:
            floor = categories[cat][0]
            floor_prices += (
                f"{catt:<{longest_name+1}}{floor['price']:>7} ₳\t({floor['name']})\n"
            )
        else:
            floor_prices += f"{catt:<{longest_name+1}} none availabe\n"
    return floor_prices[:-1] + "\n\nBrought to you by Gustav#5942```"
