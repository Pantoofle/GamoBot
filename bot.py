import os
import discord
import random
from discord.ext import commands

from table import *

# Load the bot token
path = os.path.dirname(os.path.abspath(__file__))
TOKEN = ""
with open(path+"/.token", "r") as f:
    TOKEN = f.readline()

DELIMITER = '-'
INDEX_CHAN = "liste-tables"
bot = commands.Bot(command_prefix="!")
tables = {}
index_msg = None


@bot.command()
async def start(ctx, *args):
    global tables
    txt = " ".join(args).split(DELIMITER)
    if len(txt) < 2:
        await ctx.message.delete()
        await ctx.send("Format invalide. Utiliser `!start [liste des joueurs] - [nom de la table]`", delete_after=5)
        return

    name = txt[1]
    players = ctx.message.mentions
    await ctx.send("Création de la table " + name, delete_after=10)

    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
    }

    # Create table
    table_name = "Table " + name
    category = discord.utils.find(
        lambda cat: cat.name == table_name, ctx.guild.categories)
    if not category:
        category = await ctx.guild.create_category(table_name, overwrites=overwrites)
        txt_chan = await ctx.guild.create_text_channel(
            name=table_name,
            category=category
        )
        vocal_chan = await ctx.guild.create_voice_channel(
            name="conversation",
            category=category
        )

        table = Table()
        table.name = table_name
        table.txt_channel = txt_chan
        table.vocal_channel = vocal_chan
        table.category = category
        table.players = players
        await table.update_permissions()

        tables[txt_chan] = table
        await table.start()
        await update_tables(ctx.guild)
    else:
        await ctx.send("Cette table existe déjà. Trouve un autre nom.", delete_after=5)

    await ctx.message.delete()


@bot.command()
async def end(ctx):
    global tables
    if ctx.channel in tables:
        cat = tables[ctx.channel].category
        await ctx.send("Cloture de la table. Merci d'avoir joué !")
        for chan in cat.channels:
            await chan.delete()
        await cat.delete()
        del tables[ctx.channel]
        await update_tables(ctx.guild)
    else:
        await ctx.message.delete()
        await ctx.send("Ce n'est pas une table que je gère. Je vais pas la supprimer.", delete_after=5)


@bot.command()
async def join(ctx, *args):
    global tables
    name = "table-" + "-".join(args)
    chan = discord.utils.find(
        lambda chan: chan.name.lower() == name.lower(), ctx.guild.text_channels)
    if chan is not None:
        table = tables[chan]
        if table.open:
            await table.add_player(ctx.author)
        else:
            await ctx.send("La table est fermée, elle ne prend plus de nouveau joueur", delete_after=5)
    else:
        await ctx.send("La table " + name + " n'existe pas...", delete_after=5)

    await ctx.message.delete()


@bot.command(name="open")
async def open_table(ctx):
    global tables
    if ctx.channel in tables:
        table = tables[ctx.channel]
        table.open = True
        await table.txt_channel.send("La table est maintenant ouverte au public !")
        await update_tables(ctx.guild)
    else:
        await ctx.send("Je ne peux faire ça que dans un chan de table de jeu", delete_after=5)

    await ctx.message.delete()


@bot.command(name="close")
async def close_table(ctx):
    global tables
    if ctx.channel in tables:
        table = tables[ctx.channel]
        table.open = False
        await table.txt_channel.send("La table est maintenant fermée au public !")
        await update_tables(ctx.guild)
    else:
        await ctx.send("Je ne peux faire ça que dans un chan de table de jeu", delete_after=5)

    await ctx.message.delete()


async def update_tables(guild):
    global tables
    global index_msg
    txt = "__**Tables actives : **__"
    for c in tables:
        table = tables[c]
        txt += "\n - "
        txt += table.name
        if not table.open:
            txt += " [FERMÉ]"

    if index_msg is None:
        chan = discord.utils.find(
            lambda c: c.name == INDEX_CHAN, guild.channels)
        index_msg = await chan.send(txt)
    else:
        await index_msg.edit(content=txt)


@bot.command()
async def roll(ctx, txt):
    try:
        n, _, f = txt.partition("d")
        n, f = abs(int(n)), abs(int(f))
        if n == 1:
            await ctx.send("Résultat du dé : **" + str(random.randint(1, f)) + "**")
        else:
            dices = [random.randint(1, f) for _ in range(n)]
            s = sum(dices)
            await ctx.send("Résultat des dés : (**" + "** + **".join([str(v) for v in dices]) + "**) = **" + str(s) + "**")
    except ValueError:
        await ctx.message.delete()
        await ctx.send("Pour lancer des dés : `!roll <nb de dés>d<nombre de faces>`, par exemple `!roll 3d10`", delete_after=5)
        return

bot.run(TOKEN)
