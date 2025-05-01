import discord
from discord.ext import commands
from calendar_bot.bot_config import load_config
from calendar_bot.google_calendar import run_calendar_sync
from calendar_bot.custom_logger import get_logger
import sys
import asyncio

config = load_config()
logger = get_logger()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
RUNNING_CLI_SYNC = len(sys.argv) > 1 and sys.argv[1] == "sync"
tree = bot.tree

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

    try:
        synced = await tree.sync(guild=discord.Object(id=config["DISCORD_GUILD_ID"]))
        logger.info(f"Synced {len(synced)} command(s) to guild {config['DISCORD_GUILD_ID']}")
    except Exception as e:
        logger.exception("Failed to sync application commands")

    if RUNNING_CLI_SYNC:
        try:
            await run_calendar_sync(bot)
        except Exception as e:
            logger.exception("Error during CLI sync run:")
        finally:
            logger.info("CLI sync complete. Shutting down bot.")
            await bot.close()


@tree.command(name="sync", description="Sync Google Calendar events to Discord", guild=discord.Object(id=config["DISCORD_GUILD_ID"]))
async def slash_sync(interaction: discord.Interaction):
    logger.info(f"Received /sync command from {interaction.user}")
    await interaction.response.defer(thinking=True)
    try:
        await run_calendar_sync(bot)
        await interaction.followup.send("✅ Sync complete!")
    except Exception as e:
        logger.exception("Error during /sync command.")
        await interaction.followup.send("❌ Sync failed. Check logs for details.")


def main():
    if RUNNING_CLI_SYNC:
        logger.info("Starting bot in CLI sync mode...")

        async def runner():
            try:
                await bot.start(config["DISCORD_BOT_TOKEN"])
            except Exception:
                logger.exception("Failed to start bot for CLI sync")

        asyncio.run(runner())

    else:
        logger.info("Starting bot in normal interactive mode...")
        bot.run(config["DISCORD_BOT_TOKEN"])


if __name__ == "__main__":
    main()
