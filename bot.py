import os
import random
import time
from typing import Optional

import asyncpg
import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

intents = discord.Intents.default()
intents.message_content = True

STAFF_ROLE_ID = 1240660412647866378

DROP_CHANNEL_IDS = [
    1493341908246859967,
    1295247108001103974
]

AUTO_DROP_MINUTES = 30
AUTO_DROP_CHANCE = 40

CLAIM_COOLDOWN = 30
last_claim_times = {}

db_pool = None


# ---------------- DATABASE SETUP ----------------

async def setup_database():
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                rarity TEXT NOT NULL,
                image TEXT NOT NULL
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                card_id INTEGER NOT NULL REFERENCES cards(id)
            );
        """)


# ---------------- HELPERS ----------------

def is_staff(member: discord.Member):
    return any(role.id == STAFF_ROLE_ID for role in member.roles)


def get_color(rarity):
    return {
        "Common": discord.Color.from_str("#8b8b8b"),
        "Rare": discord.Color.from_str("#5c8df6"),
        "Epic": discord.Color.from_str("#9e659d"),
        "Legendary": discord.Color.from_str("#f5c542"),
    }.get(rarity, discord.Color.blurple())


# ---------------- CARD FUNCTIONS ----------------

async def get_card_by_name(name):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM cards WHERE LOWER(name)=LOWER($1)",
            name
        )


async def get_all_cards():
    async with db_pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM cards")


async def add_card_to_inventory(user_id, card_id):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO inventory (user_id, card_id) VALUES ($1,$2)",
            user_id,
            card_id
        )


async def user_owns_card(user_id, card_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT 1 FROM inventory WHERE user_id=$1 AND card_id=$2",
            user_id,
            card_id
        )

async def get_user_cards(user_id):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT cards.name
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE user_id=$1
        """, user_id)

    return list(set([row["name"] for row in rows]))

async def trade_cards(u1, c1, u2, c2):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            a = await conn.fetchrow(
                "SELECT id FROM inventory WHERE user_id=$1 AND card_id=$2 LIMIT 1 FOR UPDATE",
                u1, c1
            )
            b = await conn.fetchrow(
                "SELECT id FROM inventory WHERE user_id=$1 AND card_id=$2 LIMIT 1 FOR UPDATE",
                u2, c2
            )

            if not a:
                return False, "Requester no longer owns card."
            if not b:
                return False, "Target no longer owns card."

            await conn.execute("UPDATE inventory SET user_id=$1 WHERE id=$2", u2, a["id"])
            await conn.execute("UPDATE inventory SET user_id=$1 WHERE id=$2", u1, b["id"])

            return True, "Trade completed!"

async def your_cards_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_user_cards(interaction.user.id)

    return [
        app_commands.Choice(name=card, value=card)
        for card in cards
        if current.lower() in card.lower()
    ][:25]

async def all_cards_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_all_cards()

    return [
        app_commands.Choice(name=card["name"], value=card["name"])
        for card in cards
        if current.lower() in card["name"].lower()
    ][:25]

# ---------------- AUTO DROP ----------------

async def choose_random_card():
    async with db_pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM cards ORDER BY RANDOM() LIMIT 1")


@tasks.loop(minutes=AUTO_DROP_MINUTES)
async def auto_drop():
    if random.randint(1, 100) > AUTO_DROP_CHANCE:
        return

    channel = bot.get_channel(random.choice(DROP_CHANNEL_IDS))
    if not channel:
        return

    card = await choose_random_card()

    embed = discord.Embed(
        title=f"{card['rarity']} Card Drop!",
        description=f"**{card['name']}** appeared!",
        color=get_color(card["rarity"])
    )
    embed.set_image(url=card["image"])

    await channel.send(embed=embed, view=ClaimView(card))


# ---------------- CLAIM SYSTEM ----------------

class ClaimView(discord.ui.View):
    def __init__(self, card):
        super().__init__(timeout=60)
        self.card = card
        self.claimed = False

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        now = time.time()

        if uid in last_claim_times:
            if now - last_claim_times[uid] < CLAIM_COOLDOWN:
                await interaction.response.send_message(
                    "⏳ You are on cooldown.",
                    ephemeral=True
                )
                return

        if self.claimed:
            await interaction.response.send_message("Already claimed.", ephemeral=True)
            return

        self.claimed = True
        last_claim_times[uid] = now

        button.disabled = True

        await add_card_to_inventory(uid, self.card["id"])

        await interaction.response.edit_message(
            content=f"{interaction.user.mention} claimed **{self.card['name']}**!",
            view=self
        )

class TradeView(discord.ui.View):
    def __init__(self, requester, target, requester_card, target_card):
        super().__init__(timeout=120)
        self.requester = requester
        self.target = target
        self.requester_card = requester_card
        self.target_card = target_card

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("Not your trade.", ephemeral=True)

        success, msg = await trade_cards(
            self.requester.id,
            self.requester_card["id"],
            self.target.id,
            self.target_card["id"]
        )

        await interaction.response.edit_message(content=msg, view=None)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("Not your trade.", ephemeral=True)

        await interaction.response.edit_message(content="Trade declined.", view=None)

# ---------------- BOT ----------------

class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        global db_pool
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        await setup_database()
        await self.tree.sync()


bot = Bot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not auto_drop.is_running():
        auto_drop.start()


# ---------------- COMMANDS ----------------

@bot.tree.command(name="ping")
async def ping(interaction):
    await interaction.response.send_message("Online!")


@bot.tree.command(name="card")
@app_commands.describe(name="Card name")
async def card(interaction, name: str):
    c = await get_card_by_name(name)
    if not c:
        return await interaction.response.send_message("Not found", ephemeral=True)

    embed = discord.Embed(
        title=c["name"],
        description=c["rarity"],
        color=get_color(c["rarity"])
    )
    embed.set_image(url=c["image"])

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="cards")
async def cards(interaction):
    all_cards = await get_all_cards()

    text = ""
    for c in all_cards:
        text += f"{c['rarity']} • {c['name']}\n"

    await interaction.response.send_message(text)


@bot.tree.command(name="inventory")
async def inventory(interaction, user: discord.Member = None):
    user = user or interaction.user

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT cards.name, cards.rarity, COUNT(*) as amount
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE user_id=$1
            GROUP BY cards.name, cards.rarity
        """, user.id)

    text = ""
    for r in rows:
        text += f"{r['rarity']} • {r['name']} x{r['amount']}\n"

    await interaction.response.send_message(text or "Empty")

@bot.tree.command(name="trade", description="Trade cards with another user")
@app_commands.describe(
    user="Trade with",
    your_card="Card you're offering",
    their_card="Card you want"
)
@app_commands.autocomplete(
    your_card=your_cards_autocomplete,
    their_card=all_cards_autocomplete
)
async def trade(
    interaction: discord.Interaction,
    user: discord.Member,
    your_card: str,
    their_card: str
):
    if user.bot:
        return await interaction.response.send_message("Cannot trade with bots.", ephemeral=True)

    if user.id == interaction.user.id:
        return await interaction.response.send_message("You cannot trade yourself.", ephemeral=True)

    your_card_data = await get_card_by_name(your_card)
    their_card_data = await get_card_by_name(their_card)

    if not your_card_data or not their_card_data:
        return await interaction.response.send_message("Card not found.", ephemeral=True)

    if not await user_owns_card(interaction.user.id, your_card_data["id"]):
        return await interaction.response.send_message(
            f"You do not own **{your_card_data['name']}**.",
            ephemeral=True
        )

    if not await user_owns_card(user.id, their_card_data["id"]):
        return await interaction.response.send_message(
            f"{user.display_name} does not own **{their_card_data['name']}**.",
            ephemeral=True
        )

    view = TradeView(interaction.user, user, your_card_data, their_card_data)

    embed = discord.Embed(
        title="Trade Request",
        description=(
            f"{interaction.user.mention} offers **{your_card_data['name']}**\n"
            f"in exchange for **{their_card_data['name']}** from {user.mention}"
        ),
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="addcard")
async def addcard(interaction, name: str, rarity: str, image: str):
    if not is_staff(interaction.user):
        return await interaction.response.send_message("No permission", ephemeral=True)

    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO cards (name, rarity, image) VALUES ($1,$2,$3)",
            name, rarity, image
        )

    await interaction.response.send_message("Added card")


@bot.tree.command(name="dropcard")
async def dropcard(interaction):
    if not is_staff(interaction.user):
        return await interaction.response.send_message("No permission", ephemeral=True)

    card = await choose_random_card()

    embed = discord.Embed(
        title=card["name"],
        color=get_color(card["rarity"])
    )
    embed.set_image(url=card["image"])

    await interaction.response.send_message(embed=embed, view=ClaimView(card))


# ---------------- RUN ----------------

bot.run(TOKEN)
