from aiohttp import web
import os
import asyncio
import discord
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1305798140649017366
ROLE_ID = 1397532181622161568
CHANNEL_ID = 1397541953956216832
PASTEL_PINK = 0xFFC0CB

status_cache = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    status_check.start()

@tasks.loop(seconds=20)
async def status_check():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    role = guild.get_role(ROLE_ID)
    channel = guild.get_channel(CHANNEL_ID)

    for member in guild.members:
        if member.bot or member.status == discord.Status.offline:
            continue

        custom_status = None
        for activity in member.activities or []:
            if isinstance(activity, discord.CustomActivity):
                custom_status = activity.name

        has_dollsick = bool(custom_status and "dollsick" in custom_status.lower())
        had_dollsick_before = status_cache.get(member.id)
        has_role = role in member.roles

        if has_dollsick and not has_role:
            await member.add_roles(role)
            status_cache[member.id] = True
            if channel:
                await channel.send(f"{member.mention}")
                embed = discord.Embed(
                    description=f"<:pusheen:1353024978722750464>  <:002_symbol2:1362146530227912775>   {member.mention} got <@&{ROLE_ID}> for including `/dollsick` in their status.",
                    color=PASTEL_PINK
                )
                await channel.send(embed=embed)

        elif not has_dollsick and has_role and had_dollsick_before:
            await member.remove_roles(role)
            status_cache[member.id] = False
            if channel:
                await channel.send(f"{member.mention}")
                embed = discord.Embed(
                    description=f"<a:pusheenblink:1397529491403837491>  <:002_symbol2:1362146530227912775>   {member.mention} lost their role because they didn't include vanity link.",
                    color=PASTEL_PINK
                )
                await channel.send(embed=embed)

        elif has_dollsick:
            status_cache[member.id] = True
        else:
            status_cache[member.id] = False

async def handle(request):
    return web.Response(text="Bot is running")

port = int(os.getenv("PORT", 8080))
app = web.Application()
app.add_routes([web.get('/', handle)])

async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server running on port {port}")

    await bot.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())
