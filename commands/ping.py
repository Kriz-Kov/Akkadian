import base64
import json
import os

import aiohttp
import discord
from discord.ext import commands
from mcstatus import JavaServer
from ping3 import ping

latency_measurements = {"10": "is amazing", "50": "is average",
                        "100": "could be better", "150": "has an issue"}

with open("config.json", "r") as file:
    data = json.load(file)
    server_ip = data["bot"]["server_ip"]

class server_ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.client = bot

    @commands.command(name="ping",
                      usage="",
                      description="Retrieves the bots latency.")
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def ping(self, ctx: commands.Context):
        """Command that retrieves the clients current latency.

        Args:
            ctx (commands.Context): The user who initiated the command. (A.K.A context)
        """
        async with ctx.typing():
            # * Retrieve the clients latency and return the value rounded up and multiplied to one thousand.
            current_latency = round(self.client.latency * 1000)
            # * Loop through the dictionary we made with key values that represent ping "levels".
            for latency in latency_measurements:
                # * If the current ping is greater than the ping "level" we return that keys message.
                if current_latency >= int(latency):
                    message = latency_measurements[latency]
            response = ping(f"{server_ip}")
            server_response = "🔴 Offline" if response == False else "🟢 Online"
            session = aiohttp.ClientSession()
            main_server = await session.get(f"https://api.mcsrvstat.us/2/{server_ip}")
            status = await main_server.json()
            await session.close()
            serverURL = JavaServer.lookup(f"{server_ip}")
            iconURL = serverURL.status().favicon
            if iconURL is not None:
                IconBinary = iconURL.split("base64,")[1]
                base64_img_bytes = IconBinary.encode('utf-8')
                with open('assets/server_favicon.png', 'wb') as file_to_save:
                    decoded_image_data = base64.decodebytes(base64_img_bytes)
                    file_to_save.write(decoded_image_data)
                    status_ = True
            else:
                status_ = False
            online = status["online"]
            main_server_response = "🟢 Online" if online == True else "🔴 Offline"
            # * Finally send a beautiful little embed.
            embed = discord.Embed(
                title="Current Ping", description=f"The bots current ping {message} [`{current_latency}`ms]\nThe server host is currently [`{server_response}`]\n**{server_ip}** is currently [`{main_server_response}`]", color=discord.Color.from_rgb(0, 255, 154))
            embed.set_footer(
                text="Server statuses are updated in 10 minute intervals, may not be accurate all of the time")
            if status_:
                file = discord.File("assets/server_favicon.png",
                                    filename="server_favicon.png")
                embed.set_thumbnail(url="attachment://server_favicon.png")
                await ctx.reply(file=file, embed=embed, mention_author=False)
                os.remove("assets/server_favicon.png")
            else:
                embed.set_thumbnail(
                    url="https://media.minecraftforum.net/attachments/300/619/636977108000120237.png")
                await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(server_ping(bot))
