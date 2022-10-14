import os
import nextcord
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands

client = commands.Bot()

GUILD_ID = 785366147331129355

@client.event
async def on_ready():
    print("bot is online")

@client.slash_command(name = "help", description = "A good place to get started with the scorekeeper", guild_ids = [GUILD_ID])
async def ping(interaction: Interaction):
    embed = nextcord.Embed(title = "Help", description = "empty for now")
    await interaction.response.send_message(embed = embed)

client.run(os.environ["CLIENT_TOKEN"])