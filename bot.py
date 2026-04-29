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

# Placeholder: replace 0 with your staff log channel ID later
REMOVED_CARD_LOG_CHANNEL_ID = 0

DROP_CHANNEL_IDS = [
    1493341908246859967,
    1295247108001103974
]

AUTO_DROP_MINUTES = 30
AUTO_DROP_CHANCE = 40

CLAIM_COOLDOWN = 30
last_claim_times = {}

active_trade_card_ids = set()

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
            ALTER TABLE cards
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
        """)

        await conn.execute("""
            UPDATE cards
            SET is_active = TRUE
            WHERE is_active IS NULL;
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


def create_card_embed(card):
    embed = discord.Embed(
        title=f"{card['rarity']} Card Drop!",
        description=f"**{card['name']}** appeared!",
        color=get_color(card["rarity"])
    )
    embed.set_image(url=card["image"])
    return embed


async def log_removed_card(interaction: discord.Interaction, card):
    if REMOVED_CARD_LOG_CHANNEL_ID == 0:
        return

    channel = interaction.guild.get_channel(REMOVED_CARD_LOG_CHANNEL_ID)

    if not channel:
        return

    embed = discord.Embed(
        title="Card Removed From Future Drops",
        description=(
            f"**Card:** {card['name']}\n"
            f"**Rarity:** {card['rarity']}\n"
            f"**Removed by:** {interaction.user.mention}\n\n"
            f"Members who already own this card will keep it."
        ),
        color=discord.Color.red()
    )

    await channel.send(embed=embed)


# ---------------- CARD FUNCTIONS ----------------

async def get_card_by_name(name):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM cards WHERE LOWER(name)=LOWER($1)",
            name
        )


async def get_active_card_by_name(name):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM cards WHERE LOWER(name)=LOWER($1) AND is_active = TRUE",
            name
        )


async def get_all_cards():
    async with db_pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM cards ORDER BY rarity, name")


async def get_active_cards():
    async with db_pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM cards WHERE is_active = TRUE ORDER BY rarity, name"
        )


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


async def get_user_active_cards(user_id):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT cards.name
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE inventory.user_id=$1
            AND cards.is_active = TRUE
            ORDER BY cards.name
        """, user_id)

    return [row["name"] for row in rows]


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


# ---------------- AUTOCOMPLETE ----------------

async def your_cards_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_user_active_cards(interaction.user.id)

    return [
        app_commands.Choice(name=card, value=card)
        for card in cards
        if current.lower() in card.lower()
    ][:25]


async def all_active_cards_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_active_cards()

    return [
        app_commands.Choice(name=card["name"], value=card["name"])
        for card in cards
        if current.lower() in card["name"].lower()
    ][:25]


# ---------------- AUTO DROP ----------------

async def choose_random_card():
    rarity = random.choices(
        ["Common", "Rare", "Epic", "Legendary"],
        weights=[60, 25, 10, 5],
        k=1
    )[0]

    async with db_pool.acquire() as conn:
        cards = await conn.fetch(
            "SELECT * FROM cards WHERE rarity=$1 AND is_active = TRUE",
            rarity
        )

        if cards:
            return random.choice(cards)

        fallback_cards = await conn.fetch(
            "SELECT * FROM cards WHERE is_active = TRUE"
        )

        if not fallback_cards:
            return None

        return random.choice(fallback_cards)


@tasks.loop(minutes=AUTO_DROP_MINUTES)
async def auto_drop():
    if random.randint(1, 100) > AUTO_DROP_CHANCE:
        return

    channel = bot.get_channel(random.choice(DROP_CHANNEL_IDS))
    if not channel:
        return

    card = await choose_random_card()

    if not card:
        return

    await channel.send(embed=create_card_embed(card), view=ClaimView(card))


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
                remaining = int(CLAIM_COOLDOWN - (now - last_claim_times[uid]))
                await interaction.response.send_message(
                    f"⏳ You are on cooldown. Try again in {remaining}s.",
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


# ---------------- TRADE SYSTEM ----------------

class TradeView(discord.ui.View):
    def __init__(self, requester, target, requester_card, target_card):
        super().__init__(timeout=120)
        self.requester = requester
        self.target = target
        self.requester_card = requester_card
        self.target_card = target_card
        self.finished = False

        active_trade_card_ids.add(requester_card["id"])
        active_trade_card_ids.add(target_card["id"])

    def clear_active_trade_cards(self):
        active_trade_card_ids.discard(self.requester_card["id"])
        active_trade_card_ids.discard(self.target_card["id"])

    async def on_timeout(self):
        self.finished = True
        self.clear_active_trade_cards()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("Not your trade.", ephemeral=True)

        if self.finished:
            return await interaction.response.send_message("This trade is already finished.", ephemeral=True)

        success, msg = await trade_cards(
            self.requester.id,
            self.requester_card["id"],
            self.target.id,
            self.target_card["id"]
        )

        self.finished = True
        self.clear_active_trade_cards()

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(content=msg, embed=None, view=self)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("Not your trade.", ephemeral=True)

        if self.finished:
            return await interaction.response.send_message("This trade is already finished.", ephemeral=True)

        self.finished = True
        self.clear_active_trade_cards()

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(content="Trade declined.", embed=None, view=self)


# ---------------- REMOVE CARD CONFIRMATION ----------------

class RemoveCardView(discord.ui.View):
    def __init__(self, requester, card):
        super().__init__(timeout=60)
        self.requester = requester
        self.card = card
        self.finished = False

    @discord.ui.button(label="Confirm Remove", style=discord.ButtonStyle.red)
    async def confirm_remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.requester.id:
            return await interaction.response.send_message("Only the staff member who started this can confirm.", ephemeral=True)

        if self.finished:
            return await interaction.response.send_message("This action is already finished.", ephemeral=True)

        if self.card["id"] in active_trade_card_ids:
            return await interaction.response.send_message(
                "This card is currently part of an active trade and cannot be removed yet.",
                ephemeral=True
            )

        async with db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE cards SET is_active = FALSE WHERE id=$1",
                self.card["id"]
            )

        self.finished = True

        for child in self.children:
            child.disabled = True

        await log_removed_card(interaction, self.card)

        await interaction.response.edit_message(
            content=(
                f"✅ **{self.card['name']}** has been removed from future drops and card lists.\n"
                f"Members who already own it will keep it in their inventories."
            ),
            embed=None,
            view=self
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.requester.id:
            return await interaction.response.send_message("Only the staff member who started this can cancel.", ephemeral=True)

        self.finished = True

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content="Card removal cancelled.",
            embed=None,
            view=self
        )


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

@bot.tree.command(name="ping", description="Check if the bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Online!")


@bot.tree.command(name="card", description="View a specific card.")
@app_commands.describe(name="Card name")
@app_commands.autocomplete(name=all_active_cards_autocomplete)
async def card(interaction: discord.Interaction, name: str):
    c = await get_card_by_name(name)
    if not c:
        return await interaction.response.send_message("Not found.", ephemeral=True)

    embed = discord.Embed(
        title=c["name"],
        description=f"**Rarity:** {c['rarity']}",
        color=get_color(c["rarity"])
    )
    embed.set_image(url=c["image"])

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="cards", description="View all currently obtainable cards.")
async def cards(interaction: discord.Interaction):
    all_cards = await get_active_cards()

    if not all_cards:
        return await interaction.response.send_message("There are no obtainable cards right now.")

    grouped = {}

    for c in all_cards:
        grouped.setdefault(c["rarity"], []).append(c["name"])

    text = ""

    for rarity in ["Common", "Rare", "Epic", "Legendary"]:
        if rarity in grouped:
            text += f"**{rarity}**\n"
            for name in grouped[rarity]:
                text += f"• {name}\n"
            text += "\n"

    embed = discord.Embed(
        title="Currently Obtainable Cards",
        description=text,
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="inventory", description="View your inventory or another user's inventory.")
async def inventory(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT cards.name, cards.rarity, cards.is_active, COUNT(*) as amount
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE user_id=$1
            GROUP BY cards.name, cards.rarity, cards.is_active
            ORDER BY cards.rarity, cards.name
        """, user.id)

    if not rows:
        return await interaction.response.send_message("Empty")

    text = ""

    for r in rows:
        limited_note = "" if r["is_active"] else " *(unobtainable)*"
        text += f"{r['rarity']} • {r['name']} x{r['amount']}{limited_note}\n"

    embed = discord.Embed(
        title=f"{user.display_name}'s Inventory",
        description=text,
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="trade", description="Trade cards with another user.")
@app_commands.describe(
    user="Trade with",
    your_card="Card you're offering",
    their_card="Card you want"
)
@app_commands.autocomplete(
    your_card=your_cards_autocomplete,
    their_card=all_active_cards_autocomplete
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

    your_card_data = await get_active_card_by_name(your_card)
    their_card_data = await get_active_card_by_name(their_card)

    if not your_card_data or not their_card_data:
        return await interaction.response.send_message("One of those cards is not currently tradeable.", ephemeral=True)

    if your_card_data["id"] in active_trade_card_ids or their_card_data["id"] in active_trade_card_ids:
        return await interaction.response.send_message(
            "One of those cards is already part of an active trade. Try again after that trade finishes.",
            ephemeral=True
        )

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
            f"in exchange for **{their_card_data['name']}** from {user.mention}\n\n"
            f"{user.mention}, accept or decline this trade."
        ),
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed, view=view)


@bot.tree.command(name="addcard", description="Staff only: add or reactivate a collectible card.")
@app_commands.describe(
    name="Card name",
    rarity="Card rarity",
    image="Direct image URL"
)
@app_commands.choices(
    rarity=[
        app_commands.Choice(name="Common", value="Common"),
        app_commands.Choice(name="Rare", value="Rare"),
        app_commands.Choice(name="Epic", value="Epic"),
        app_commands.Choice(name="Legendary", value="Legendary"),
    ]
)
async def addcard(
    interaction: discord.Interaction,
    name: str,
    rarity: app_commands.Choice[str],
    image: str
):
    if not is_staff(interaction.user):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    existing_card = await get_card_by_name(name)

    async with db_pool.acquire() as conn:
        if existing_card:
            await conn.execute(
                """
                UPDATE cards
                SET rarity=$1, image=$2, is_active = TRUE
                WHERE id=$3
                """,
                rarity.value,
                image,
                existing_card["id"]
            )

            return await interaction.response.send_message(
                f"✅ Reactivated/updated **{name}** as a **{rarity.value}** card."
            )

        await conn.execute(
            "INSERT INTO cards (name, rarity, image, is_active) VALUES ($1,$2,$3, TRUE)",
            name,
            rarity.value,
            image
        )

    await interaction.response.send_message(f"✅ Added **{name}** as a **{rarity.value}** card.")


@bot.tree.command(name="dropcard", description="Staff only: drop a card.")
@app_commands.describe(
    rarity="Choose a rarity to drop from",
    card_name="Choose a specific card to drop"
)
@app_commands.choices(
    rarity=[
        app_commands.Choice(name="Common", value="Common"),
        app_commands.Choice(name="Rare", value="Rare"),
        app_commands.Choice(name="Epic", value="Epic"),
        app_commands.Choice(name="Legendary", value="Legendary"),
    ]
)
@app_commands.autocomplete(card_name=all_active_cards_autocomplete)
async def dropcard(
    interaction: discord.Interaction,
    rarity: Optional[app_commands.Choice[str]] = None,
    card_name: Optional[str] = None
):
    if not is_staff(interaction.user):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    async with db_pool.acquire() as conn:
        if card_name:
            cards = await conn.fetch(
                "SELECT * FROM cards WHERE LOWER(name)=LOWER($1) AND is_active = TRUE",
                card_name
            )
        elif rarity:
            cards = await conn.fetch(
                "SELECT * FROM cards WHERE rarity=$1 AND is_active = TRUE",
                rarity.value
            )
        else:
            cards = await conn.fetch("SELECT * FROM cards WHERE is_active = TRUE")

    if not cards:
        return await interaction.response.send_message("No cards found for that choice.", ephemeral=True)

    selected_card = random.choice(cards)

    await interaction.response.send_message(
        embed=create_card_embed(selected_card),
        view=ClaimView(selected_card)
    )


@bot.tree.command(name="removecard", description="Staff only: remove a card from future drops.")
@app_commands.describe(card_name="Choose the card to remove")
@app_commands.autocomplete(card_name=all_active_cards_autocomplete)
async def removecard(interaction: discord.Interaction, card_name: str):
    if not is_staff(interaction.user):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    card = await get_active_card_by_name(card_name)

    if not card:
        return await interaction.response.send_message("That active card was not found.", ephemeral=True)

    if card["id"] in active_trade_card_ids:
        return await interaction.response.send_message(
            "This card is currently part of an active trade and cannot be removed yet.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="Confirm Card Removal",
        description=(
            f"Are you sure you want to remove **{card['name']}** from future drops and card lists?\n\n"
            f"Members who already own it will **keep it**."
        ),
        color=discord.Color.red()
    )

    await interaction.response.send_message(
        embed=embed,
        view=RemoveCardView(interaction.user, card),
        ephemeral=True
    )


# ---------------- RUN ----------------

bot.run(TOKEN)