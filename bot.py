import os
import random
import time
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

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
WEEKLY_COOLDOWN = 7 * 24 * 60 * 60

DAILY_MIN = 75
DAILY_MAX = 195
DAILY_STREAK_BONUS_EVERY = 10
DAILY_STREAK_BONUS_AMOUNT = 500
DAILY_LOOT_CRATE_CHANCE = 2  # 2% chance

WEEKLY_MIN = 500
WEEKLY_MAX = 900

CLAIM_LOOT_CRATE_CHANCE = 5  # 5% chance

REGULAR_CRATE_MIN = 100
REGULAR_CRATE_MAX = 500

LEGENDARY_CRATE_MIN = 500
LEGENDARY_CRATE_MAX = 1500
LEGENDARY_SECOND_CARD_CHANCE = 20  # 20% chance

CURRENCY_EMOJI = "<:sancs:1499174670568788018>"
STREAK_EMOJI = "<:sancstreak:1499522539209359440>"
WEEKLY_BOX_EMOJI = "<:weeklybox:1499468656290168964>"
GIFT_BOX_EMOJI = "<:giftbox:1499565358074560582>"
LOOT_CRATE_EMOJI = "<:lootcrate:1499544926864802032>"
LEGENDARY_CRATE_EMOJI = "<:legendarycrate:1499567119233450055>"
BULLET_EMOJI = "<:heartdot:1499831890557800548>"

# Optional: paste direct Discord/CDN image links here later for shop item thumbnails.
# The images you uploaded to ChatGPT cannot be used directly by the bot on Railway.
LOOT_CRATE_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499628974966444052/CCEE5E4A-7174-4490-AAFC-11C0EBE59404.png?ex=69f57dd1&is=69f42c51&hm=de07d24e7036229395f24221f8ce35b03dbb9917ecadf019dd98464b9317b396"
LEGENDARY_CRATE_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499628950811447426/80D3C92F-BF33-4F0A-998C-4D6D076D1678.png?ex=69f57dcb&is=69f42c4b&hm=12738cf641cbdc40b176407fa1c6800bb7487955ddcf731a58e37e92b843d26e"

AVAILABLE_TITLES = {
    "Sanction Elite": 5000,
    "Loot Goblin": 5000,
    "Crate Hunter": 5000,
    "High Roller": 7500,
    "Card Collector": 5000,
}

SELL_VALUES = {
    "Common": 25,
    "Rare": 75,
    "Epic": 175,
    "Legendary": 400,
}

SHOP_ITEMS = {
    "lootcrate": {
        "name": "Loot Crate",
        "price": 750,
        "description": "Open it with /opencrate for Sancs and a random card.",
        "category": "Crates",
        "crate_type": "regular"
    },
    "legendarycrate": {
        "name": "Legendary Loot Crate",
        "price": 3000,
        "description": "Higher rewards, better rarity odds, and a chance for 2 cards.",
        "category": "Crates",
        "crate_type": "legendary"
    },
    "luckboost": {
        "name": "Luck Boost",
        "price": 2500,
        "description": "Better crate rarity odds for 1 hour.",
        "category": "Boosts",
        "boost_type": "luck",
        "duration_seconds": 60 * 60
    },
    "title": {
        "name": "Special Title",
        "price": 5000,
        "description": "Unlocks the title: Sanction Elite. More approved titles can be listed with /viewtitles.",
        "category": "Cosmetics",
        "title_text": "Sanction Elite"
    },
    "goos100": {
        "name": "100 Goos Exchange",
        "price": 2500,
        "description": "Request 100 Goos. Staff must fulfill this manually.",
        "category": "Exchange",
        "goos_amount": 100
    },
    "goos250": {
        "name": "250 Goos Exchange",
        "price": 6000,
        "description": "Request 250 Goos. Staff must fulfill this manually.",
        "category": "Exchange",
        "goos_amount": 250
    },
    "goos500": {
        "name": "500 Goos Exchange",
        "price": 11000,
        "description": "Request 500 Goos. Staff must fulfill this manually.",
        "category": "Exchange",
        "goos_amount": 500
    },
}

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

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS balances (
                user_id BIGINT PRIMARY KEY,
                balance BIGINT NOT NULL DEFAULT 0
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS cooldowns (
                user_id BIGINT NOT NULL,
                command_name TEXT NOT NULL,
                last_used BIGINT NOT NULL,
                PRIMARY KEY (user_id, command_name)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_streaks (
                user_id BIGINT PRIMARY KEY,
                streak_count INTEGER NOT NULL DEFAULT 0,
                last_claim_day BIGINT
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                item_key TEXT NOT NULL,
                item_name TEXT NOT NULL,
                price BIGINT NOT NULL,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS loot_crates (
                user_id BIGINT PRIMARY KEY,
                regular_count INTEGER NOT NULL DEFAULT 0,
                legendary_count INTEGER NOT NULL DEFAULT 0
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_boosts (
                user_id BIGINT NOT NULL,
                boost_type TEXT NOT NULL,
                expires_at BIGINT NOT NULL,
                PRIMARY KEY (user_id, boost_type)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_titles (
                user_id BIGINT PRIMARY KEY,
                title TEXT NOT NULL
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS goos_exchange_requests (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                goos_amount BIGINT NOT NULL,
                sancs_cost BIGINT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id BIGINT PRIMARY KEY,
                staff_role_id BIGINT
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS drop_channels (
                guild_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                PRIMARY KEY (guild_id, channel_id)
            );
        """)


# ---------------- HELPERS ----------------

def is_staff(member: discord.Member):
    return any(role.id == STAFF_ROLE_ID for role in member.roles)


async def get_staff_role(guild_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT staff_role_id FROM server_settings WHERE guild_id=$1",
            guild_id
        )


async def set_staff_role_db(guild_id, role_id):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO server_settings (guild_id, staff_role_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET staff_role_id=$2
        """, guild_id, role_id)


async def add_drop_channel_db(guild_id, channel_id):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO drop_channels (guild_id, channel_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
        """, guild_id, channel_id)


async def remove_drop_channel_db(guild_id, channel_id):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM drop_channels WHERE guild_id=$1 AND channel_id=$2",
            guild_id,
            channel_id
        )


async def get_drop_channels_db(guild_id):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT channel_id FROM drop_channels WHERE guild_id=$1",
            guild_id
        )
        return [row["channel_id"] for row in rows]


async def get_all_drop_channel_ids():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT channel_id FROM drop_channels")
        return [row["channel_id"] for row in rows]


async def is_staff_member(interaction: discord.Interaction):
    if not interaction.guild or not isinstance(interaction.user, discord.Member):
        return False

    if interaction.user.guild_permissions.administrator:
        return True

    saved_staff_role_id = await get_staff_role(interaction.guild.id)

    if saved_staff_role_id:
        return any(role.id == saved_staff_role_id for role in interaction.user.roles)

    return is_staff(interaction.user)


def get_color(rarity):
    return {
        "Common": discord.Color.from_str("#8b8b8b"),
        "Rare": discord.Color.from_str("#5c8df6"),
        "Epic": discord.Color.from_str("#9e659d"),
        "Legendary": discord.Color.from_str("#f5c542"),
    }.get(rarity, discord.Color.blurple())


def format_coins(amount: int):
    return f"{CURRENCY_EMOJI} {amount:,}"


def eastern_day_number():
    now = datetime.now(ZoneInfo("America/New_York"))
    return int(now.strftime("%Y%m%d"))


def previous_eastern_day_number(today: int):
    current_date = datetime.strptime(str(today), "%Y%m%d")
    previous_date = current_date - timedelta(days=1)
    return int(previous_date.strftime("%Y%m%d"))


def format_title(title):
    return title if title else "None"


def get_shop_item_emoji(item):
    if item.get("crate_type") == "regular":
        return LOOT_CRATE_EMOJI
    if item.get("crate_type") == "legendary":
        return LEGENDARY_CRATE_EMOJI
    return ""

def get_shop_item_image(item_key):
    if item_key == "lootcrate":
        return LOOT_CRATE_IMAGE_URL
    if item_key == "legendarycrate":
        return LEGENDARY_CRATE_IMAGE_URL
    return ""


def create_shop_embed():
    categories = ["Crates", "Boosts", "Cosmetics", "Exchange"]
    text = ""

    for category in categories:
        items = [
            (key, item)
            for key, item in SHOP_ITEMS.items()
            if item.get("category") == category
        ]

        if not items:
            continue

        text += f"**{category}**\n"

        for key, item in items:
            emoji = get_shop_item_emoji(item)
            emoji_text = f"{emoji} " if emoji else ""
            text += f"{BULLET_EMOJI} {emoji_text}`{item['name']}` [{format_coins(item['price'])}]\n"

        text += "\n"

    embed = discord.Embed(
        title="Shop",
        description=text or "The shop is currently empty.",
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_footer(text="Choose an item below to view details.")

    return embed


def create_shop_item_embed(item_key):
    item = SHOP_ITEMS[item_key]
    emoji = get_shop_item_emoji(item)
    image_url = get_shop_item_image(item_key)

    details = f"**Price:** [{format_coins(item['price'])}]\n\n"
    details += f"**Info:** {item['description']}\n\n"

    if item.get("crate_type") == "regular":
        details += (
            "**Contains:**\n"
            f"{BULLET_EMOJI} {format_coins(REGULAR_CRATE_MIN)} to {REGULAR_CRATE_MAX:,}\n"
            f"{BULLET_EMOJI} 1 random card\n\n"
        )
    elif item.get("crate_type") == "legendary":
        details += (
            "**Contains:**\n"
            f"{BULLET_EMOJI} {format_coins(LEGENDARY_CRATE_MIN)} to {LEGENDARY_CRATE_MAX:,}\n"
            f"{BULLET_EMOJI} Higher rarity card odds\n"
            f"{BULLET_EMOJI} {LEGENDARY_SECOND_CARD_CHANCE}% chance for a bonus card\n\n"
        )
    elif item.get("boost_type") == "luck":
        details += (
            "**Effect:**\n"
            f"{BULLET_EMOJI} Lasts 1 hour\n"
            f"{BULLET_EMOJI} Improves crate rarity odds while active\n\n"
        )
    elif "title_text" in item:
        details += (
            "**Title:**\n"
            f"{BULLET_EMOJI} {item['title_text']}\n"
            f"{BULLET_EMOJI} Shows in /inventory and /leaderboard\n\n"
        )
    elif "goos_amount" in item:
        details += (
            "**Exchange:**\n"
            f"{BULLET_EMOJI} Requests {item['goos_amount']} Goos\n"
            f"{BULLET_EMOJI} Staff must fulfill this manually\n\n"
        )

    details += f"Use `/buy` and choose `{item['name']}` to purchase."

    embed = discord.Embed(
        title=f"{emoji} {item['name']}",
        description=details,
        color=discord.Color.from_str("#9e659d")
    )

    if image_url:
        embed.set_thumbnail(url=image_url)

    embed.set_footer(text="Use the button below to return to the full shop list.")

    return embed


def card_label(card):
    return f"ID: {card['id']} {card['name']} ({card['rarity']})"


def format_card_line(card, amount=None, limited_note=""):
    amount_text = f" x{amount}" if amount is not None else ""
    return f"ID: {card['id']} {card['name']} ({card['rarity']}){amount_text}{limited_note}"


def clean_card_ref(card_ref: str):
    return card_ref.strip().replace("#", "").replace("ID", "").replace("id", "").strip()


def create_card_embed(card):
    embed = discord.Embed(
        title=f"{card['rarity']} Card Drop!",
        description=f"**{card['name']}** appeared!\n`ID: {card['id']}`",
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
            f"**ID:** {card['id']}\n"
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


async def get_card_by_id(card_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM cards WHERE id=$1",
            card_id
        )


async def get_card_by_ref(card_ref):
    cleaned = clean_card_ref(str(card_ref))

    if cleaned.isdigit():
        card = await get_card_by_id(int(cleaned))
        if card:
            return card

    return await get_card_by_name(str(card_ref))


async def get_active_card_by_ref(card_ref):
    cleaned = clean_card_ref(str(card_ref))

    async with db_pool.acquire() as conn:
        if cleaned.isdigit():
            return await conn.fetchrow(
                "SELECT * FROM cards WHERE id=$1 AND is_active = TRUE",
                int(cleaned)
            )

        return await conn.fetchrow(
            "SELECT * FROM cards WHERE LOWER(name)=LOWER($1) AND is_active = TRUE",
            str(card_ref)
        )


async def get_all_cards():
    async with db_pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM cards ORDER BY id")


async def get_active_cards():
    async with db_pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM cards WHERE is_active = TRUE ORDER BY id"
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
        return await conn.fetch("""
            SELECT DISTINCT cards.id, cards.name, cards.rarity
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE inventory.user_id=$1
            AND cards.is_active = TRUE
            ORDER BY cards.id
        """, user_id)


async def get_user_owned_cards_for_sell(user_id):
    async with db_pool.acquire() as conn:
        return await conn.fetch("""
            SELECT DISTINCT cards.id, cards.name, cards.rarity
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE inventory.user_id=$1
            ORDER BY cards.id
        """, user_id)


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


# ---------------- CURRENCY FUNCTIONS ----------------

async def get_balance(user_id):
    async with db_pool.acquire() as conn:
        balance = await conn.fetchval(
            "SELECT balance FROM balances WHERE user_id=$1",
            user_id
        )

        if balance is None:
            await conn.execute(
                "INSERT INTO balances (user_id, balance) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING",
                user_id
            )
            return 0

        return balance


async def add_balance(user_id, amount):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO balances (user_id, balance)
            VALUES ($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET balance = balances.balance + $2
        """, user_id, amount)


async def subtract_balance(user_id, amount):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            balance = await conn.fetchval(
                "SELECT balance FROM balances WHERE user_id=$1 FOR UPDATE",
                user_id
            )

            if balance is None:
                balance = 0
                await conn.execute(
                    "INSERT INTO balances (user_id, balance) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING",
                    user_id
                )

            if balance < amount:
                return False

            await conn.execute(
                "UPDATE balances SET balance = balance - $1 WHERE user_id=$2",
                amount,
                user_id
            )

            return True


async def transfer_balance(sender_id, receiver_id, amount):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            sender_balance = await conn.fetchval(
                "SELECT balance FROM balances WHERE user_id=$1 FOR UPDATE",
                sender_id
            )

            if sender_balance is None:
                sender_balance = 0
                await conn.execute(
                    "INSERT INTO balances (user_id, balance) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING",
                    sender_id
                )

            if sender_balance < amount:
                return False

            await conn.execute(
                "UPDATE balances SET balance = balance - $1 WHERE user_id=$2",
                amount,
                sender_id
            )

            await conn.execute("""
                INSERT INTO balances (user_id, balance)
                VALUES ($1, $2)
                ON CONFLICT (user_id)
                DO UPDATE SET balance = balances.balance + $2
            """, receiver_id, amount)

            return True


async def get_cooldown(user_id, command_name):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT last_used FROM cooldowns WHERE user_id=$1 AND command_name=$2",
            user_id,
            command_name
        )


async def set_cooldown(user_id, command_name):
    now = int(time.time())

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO cooldowns (user_id, command_name, last_used)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, command_name)
            DO UPDATE SET last_used=$3
        """, user_id, command_name, now)


async def update_daily_streak(user_id):
    today = eastern_day_number()
    yesterday = previous_eastern_day_number(today)

    async with db_pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT streak_count, last_claim_day FROM daily_streaks WHERE user_id=$1 FOR UPDATE",
                user_id
            )

            if not row:
                streak = 1
                await conn.execute(
                    "INSERT INTO daily_streaks (user_id, streak_count, last_claim_day) VALUES ($1, $2, $3)",
                    user_id,
                    streak,
                    today
                )
                return streak

            last_day = row["last_claim_day"]
            old_streak = row["streak_count"]

            if last_day == today:
                return old_streak

            if last_day == yesterday:
                streak = old_streak + 1
            else:
                streak = 1

            await conn.execute(
                "UPDATE daily_streaks SET streak_count=$1, last_claim_day=$2 WHERE user_id=$3",
                streak,
                today,
                user_id
            )

            return streak


async def sell_one_card(user_id, card_ref):
    card = await get_card_by_ref(card_ref)

    if not card:
        return False, None, 0

    async with db_pool.acquire() as conn:
        async with conn.transaction():
            card_entry = await conn.fetchrow("""
                SELECT inventory.id AS inventory_id, cards.id AS card_id, cards.name, cards.rarity
                FROM inventory
                JOIN cards ON cards.id = inventory.card_id
                WHERE inventory.user_id=$1
                AND cards.id=$2
                LIMIT 1
                FOR UPDATE
            """, user_id, card["id"])

            if not card_entry:
                return False, None, 0

            value = SELL_VALUES.get(card_entry["rarity"], 10)

            await conn.execute(
                "DELETE FROM inventory WHERE id=$1",
                card_entry["inventory_id"]
            )

            await conn.execute("""
                INSERT INTO balances (user_id, balance)
                VALUES ($1, $2)
                ON CONFLICT (user_id)
                DO UPDATE SET balance = balances.balance + $2
            """, user_id, value)

            return True, card_entry, value



# ---------------- BOOST / TITLE FUNCTIONS ----------------

async def get_active_boost(user_id, boost_type):
    now = int(time.time())

    async with db_pool.acquire() as conn:
        expires_at = await conn.fetchval(
            "SELECT expires_at FROM user_boosts WHERE user_id=$1 AND boost_type=$2",
            user_id,
            boost_type
        )

        if not expires_at:
            return None

        if expires_at <= now:
            await conn.execute(
                "DELETE FROM user_boosts WHERE user_id=$1 AND boost_type=$2",
                user_id,
                boost_type
            )
            return None

        return expires_at


async def set_boost(user_id, boost_type, duration_seconds):
    expires_at = int(time.time()) + duration_seconds

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_boosts (user_id, boost_type, expires_at)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, boost_type)
            DO UPDATE SET expires_at=$3
        """, user_id, boost_type, expires_at)

    return expires_at


async def get_title(user_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT title FROM user_titles WHERE user_id=$1",
            user_id
        )


async def set_title(user_id, title):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_titles (user_id, title)
            VALUES ($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET title=$2
        """, user_id, title)


async def create_goos_request(user_id, goos_amount, cost):
    async with db_pool.acquire() as conn:
        return await conn.fetchval("""
            INSERT INTO goos_exchange_requests (user_id, goos_amount, sancs_cost)
            VALUES ($1, $2, $3)
            RETURNING id
        """, user_id, goos_amount, cost)



# ---------------- LOOT CRATE FUNCTIONS ----------------

async def get_loot_crates(user_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT regular_count, legendary_count FROM loot_crates WHERE user_id=$1",
            user_id
        )

        if not row:
            await conn.execute(
                "INSERT INTO loot_crates (user_id, regular_count, legendary_count) VALUES ($1, 0, 0) ON CONFLICT (user_id) DO NOTHING",
                user_id
            )
            return 0, 0

        return row["regular_count"], row["legendary_count"]


async def add_loot_crate(user_id, crate_type="regular", amount=1):
    column = "legendary_count" if crate_type == "legendary" else "regular_count"

    async with db_pool.acquire() as conn:
        await conn.execute(f"""
            INSERT INTO loot_crates (user_id, {column})
            VALUES ($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET {column} = loot_crates.{column} + $2
        """, user_id, amount)


async def remove_loot_crate(user_id, crate_type="regular"):
    column = "legendary_count" if crate_type == "legendary" else "regular_count"

    async with db_pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchval(
                f"SELECT {column} FROM loot_crates WHERE user_id=$1 FOR UPDATE",
                user_id
            )

            if count is None:
                await conn.execute(
                    "INSERT INTO loot_crates (user_id, regular_count, legendary_count) VALUES ($1, 0, 0) ON CONFLICT (user_id) DO NOTHING",
                    user_id
                )
                return False

            if count <= 0:
                return False

            await conn.execute(
                f"UPDATE loot_crates SET {column} = {column} - 1 WHERE user_id=$1",
                user_id
            )

            return True


async def choose_random_card_with_weights(weights):
    rarity = random.choices(
        ["Common", "Rare", "Epic", "Legendary"],
        weights=weights,
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


async def choose_regular_crate_card(user_id=None):
    if user_id and await get_active_boost(user_id, "luck"):
        return await choose_random_card_with_weights([45, 30, 17, 8])

    return await choose_random_card_with_weights([60, 25, 10, 5])


async def choose_legendary_crate_card(user_id=None):
    if user_id and await get_active_boost(user_id, "luck"):
        return await choose_random_card_with_weights([15, 30, 30, 25])

    return await choose_random_card_with_weights([25, 35, 25, 15])


# ---------------- AUTOCOMPLETE ----------------

async def your_cards_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_user_active_cards(interaction.user.id)

    return [
        app_commands.Choice(name=card_label(card), value=str(card["id"]))
        for card in cards
        if current.lower() in card_label(card).lower()
    ][:25]


async def sell_cards_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_user_owned_cards_for_sell(interaction.user.id)

    return [
        app_commands.Choice(name=card_label(card), value=str(card["id"]))
        for card in cards
        if current.lower() in card_label(card).lower()
    ][:25]


async def all_active_cards_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_active_cards()

    return [
        app_commands.Choice(name=card_label(card), value=str(card["id"]))
        for card in cards
        if current.lower() in card_label(card).lower()
    ][:25]


async def shop_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=item["name"], value=key)
        for key, item in SHOP_ITEMS.items()
        if current.lower() in item["name"].lower() or current.lower() in key.lower()
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

    saved_channel_ids = await get_all_drop_channel_ids()
    possible_channel_ids = saved_channel_ids or DROP_CHANNEL_IDS

    if not possible_channel_ids:
        return

    channel = bot.get_channel(random.choice(possible_channel_ids))
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
                    f"You are on cooldown. Try again in {remaining}s.",
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

        found_crate = random.randint(1, 100) <= CLAIM_LOOT_CRATE_CHANCE

        if found_crate:
            await add_loot_crate(uid, "regular", 1)

        content = f"{interaction.user.mention} claimed **{self.card['name']}**! `ID: {self.card['id']}`"

        if found_crate:
            content += f"\n{GIFT_BOX_EMOJI} You found a Loot Crate! Use `/opencrate`"

        await interaction.response.edit_message(
            content=content,
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
                f"**{self.card['name']}** `ID: {self.card['id']}` has been removed from future drops and card lists.\n"
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



# ---------------- SHOP UI ----------------

class ShopSelect(discord.ui.Select):
    def __init__(self):
        options = []

        for key, item in SHOP_ITEMS.items():
            options.append(
                discord.SelectOption(
                    label=item["name"],
                    value=key,
                    description=item["description"][:100]
                )
            )

        super().__init__(
            placeholder="Select an item to view details...",
            min_values=1,
            max_values=1,
            options=options[:25]
        )

    async def callback(self, interaction: discord.Interaction):
        item_key = self.values[0]
        embed = create_shop_item_embed(item_key)
        await interaction.response.edit_message(embed=embed, view=BackToShopView())


class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(ShopSelect())


class BackToShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="Back to Shop", style=discord.ButtonStyle.secondary)
    async def back_to_shop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=create_shop_embed(), view=ShopView())


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


@bot.tree.command(name="balance", description="View your balance or another user's balance.")
@app_commands.describe(user="Choose whose balance to view")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    bal = await get_balance(target.id)

    embed = discord.Embed(
        title=f"{target.display_name}'s Balance",
        description=f"**Balance:** {format_coins(bal)}",
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="daily", description="Claim your daily Sancs and build a streak.")
async def daily(interaction: discord.Interaction):
    user_id = interaction.user.id
    today = eastern_day_number()

    async with db_pool.acquire() as conn:
        last_claim_day = await conn.fetchval(
            "SELECT last_claim_day FROM daily_streaks WHERE user_id=$1",
            user_id
        )

    if last_claim_day == today:
        return await interaction.response.send_message(
            "You already claimed your daily today. Daily resets at midnight Eastern.",
            ephemeral=True
        )

    amount = random.randint(DAILY_MIN, DAILY_MAX)
    streak = await update_daily_streak(user_id)

    bonus = 0
    if streak % DAILY_STREAK_BONUS_EVERY == 0:
        bonus = DAILY_STREAK_BONUS_AMOUNT

    found_crate = random.randint(1, 100) <= DAILY_LOOT_CRATE_CHANCE

    total = amount + bonus
    await add_balance(user_id, total)

    if found_crate:
        await add_loot_crate(user_id, "regular", 1)

    message = (
        f"{CURRENCY_EMOJI} | Take your Sancs and go! "
        f"**{amount} {CURRENCY_EMOJI}**"
    )

    if streak >= 3:
        message += f" [{STREAK_EMOJI} {streak}]"

    if bonus > 0:
        message += f"\nMilestone bonus: **{format_coins(bonus)}**"

    if found_crate:
        message += f"\n{GIFT_BOX_EMOJI} You found a Loot Crate! Use `/opencrate`"

    await interaction.response.send_message(message)


@bot.tree.command(name="weekly", description="Claim your weekly reward and Loot Crate.")
async def weekly(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = int(time.time())
    last_used = await get_cooldown(user_id, "weekly")

    if last_used and now - last_used < WEEKLY_COOLDOWN:
        remaining = WEEKLY_COOLDOWN - (now - last_used)
        days = remaining // 86400
        hours = (remaining % 86400) // 3600

        return await interaction.response.send_message(
            f"You already claimed your weekly. Try again in {days}d {hours}h.",
            ephemeral=True
        )

    amount = random.randint(WEEKLY_MIN, WEEKLY_MAX)
    await add_balance(user_id, amount)
    await add_loot_crate(user_id, "regular", 1)
    await set_cooldown(user_id, "weekly")

    await interaction.response.send_message(
        f"{WEEKLY_BOX_EMOJI} | Your Weekly Box is unsealing!\n"
        f"You received **{format_coins(amount)}** and **1 {LOOT_CRATE_EMOJI} Loot Crate**."
    )


@bot.tree.command(name="givecurrency", description="Give some of your currency to another user.")
@app_commands.describe(
    user="User to give currency to",
    amount="Amount to give"
)
async def givecurrency(interaction: discord.Interaction, user: discord.Member, amount: int):
    if user.bot:
        return await interaction.response.send_message("You cannot give currency to a bot.", ephemeral=True)

    if user.id == interaction.user.id:
        return await interaction.response.send_message("You cannot give currency to yourself.", ephemeral=True)

    if amount <= 0:
        return await interaction.response.send_message("Amount must be greater than 0.", ephemeral=True)

    success = await transfer_balance(interaction.user.id, user.id, amount)

    if not success:
        return await interaction.response.send_message(
            "You do not have enough currency.",
            ephemeral=True
        )

    await interaction.response.send_message(
        f"{interaction.user.mention} gave {user.mention} **{format_coins(amount)}**."
    )


@bot.tree.command(name="addbal", description="Staff only: add currency to a user's balance.")
@app_commands.describe(
    user="User to add balance to",
    amount="Amount to add"
)
async def addbal(interaction: discord.Interaction, user: discord.Member, amount: int):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    if amount <= 0:
        return await interaction.response.send_message("Amount must be greater than 0.", ephemeral=True)

    await add_balance(user.id, amount)

    await interaction.response.send_message(
        f"Added **{format_coins(amount)}** to {user.mention}'s balance."
    )


@bot.tree.command(name="sell", description="Sell one of your cards for currency.")
@app_commands.describe(card="Choose the card to sell")
@app_commands.autocomplete(card=sell_cards_autocomplete)
async def sell(interaction: discord.Interaction, card: str):
    success, card_entry, value = await sell_one_card(interaction.user.id, card)

    if not success:
        return await interaction.response.send_message(
            "You do not own that card.",
            ephemeral=True
        )

    await interaction.response.send_message(
        f"You sold **{card_entry['name']}** `ID: {card_entry['card_id']}` ({card_entry['rarity']}) for **{format_coins(value)}**."
    )


@bot.tree.command(name="leaderboard", description="View the richest users.")
async def leaderboard(interaction: discord.Interaction):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT user_id, balance
            FROM balances
            ORDER BY balance DESC
            LIMIT 10
        """)

    if not rows:
        return await interaction.response.send_message("No balances yet.")

    place_emojis = {
        1: "ð¥",
        2: "ð¥",
        3: "ð¥",
    }

    text = ""

    for index, row in enumerate(rows, start=1):
        place = place_emojis.get(index, f"**{index}.**")
        user_mention = f"<@{row['user_id']}>"

        title = await get_title(row["user_id"])
        title_text = f" *{title}*" if title else ""

        text += f"{place} {user_mention}{title_text}\n"
        text += f"{BULLET_EMOJI} {format_coins(row['balance'])}\n\n"

    embed = discord.Embed(
        title="Currency Leaderboard",
        description=text,
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="shop", description="View the currency shop.")
async def shop(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_shop_embed(), view=ShopView())


@bot.tree.command(name="viewtitles", description="View approved titles available for purchase.")
async def viewtitles(interaction: discord.Interaction):
    text = ""

    for title_name, price in AVAILABLE_TITLES.items():
        text += f"{BULLET_EMOJI} `{title_name}` [{format_coins(price)}]\n"

    embed = discord.Embed(
        title="Available Titles",
        description=text or "No titles are available right now.",
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_footer(text="For now, /buy Special Title unlocks Sanction Elite. More title buying options can be added later.")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="buy", description="Buy an item from the shop.")
@app_commands.describe(item="Choose an item to buy")
@app_commands.autocomplete(item=shop_autocomplete)
async def buy(interaction: discord.Interaction, item: str):
    if item not in SHOP_ITEMS:
        return await interaction.response.send_message("That shop item does not exist.", ephemeral=True)

    shop_item = SHOP_ITEMS[item]
    success = await subtract_balance(interaction.user.id, shop_item["price"])

    if not success:
        return await interaction.response.send_message(
            f"You do not have enough currency. This costs **{format_coins(shop_item['price'])}**.",
            ephemeral=True
        )

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO purchases (user_id, item_key, item_name, price)
            VALUES ($1, $2, $3, $4)
        """, interaction.user.id, item, shop_item["name"], shop_item["price"])

    if "crate_type" in shop_item:
        await add_loot_crate(interaction.user.id, shop_item["crate_type"], 1)
        emoji = LEGENDARY_CRATE_EMOJI if shop_item.get("crate_type") == "legendary" else LOOT_CRATE_EMOJI

        return await interaction.response.send_message(
            f"{interaction.user.mention} bought **1 {emoji} {shop_item['name']}** for **{format_coins(shop_item['price'])}**!"
        )

    if shop_item.get("boost_type") == "luck":
        expires_at = await set_boost(
            interaction.user.id,
            "luck",
            shop_item.get("duration_seconds", 3600)
        )

        return await interaction.response.send_message(
            f"Luck Boost activated for **1 hour**! Crate odds are improved until <t:{expires_at}:t>."
        )

    if "title_text" in shop_item:
        await set_title(interaction.user.id, shop_item["title_text"])

        return await interaction.response.send_message(
            f"{interaction.user.mention} bought the title **{shop_item['title_text']}** for **{format_coins(shop_item['price'])}**!"
        )

    if "goos_amount" in shop_item:
        request_id = await create_goos_request(
            interaction.user.id,
            shop_item["goos_amount"],
            shop_item["price"]
        )

        return await interaction.response.send_message(
            f"Goos exchange request created!\n"
            f"Request ID: **#{request_id}**\n"
            f"Requested: **{shop_item['goos_amount']} Goos**\n"
            f"Cost: **{format_coins(shop_item['price'])}**\n"
            f"A staff member will need to fulfill this manually."
        )

    await interaction.response.send_message(
        f"{interaction.user.mention} bought **{shop_item['name']}** for **{format_coins(shop_item['price'])}**!"
    )


@bot.tree.command(name="opencrate", description="Open a Loot Crate or Legendary Loot Crate.")
@app_commands.describe(crate_type="Choose which crate to open")
@app_commands.choices(
    crate_type=[
        app_commands.Choice(name="Loot Crate", value="regular"),
        app_commands.Choice(name="Legendary Loot Crate", value="legendary"),
    ]
)
async def opencrate(
    interaction: discord.Interaction,
    crate_type: app_commands.Choice[str]
):
    user_id = interaction.user.id
    selected_type = crate_type.value

    removed = await remove_loot_crate(user_id, selected_type)

    if not removed:
        crate_name = "Legendary Loot Crate" if selected_type == "legendary" else "Loot Crate"
        return await interaction.response.send_message(
            f"You do not have any **{crate_name}s** to open.",
            ephemeral=True
        )

    if selected_type == "legendary":
        coins = random.randint(LEGENDARY_CRATE_MIN, LEGENDARY_CRATE_MAX)
        first_card = await choose_legendary_crate_card(user_id)
        second_card = None

        if random.randint(1, 100) <= LEGENDARY_SECOND_CARD_CHANCE:
            second_card = await choose_legendary_crate_card(user_id)

        crate_emoji = LEGENDARY_CRATE_EMOJI
        crate_name = "Legendary Loot Crate"
    else:
        coins = random.randint(REGULAR_CRATE_MIN, REGULAR_CRATE_MAX)
        first_card = await choose_regular_crate_card(user_id)
        second_card = None
        crate_emoji = LOOT_CRATE_EMOJI
        crate_name = "Loot Crate"

    await add_balance(user_id, coins)

    rewards = f"**Sancs:** {format_coins(coins)}"

    if first_card:
        await add_card_to_inventory(user_id, first_card["id"])
        rewards += f"\n**Card:** ID: {first_card['id']} {first_card['name']} ({first_card['rarity']})"

    if second_card:
        await add_card_to_inventory(user_id, second_card["id"])
        rewards += f"\n**Bonus Card:** ID: {second_card['id']} {second_card['name']} ({second_card['rarity']})"

    embed = discord.Embed(
        title=f"{crate_emoji} {crate_name} Opened!",
        description=rewards,
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="viewcard", description="View a specific card.")
@app_commands.describe(card="Choose a card by ID or name")
@app_commands.autocomplete(card=all_active_cards_autocomplete)
async def viewcard(interaction: discord.Interaction, card: str):
    c = await get_card_by_ref(card)
    if not c:
        return await interaction.response.send_message("Not found.", ephemeral=True)

    active_text = "Currently obtainable" if c["is_active"] else "Unobtainable / limited"
    embed = discord.Embed(
        title=c["name"],
        description=(
            f"**ID:** {c['id']}\n"
            f"**Rarity:** {c['rarity']}\n"
            f"**Status:** {active_text}"
        ),
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
        grouped.setdefault(c["rarity"], []).append(c)

    text = ""

    for rarity in ["Common", "Rare", "Epic", "Legendary"]:
        if rarity in grouped:
            text += f"**{rarity}**\n"
            for card in grouped[rarity]:
                text += f"{BULLET_EMOJI} ID: {card['id']} {card['name']} ({card['rarity']})\n"
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
    bal = await get_balance(user.id)
    regular_crates, legendary_crates = await get_loot_crates(user.id)
    title = await get_title(user.id)

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT cards.id, cards.name, cards.rarity, cards.is_active, COUNT(*) as amount
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE user_id=$1
            GROUP BY cards.id, cards.name, cards.rarity, cards.is_active
            ORDER BY cards.rarity, cards.id
        """, user.id)

    text = f"**Balance:** {format_coins(bal)}\n"
    text += f"{BULLET_EMOJI} {LOOT_CRATE_EMOJI} **Loot Crates:** {regular_crates}\n"
    text += f"{BULLET_EMOJI} {LEGENDARY_CRATE_EMOJI} **Legendary Loot Crates:** {legendary_crates}\n\n"

    if not rows:
        text += "No cards yet."
    else:
        for r in rows:
            limited_note = "" if r["is_active"] else " *(unobtainable)*"
            text += f"{BULLET_EMOJI} ID: {r['id']} {r['name']} ({r['rarity']}) x{r['amount']}{limited_note}\n"

    inventory_title = f"{title} {user.display_name}'s Inventory" if title else f"{user.display_name}'s Inventory"

    embed = discord.Embed(
        title=inventory_title,
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

    your_card_data = await get_active_card_by_ref(your_card)
    their_card_data = await get_active_card_by_ref(their_card)

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
            f"{interaction.user.mention} offers **{your_card_data['name']}** `ID: {your_card_data['id']}`\n"
            f"in exchange for **{their_card_data['name']}** `ID: {their_card_data['id']}` from {user.mention}\n\n"
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
    if not await is_staff_member(interaction):
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
                f"Reactivated/updated **{name}** as a **{rarity.value}** card. `ID: {existing_card['id']}`"
            )

        new_id = await conn.fetchval(
            "INSERT INTO cards (name, rarity, image, is_active) VALUES ($1,$2,$3, TRUE) RETURNING id",
            name,
            rarity.value,
            image
        )

    await interaction.response.send_message(f"Added **{name}** as a **{rarity.value}** card. `ID: {new_id}`")


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
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    async with db_pool.acquire() as conn:
        if card_name:
            cleaned = clean_card_ref(card_name)
            if cleaned.isdigit():
                cards = await conn.fetch(
                    "SELECT * FROM cards WHERE id=$1 AND is_active = TRUE",
                    int(cleaned)
                )
            else:
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
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    card = await get_active_card_by_ref(card_name)

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
            f"Are you sure you want to remove **{card['name']}** `ID: {card['id']}` from future drops and card lists?\n\n"
            f"Members who already own it will **keep it**."
        ),
        color=discord.Color.red()
    )

    await interaction.response.send_message(
        embed=embed,
        view=RemoveCardView(interaction.user, card),
        ephemeral=True
    )



@bot.tree.command(name="setstaffrole", description="Admin only: set the staff role for this server.")
@app_commands.describe(role="Role allowed to use staff bot commands")
async def setstaffrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "Only server administrators can set the staff role.",
            ephemeral=True
        )

    await set_staff_role_db(interaction.guild.id, role.id)

    await interaction.response.send_message(
        f"Staff role set to {role.mention}."
    )


@bot.tree.command(name="adddropchannel", description="Staff only: add a channel for automatic card drops.")
@app_commands.describe(channel="Channel where automatic drops can happen")
async def adddropchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    await add_drop_channel_db(interaction.guild.id, channel.id)

    await interaction.response.send_message(
        f"Added {channel.mention} as a drop channel."
    )


@bot.tree.command(name="removedropchannel", description="Staff only: remove a channel from automatic card drops.")
@app_commands.describe(channel="Channel to remove from automatic drops")
async def removedropchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    await remove_drop_channel_db(interaction.guild.id, channel.id)

    await interaction.response.send_message(
        f"Removed {channel.mention} from drop channels."
    )


@bot.tree.command(name="listdropchannels", description="View this server's automatic card drop channels.")
async def listdropchannels(interaction: discord.Interaction):
    channels = await get_drop_channels_db(interaction.guild.id)

    if not channels:
        return await interaction.response.send_message("No drop channels set for this server.")

    mentions = []

    for channel_id in channels:
        channel = interaction.guild.get_channel(channel_id)
        mentions.append(channel.mention if channel else f"`{channel_id}`")

    embed = discord.Embed(
        title="Drop Channels",
        description="\n".join(mentions),
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)


# ---------------- RUN ----------------

bot.run(TOKEN)
