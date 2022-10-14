from optparse import TitledHelpFormatter
import os
import nextcord
from pyterri import clan as pyterri_clan
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands

client = commands.Bot()

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
async def clan(interaction: Interaction, arg: str):
    try:
        data = pyterri_clan.getClan(arg)
        embed = nextcord.Embed(title = arg.upper(), color = nextcord.Color.blue())
        embed.add_field(name = "Rank", value = data["rank"])
        embed.add_field(name = "Score", value = data["score"])
    except IndexError:
        embed = nextcord.Embed(title = arg.upper(), description = "No data was found for this clan, most likely because it does not have a recorded score.", color = nextcord.Color.red())
    except TypeError:
        embed = nextcord.Embed(title = arg.upper(), description = "No data was found for this clan, most likely because it does not have a recorded score.", color = nextcord.Color.red())

    await interaction.response.send_message(embed = embed)

client.run(os.environ["CLIENT_TOKEN"])