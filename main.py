import os
import io
import nextcord
import matplotlib.pyplot as plot
from pyterri import clan as pyterri_clan
from operator import itemgetter
from pymongo import MongoClient
from nextcord import Interaction
from nextcord.ext import commands

intents = nextcord.Intents.all()
intents.messages = True
client = commands.Bot(intents = intents)

cluster = MongoClient(os.environ["DB_URL"])
collection = cluster["scorekeeper-db"]["scorekeeper-db"]
roblocdb = cluster["robloc"]

GUILD_IDS = list()
for i in client.guilds:
    GUILD_IDS.append(i.id)

ROBLOC = [1038582742700527826]

# Events
@client.event
async def on_ready():
    print("bot is online")

@client.event
async def on_message(message):
    userid = str(message.author.id)
    collist = roblocdb.list_collection_names()

    if userid in collist:
        usercol = roblocdb[userid]
        data = usercol.find_one()
        lvl_increase_requirement = 100 + (data["lvl"] * 10)

        try:
            xp_increase = len(message.content) // data["lvl"]
        except ZeroDivisionError:
            xp_increase = len(message.content)

        if xp_increase == 0:
            xp_increase = 1

        usercol.update_one({"xp": data["xp"]}, {"$set": {"xp": data["xp"] + xp_increase}})
        data = usercol.find_one()
        print(f"[xp log] {message.author.name} [{data['xp'] - xp_increase} -> {data['xp']}]\n    xp: {xp_increase}\n    chars: {len(message.content)}\n    id: {message.author.id}\n")

        if data["xp"] >= lvl_increase_requirement:
            usercol.update_one({"lvl": data["lvl"]}, {"$set": {"lvl": data["lvl"] + 1}})
            usercol.update_one({"xp": data["xp"]}, {"$set": {"xp": 0}})
            data = usercol.find_one()

            await message.channel.send(f":partying_face: <@{message.author.id}> just leveled up! [{data['lvl'] - 1} -> **{data['lvl']}**]")
            print(f"[lvl log] {message.author.name} [{data['lvl'] - 1} -> {data['lvl']}]\n    id: {message.author.id}\n")

# Global commands
@client.slash_command(name = "help", description = "A good place to get started with the scorekeeper", guild_ids = GUILD_IDS)
async def ping(interaction: Interaction):
    embed = nextcord.Embed(title = "Help", description = "empty for now")
    await interaction.response.send_message(embed = embed)

@client.slash_command(name = "clan", description = "Get score and rank for a clan", guild_ids = GUILD_IDS)
async def clan(interaction: Interaction, tag: str):
    try:
        data = pyterri_clan.getClan(tag)
        embed = nextcord.Embed(title = tag.upper(), color = nextcord.Color.blue())
        embed.add_field(name = "Rank", value = data["rank"])
        embed.add_field(name = "Score", value = data["score"])
    except IndexError:
        embed = nextcord.Embed(title = tag.upper(), description = "No data was found for this clan, most likely because it does not have a recorded score.", color = nextcord.Color.red())
    except TypeError:
        embed = nextcord.Embed(title = tag.upper(), description = "No data was found for this clan, most likely because it does not have a recorded score.", color = nextcord.Color.red())

    await interaction.response.send_message(embed = embed)

@client.slash_command(name = "lb", description = "Get the clan leaderboard", guild_ids = GUILD_IDS)
async def lb(interaction: Interaction, limit: int = 0):
    if (limit != 0) and (limit <= 25):
        data = pyterri_clan.getClans(limit = limit)
    elif limit > 25:
        await interaction.response.send_message(embed = nextcord.Embed(title = "Invalid limit provided", description = "Due to discord constraints no more than the top 25 clans can be displayed.", color = nextcord.Color.red()))
    else:
        data = pyterri_clan.getClans(limit = 10)

    # Create graph
    graph_clanlist = list()
    graph_scorelist = list()
    for i in data:
        graph_clanlist.append(i["clan"])
        graph_scorelist.append(float(i["score"]))

    plot.bar(graph_clanlist, graph_scorelist)
    plot.title(f"Visualization")
    plot.xlabel("Clan")
    plot.ylabel("Score")

    data_stream = io.BytesIO()
    plot.savefig(data_stream, format = "png")
    data_stream.seek(0)
    img = nextcord.File(data_stream, filename = "plot.png")

    embed = nextcord.Embed(title = f"Top {limit} clans", color = nextcord.Color.blurple())
    embed.set_image(url = "attachment://plot.png")

    for clandata in data:
        embed.add_field(name = f"{clandata['rank']}. {clandata['clan'].upper()}", value = clandata["score"])

    await interaction.response.send_message(embed = embed, file = img)
    plot.clf()

@client.slash_command(name = "time", description = "in development", guild_ids = GUILD_IDS)
async def time(interaction: Interaction, clan: str):
    if clan.upper() != "EXAMPLE":
        await interaction.response.send_message("clan must be `EXAMPLE` for now")
        return
    else:
        document = collection.find({"clan": clan.upper()})
        graph_indexes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        graph_points = document["scores"]

        plot.plot(graph_indexes, graph_points)
        plot.title(f"Score over time: {clan.upper()}")
        plot.xlabel("Time")
        plot.ylabel("Score")

        data_stream = io.BytesIO()
        plot.savefig(data_stream, format = "png")
        data_stream.seek(0)
        img = nextcord.File(data_stream, filename = "plot.png")

        embed = nextcord.Embed(title = f"Score over time for {clan.upper()}", color = nextcord.Color.blurple())
        embed.set_image(url = "attachment://plot.png")

        await interaction.response.send_message(embed = embed, file = img)
        plot.clf()


# ROBLOC COMMANDS
@client.slash_command(name = "escuminac", description = "heheheha", guild_ids = ROBLOC)
async def escuminac(interaction: Interaction):
    if interaction.channel.id == 1038795433465626774:
        await interaction.response.send_message("It's time to ping **escuminac!!!**")
        for i in range(20):
            await interaction.channel.send(f"hi <@{946786939200208937}> (ping **#{i + 1}** of 20)")

        await interaction.channel.send(":white_check_mark: Escuminac has been pinged")

    else:
        channel = client.get_channel(1038795433465626774)
        await interaction.response.send_message(f"if you want to ping escuminac, please go to {channel.mention} and try again")

@client.slash_command(name = "level", description = "Get a user's level", guild_ids = ROBLOC)
async def level(interaction: Interaction, user: nextcord.Member = None):
    if user == None:
        user = interaction.user

    if user.nick == None:
        name = user.name
    else:
        name = user.nick

    data = roblocdb[str(user.id)].find_one()
    embed = nextcord.Embed(title = f"{name}'s stats")
    embed.add_field(name = "Level", value = data["lvl"])
    embed.add_field(name = "XP", value = data["xp"])
    embed.add_field(name = "Required XP", value = (100 + (data["lvl"] * 10)))

    await interaction.response.send_message(embed = embed)

@client.slash_command(name = "levelstart", description = "The bot will start tracking your messages and levels!", guild_ids = ROBLOC)
async def levelstart(interaction: Interaction):
    collist = roblocdb.list_collection_names()
    userid = str(interaction.user.id)

    if userid in collist:
        await interaction.response.send_message(":joy: You're already in the database!")
    else:
        usercol = roblocdb[str(interaction.user.id)]
        usercol.insert_one({"_id": "lvldata", "lvl": 0, "xp": 0})

        await interaction.response.send_message(":white_check_mark: Done")

@client.slash_command(name = "xp_leaderboard", description = "It kinda speaks for itself")
async def xp_leaderboard(interaction: Interaction):
    lb = list()
    for collection in roblocdb.list_collection_names():
        data = roblocdb[collection].find_one()
        lb.append({"userid": collection, "lvl": data["lvl"], "xp": data["xp"]})

    lb = sorted(lb, key = itemgetter("lvl", "xp"), reverse = True)
    lb_message = ""
    
    idx = 0
    for i in lb:
        idx += 1

        match idx:
            case 1:
                lb_message += f":first_place: <@{i['userid']}> {i['xp']}XP | **LVL{i['lvl']}**"
            case 2:
                lb_message += f":second_place: <@{i['userid']}> {i['xp']}XP | **LVL{i['lvl']}**"
            case 3:
                lb_message += f":third_place: <@{i['userid']}> {i['xp']}XP | **LVL{i['lvl']}**"
            case other:
                lb_message += f"{idx}. <@{i['userid']}> {i['xp']}XP | **LVL{i['lvl']}**"
        
        if idx - 1 != len(lb):
            lb_message += "\n"

    embed = nextcord.Embed(title = "XP Leaderboard", description = lb_message)
    await interaction.response.send_message(embed = embed)

client.run(os.environ["CLIENT_TOKEN"])