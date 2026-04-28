import os
import random
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

RARITIES = ["Common", "Rare", "Epic", "Legendary"]

STARTER_CARDS = [
    {
        "name": "Sanction Shadow",
        "rarity": "Common",
        "image": "https://media.discordapp.net/attachments/1493341908246859967/1498448123008258048/IMG_7150.png.webp?ex=69f13210&is=69efe090&hm=314ff383079210f6215fde2cc5f9ba35953cce3f87546199bb498056bae0c2ed&=&format=webp&width=880&height=1300"
    },
    {
        "name": "Hoarder",
        "rarity": "Rare",
        "image": "https://media.discordapp.net/attachments/1493341908246859967/1498448123008258048/IMG_7150.png.webp?ex=69f13210&is=69efe090&hm=314ff383079210f6215fde2cc5f9ba35953cce3f87546199bb498056bae0c2ed&=&format=webp&width=880&height=1300"
    },
    {
        "name": "Chrome Saint",
        "rarity": "Legendary",
        "image": "https://media.discordapp.net/attachments/1493341908246859967/1498448123008258048/IMG_7150.png.webp?ex=69f13210&is=69efe090&hm=314ff383079210f6215fde2cc5f9ba35953cce3f87546199bb498056bae0c2ed&=&format=webp&width=880&height=1300"
    }
]

db_pool = None


def is_staff(member: discord.Member):
    return any(role.id == STAFF_ROLE_ID for role in member.roles)


def get_color(rarity):
    if rarity == "Common":
        return discord.Color.from_str("#8b8b8b")
    elif rarity == "Rare":
        return discord.Color.from_str("#5c8df6")
    elif rarity == "Epic":
        return discord.Color.from_str("#9e659d")
    elif rarity == "Legendary":
        return discord.Color.from_str("#f5c542")
    else:
        return discord.Color.from_str("#9e659d")


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
            CREATE TABLE IF NOT EXISTS inventory_entries (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
                acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        for card in STARTER_CARDS:
            await conn.execute("""
                INSERT INTO cards (name, rarity, image)
                VALUES ($1, $2, $3)
                ON CONFLICT (name) DO NOTHING;
            """, card["name"], card["rarity"], card["image"])


async def get_all_cards():
    async with db_pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM cards ORDER BY rarity, name;")


async def get_card_by_name(card_name):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM cards WHERE LOWER(name) = LOWER($1);",
            card_name
        )


async def add_card_to_inventory(user_id, card_id):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO inventory_entries (user_id, card_id) VALUES ($1, $2);",
            user_id,
            card_id
        )


async def user_owns_card(user_id, card_id):
    async with db_pool.acquire() as conn:
        result = await conn.fetchval("""
            SELECT id FROM inventory_entries
            WHERE user_id = $1 AND card_id = $2
            LIMIT 1;
        """, user_id, card_id)

        return result is not None


async def trade_cards(user_one_id, user_one_card_id, user_two_id, user_two_card_id):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            user_one_entry = await conn.fetchrow("""
                SELECT id FROM inventory_entries
                WHERE user_id = $1 AND card_id = $2
                LIMIT 1
                FOR UPDATE;
            """, user_one_id, user_one_card_id)

            user_two_entry = await conn.fetchrow("""
                SELECT id FROM inventory_entries
                WHERE user_id = $1 AND card_id = $2
                LIMIT 1
                FOR UPDATE;
            """, user_two_id, user_two_card_id)

            if not user_one_entry:
                return False, "The requester no longer owns that card."

            if not user_two_entry:
                return False, "The other user no longer owns that card."

            await conn.execute(
                "UPDATE inventory_entries SET user_id = $1 WHERE id = $2;",
                user_two_id,
                user_one_entry["id"]
            )

            await conn.execute(
                "UPDATE inventory_entries SET user_id = $1 WHERE id = $2;",
                user_one_id,
                user_two_entry["id"]
            )

            return True, "Trade completed successfully!"


async def choose_random_card_by_rarity():
    rarity = random.choices(
        ["Common", "Rare", "Epic", "Legendary"],
        weights=[60, 25, 10, 5],
        k=1
    )[0]

    async with db_pool.acquire() as conn:
        matching_cards = await conn.fetch(
            "SELECT * FROM cards WHERE rarity = $1;",
            rarity
        )

        if matching_cards:
            return random.choice(matching_cards)

        all_cards = await conn.fetch("SELECT * FROM cards;")

        if not all_cards:
            return None

        return random.choice(all_cards)


def create_card_embed(card):
    embed = discord.Embed(
        title=f"{card['rarity']} Card Drop!",
        description=f"A card has appeared...\n\n**{card['name']}**\n\n⏳ Click below to claim it!",
        color=get_color(card["rarity"])
    )

    embed.set_image(url=card["image"])
    return embed


async def card_name_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_all_cards()

    matches = [
        app_commands.Choice(name=card["name"], value=card["name"])
        for card in cards
        if current.lower() in card["name"].lower()
    ]

    return matches[:25]


class ClaimButton(discord.ui.View):
    def __init__(self, card):
        super().__init__(timeout=60)
        self.card = card
        self.claimed = False

    @discord.ui.button(label="Claim Card", style=discord.ButtonStyle.green)
    async def claim_card(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.claimed:
            await interaction.response.send_message(
                "This card was already claimed!",
                ephemeral=True
            )
            return

        self.claimed = True
        button.disabled = True

        await add_card_to_inventory(interaction.user.id, self.card["id"])

        await interaction.response.edit_message(
            content=f"{interaction.user.mention} claimed **{self.card['name']}**! It has been added to their inventory.",
            view=self
        )


class TradeView(discord.ui.View):
    def __init__(self, requester, target, requester_card, target_card):
        super().__init__(timeout=120)
        self.requester = requester
        self.target = target
        self.requester_card = requester_card
        self.target_card = target_card
        self.finished = False

    @discord.ui.button(label="Accept Trade", style=discord.ButtonStyle.green)
    async def accept_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "Only the person receiving the trade request can accept it.",
                ephemeral=True
            )
            return

        if self.finished:
            await interaction.response.send_message(
                "This trade is already finished.",
                ephemeral=True
            )
            return

        success, message = await trade_cards(
            self.requester.id,
            self.requester_card["id"],
            self.target.id,
            self.target_card["id"]
        )

        self.finished = True

        for child in self.children:
            child.disabled = True

        if success:
            await interaction.response.edit_message(
                content=(
                    f"✅ Trade completed!\n\n"
                    f"{self.requester.mention} received **{self.target_card['name']}**.\n"
                    f"{self.target.mention} received **{self.requester_card['name']}**."
                ),
                embed=None,
                view=self
            )
        else:
            await interaction.response.edit_message(
                content=f"❌ {message}",
                embed=None,
                view=self
            )

    @discord.ui.button(label="Decline Trade", style=discord.ButtonStyle.red)
    async def decline_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "Only the person receiving the trade request can decline it.",
                ephemeral=True
            )
            return

        if self.finished:
            await interaction.response.send_message(
                "This trade is already finished.",
                ephemeral=True
            )
            return

        self.finished = True

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=f"❌ {self.target.mention} declined the trade.",
            embed=None,
            view=self
        )


class SanctionCardsBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        global db_pool

        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is missing. Add it to your .env or Railway variables.")

        db_pool = await asyncpg.create_pool(DATABASE_URL)
        await setup_database()
        await self.tree.sync()


bot = SanctionCardsBot()


@tasks.loop(minutes=AUTO_DROP_MINUTES)
async def auto_drop_loop():
    roll = random.randint(1, 100)

    if roll > AUTO_DROP_CHANCE:
        return

    channel_id = random.choice(DROP_CHANNEL_IDS)
    channel = bot.get_channel(channel_id)

    if channel is None:
        return

    card = await choose_random_card_by_rarity()

    if card is None:
        return

    embed = create_card_embed(card)
    view = ClaimButton(card)

    await channel.send(embed=embed, view=view)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    if not auto_drop_loop.is_running():
        auto_drop_loop.start()


@bot.tree.command(name="ping", description="Test if the card bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Sanction Cards is online!")


@bot.tree.command(name="addcard", description="Staff only: add a new collectible card.")
@app_commands.describe(
    name="The card name.",
    rarity="The card rarity.",
    image="The direct image URL."
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
        await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )
        return

    existing_card = await get_card_by_name(name)

    if existing_card:
        await interaction.response.send_message(
            f"A card named **{name}** already exists.",
            ephemeral=True
        )
        return

    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO cards (name, rarity, image) VALUES ($1, $2, $3);",
            name,
            rarity.value,
            image
        )

    await interaction.response.send_message(
        f"✅ Added **{name}** as a **{rarity.value}** card."
    )


@bot.tree.command(name="inventory", description="View a card inventory.")
@app_commands.describe(user="Choose whose inventory you want to view.")
async def inventory(interaction: discord.Interaction, user: discord.Member = None):
    target_user = user or interaction.user

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT cards.name, cards.rarity, COUNT(*) AS amount
            FROM inventory_entries
            JOIN cards ON inventory_entries.card_id = cards.id
            WHERE inventory_entries.user_id = $1
            GROUP BY cards.name, cards.rarity
            ORDER BY cards.rarity, cards.name;
        """, target_user.id)

    if not rows:
        await interaction.response.send_message(
            f"{target_user.display_name} does not have any cards yet.",
            ephemeral=True
        )
        return

    total_cards = sum(row["amount"] for row in rows)
    cards_by_rarity = {}

    for row in rows:
        rarity = row["rarity"]

        if rarity not in cards_by_rarity:
            cards_by_rarity[rarity] = []

        cards_by_rarity[rarity].append((row["name"], row["amount"]))

    card_list = ""

    for rarity in ["Common", "Rare", "Epic", "Legendary"]:
        if rarity in cards_by_rarity:
            card_list += f"**{rarity}**\n"
            for card_name, amount in cards_by_rarity[rarity]:
                card_list += f"• {card_name} x{amount}\n"
            card_list += "\n"

    embed = discord.Embed(
        title=f"{target_user.display_name}'s Inventory",
        description=f"**Total Cards:** {total_cards}\n\n{card_list}",
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="cards", description="View all obtainable cards.")
async def cards(interaction: discord.Interaction):
    all_cards = await get_all_cards()

    if not all_cards:
        await interaction.response.send_message(
            "There are no obtainable cards yet.",
            ephemeral=True
        )
        return

    cards_by_rarity = {}

    for card in all_cards:
        rarity = card["rarity"]

        if rarity not in cards_by_rarity:
            cards_by_rarity[rarity] = []

        cards_by_rarity[rarity].append(card["name"])

    description = ""

    for rarity in ["Common", "Rare", "Epic", "Legendary"]:
        if rarity in cards_by_rarity:
            description += f"**{rarity}**\n"
            for card_name in cards_by_rarity[rarity]:
                description += f"• {card_name}\n"
            description += "\n"

    embed = discord.Embed(
        title="Available Cards",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="card", description="View a specific card.")
@app_commands.describe(card_name="Choose a card to view.")
@app_commands.autocomplete(card_name=card_name_autocomplete)
async def card(interaction: discord.Interaction, card_name: str):
    selected_card = await get_card_by_name(card_name)

    if not selected_card:
        await interaction.response.send_message(
            "That card does not exist.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=selected_card["name"],
        description=f"**Rarity:** {selected_card['rarity']}",
        color=get_color(selected_card["rarity"])
    )

    embed.set_image(url=selected_card["image"])

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="trade", description="Offer to trade one of your cards for someone else's card.")
@app_commands.describe(
    user="The user you want to trade with.",
    your_card="The card you are offering.",
    their_card="The card you want from them."
)
@app_commands.autocomplete(
    your_card=card_name_autocomplete,
    their_card=card_name_autocomplete
)
async def trade(
    interaction: discord.Interaction,
    user: discord.Member,
    your_card: str,
    their_card: str
):
    if user.bot:
        await interaction.response.send_message(
            "You cannot trade with a bot.",
            ephemeral=True
        )
        return

    if user.id == interaction.user.id:
        await interaction.response.send_message(
            "You cannot trade with yourself.",
            ephemeral=True
        )
        return

    requester_card = await get_card_by_name(your_card)
    target_card = await get_card_by_name(their_card)

    if not requester_card or not target_card:
        await interaction.response.send_message(
            "One of those cards does not exist.",
            ephemeral=True
        )
        return

    if not await user_owns_card(interaction.user.id, requester_card["id"]):
        await interaction.response.send_message(
            f"You do not own **{requester_card['name']}**.",
            ephemeral=True
        )
        return

    if not await user_owns_card(user.id, target_card["id"]):
        await interaction.response.send_message(
            f"{user.display_name} does not own **{target_card['name']}**.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Trade Request",
        description=(
            f"{interaction.user.mention} wants to trade with {user.mention}.\n\n"
            f"**{interaction.user.display_name} gives:** {requester_card['name']}\n"
            f"**{user.display_name} gives:** {target_card['name']}\n\n"
            f"{user.mention}, accept or decline this trade."
        ),
        color=discord.Color.from_str("#9e659d")
    )

    view = TradeView(interaction.user, user, requester_card, target_card)

    await interaction.response.send_message(embed=embed, view=view)


@bot.tree.command(name="dropcard", description="Staff only: drop a collectible card.")
@app_commands.describe(
    rarity="Choose a rarity to drop from.",
    card_name="Choose the exact card name to drop."
)
@app_commands.choices(
    rarity=[
        app_commands.Choice(name="Common", value="Common"),
        app_commands.Choice(name="Rare", value="Rare"),
        app_commands.Choice(name="Epic", value="Epic"),
        app_commands.Choice(name="Legendary", value="Legendary"),
    ]
)
@app_commands.autocomplete(card_name=card_name_autocomplete)
async def dropcard(
    interaction: discord.Interaction,
    rarity: Optional[app_commands.Choice[str]] = None,
    card_name: Optional[str] = None
):
    if not is_staff(interaction.user):
        await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )
        return

    async with db_pool.acquire() as conn:
        if card_name:
            matching_cards = await conn.fetch(
                "SELECT * FROM cards WHERE LOWER(name) = LOWER($1);",
                card_name
            )
        elif rarity:
            matching_cards = await conn.fetch(
                "SELECT * FROM cards WHERE rarity = $1;",
                rarity.value
            )
        else:
            matching_cards = await conn.fetch("SELECT * FROM cards;")

    if not matching_cards:
        await interaction.response.send_message(
            "No cards found for that choice.",
            ephemeral=True
        )
        return

    selected_card = random.choice(matching_cards)
    embed = create_card_embed(selected_card)
    view = ClaimButton(selected_card)

    await interaction.response.send_message(embed=embed, view=view)


bot.run(TOKEN)