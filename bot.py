import discord
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import re
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
intents.members = True  # Enable the members intent
intents.message_content = True # Enable the message content intent

bot = commands.Bot(command_prefix='!', intents=intents)

room_number = 1

user_channels = {}

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command()
async def odakur(ctx, duration: int, *, users: str):
    global room_number  # Use the global room_number variable
    guild = ctx.guild
    user_id = ctx.author.id

    category = get(guild.categories, name='Study Rooms')

    if not category:
        await ctx.send("Category 'Study Rooms' does not exist.")
        return

    global list_of_rooms
    list_of_rooms = []

    # Create the voice channel with a sequential room number
    global room_name
    room_name = f'GelisimOdasi{room_number}'
    voice_channel = await guild.create_voice_channel(name=room_name, category=category)
    await ctx.send(f"{voice_channel.mention} {duration} dakikalığına kuruldu.")
    room_number += 1  # Increment the room number for the next room
    
    user_channels[user_id] = voice_channel

    # Retrieve the user objects
    user_ids = [int(user_id.strip('<@!>')) for user_id in users.split()]
    global allowed_users
    allowed_users = []
    for usess in user_ids:
        user = guild.get_member(usess)
        if user:
            allowed_users.append(user)

    if not allowed_users:
        await ctx.send("Uygun kullanıcı bulunamadı.")
        return

    # Set permissions for the voice channel
    overwrite = {
        guild.default_role: discord.PermissionOverwrite(connect=False),
    }
    for user in allowed_users:
        overwrite[user] = discord.PermissionOverwrite(connect=True,use_voice_activation=True)
    await voice_channel.edit(overwrites=overwrite)

    # Notify users
    for user in allowed_users:
        await ctx.send(f"{user.mention}, bir çalışma odası senin için oluşturuldu!.")

    # Wait for the specified duration
    await asyncio.sleep(duration * 60)

    # Delete the voice channel
    await voice_channel.delete()
    await ctx.send(f"{voice_channel.name} silindi.")

@bot.command()
async def odasil(ctx, room_name: str):
    guild = ctx.guild
    author = ctx.author

    # Find the voice channel by name
    channel = discord.utils.get(guild.voice_channels, name=room_name)
    
    if channel:
        # Check if the author is a member of the voice channel
        if author in channel.members:
            try:
                await channel.delete()
                await ctx.send(f"{channel.name} silindi.")
            except discord.Forbidden:
                await ctx.send("Silme işlemi başarısız oldu.")
            except discord.HTTPException as e:
                await ctx.send(f"Kanali silerken bir hata oluştu: {e}")
        else:
            await ctx.send("Bu kanalda değilsiniz!")
    else:
        await ctx.send("Ses kanali bulunamadi!")



bot.run(TOKEN)