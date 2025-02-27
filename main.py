import discord, os
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

client = commands.Bot(command_prefix=os.getenv("PREFIX"), help_command=None, intents=discord.Intents.all())
allow_cogs = ["tools", "interactions"]

@client.event
async def on_ready():

    # Chargement des cogs
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):

            # Exclusion chargement cogs
            if filename[:-3] not in allow_cogs:

                # Charge la cog
                await client.load_extension(f"cogs.{filename[:-3]}")

    # Slash Commands
    await client.tree.sync()
    print(f"✅ Connecté en tant que {client.user}")

@client.command()
@commands.has_permissions(manage_messages=True)
async def reload(ctx: commands.Context, extension):
    try: await ctx.message.delete()
    except: pass

    if extension in allow_cogs:
        return await ctx.send(f"**{extension.capitalize()}** ne peut être rechargé !", delete_after=2)

    await client.unload_extension(f"cogs.{extension}")
    await client.load_extension(f"cogs.{extension}")
    await ctx.send(f"**{extension.capitalize()}** rechargé !", delete_after=2)


client.run(os.getenv("TOKEN"))