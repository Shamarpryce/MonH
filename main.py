from typing import Any
import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os

from keep_alive import keep_alive # NEW

# Load environment variables
load_dotenv()
token: Any = os.getenv('DISCORD_TOKEN')

keep_alive() # NEW

# Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)


class MHPCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ENTRY EXAM COMMAND
    @app_commands.command(name="entry_exam", description="Post the results of an entry exam.")
    @app_commands.describe(
        candidate="The user who took the exam",
        result="Pass or Fail",
        channel="The channel to send the result to"
    )
    @app_commands.choices(result=[
        app_commands.Choice(name="Pass", value="pass"),
        app_commands.Choice(name="Fail", value="fail")
    ])
    async def entry_exam(
        self,
        interaction: discord.Interaction,
        candidate: discord.Member,
        result: app_commands.Choice[str],
        channel: discord.TextChannel
    ):
        if result.value == "pass":
            description = (
                f"{candidate.mention}, you have **passed** your entry exam! "
                f"Welcome to the Montana Highway Patrol.\nYou have **7 days** to complete your training."
            )
            color = discord.Color.green()
        else:
            description = (
                f"{candidate.mention}, you have **failed** your entry exam. "
                f"You may reapply in the future."
            )
            color = discord.Color.red()

        embed = discord.Embed(title="Entry Exam Results", description=description, color=color)

        # Send result to selected channel
        await channel.send(content=candidate.mention, embed=embed)

        # DM candidate only if possible
        try:
            await candidate.send(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                f"⚠️ Could not DM {candidate.mention} (DMs may be closed).",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Entry exam result posted in {channel.mention}.",
            ephemeral=True
        )

    # TRAINING REQUEST COMMAND
    @app_commands.command(name="training_request", description="Post a training request.")
    @app_commands.describe(
        trainee="The user requesting training",
        stage="Stage of training the trainee is in",
        availability="Trainee's availability",
        role="Role to ping for trainers",
        channel="Channel to post the request in"
    )
    async def training_request(
        self,
        interaction: discord.Interaction,
        trainee: discord.Member,
        stage: str,
        availability: str,
        role: discord.Role,
        channel: discord.TextChannel
    ):
        ping_text = f"{trainee.mention} | {role.mention}"

        embed = discord.Embed(
            title="Training Request",
            description=f"{trainee.mention} has requested a training",
            color=discord.Color.blue()
        )
        embed.add_field(name="Trainee's Availability", value=availability, inline=False)
        embed.add_field(name="Stage of Training Trainee is in", value=stage, inline=False)
        embed.set_footer(
            text="This trainee needs training, please get to this Boot as soon as you can "
                 "so he/her can get the best of the best training experience."
        )

        await channel.send(content=ping_text, embed=embed)
        await interaction.response.send_message(
            f"Training request posted in {channel.mention}.",
            ephemeral=True
        )


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.online)


async def setup_hook():
    await bot.add_cog(MHPCommands(bot))
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")

bot.setup_hook = setup_hook

# Run the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
