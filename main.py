import os
import io
import nextcord
import matplotlib.pyplot as plot
from pyterri import clan as pyterri_clan
from pymongo import MongoClient
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands

client = commands.Bot()
db = MongoClient(os.environ["DB_URL"])["scorekeeper-db"]["scorekeeper-db"]

GUILD_IDS = list()
for i in client.guilds:
    GUILD_IDS.append(i.id)

@client.event
async def on_ready():
    print("bot is online")

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

    """
    with open("plot.png", "rb") as f:
        img = nextcord.File(f)
    
    os.remove("plot.png")
    """

    embed = nextcord.Embed(title = f"Top {limit} clans", color = nextcord.Color.blurple())
    embed.set_image(url = "attachment://plot.png")

    for clandata in data:
        embed.add_field(name = f"{clandata['rank']}. {clandata['clan'].upper()}", value = clandata["score"])

    await interaction.response.send_message(embed = embed, file = img)
    plot.clf()

@client.slash_command(name = "setupdatechannel", description = "Set the channel where the scorekeeper will send update messages", guild_ids = GUILD_IDS)
async def setupdatechannel(interaction: Interaction, channel: GuildChannel):
    db.update_one({"_id": "update_channels"}, {"$set": {str(interaction.guild.id): str(channel.id)}})
    await interaction.response.send_message(f":white_check_mark: Set update channel to {GuildChannel}")

client.run(os.environ["CLIENT_TOKEN"])