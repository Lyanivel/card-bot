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
BULLET_EMOJI = "<:heartdot:1499885862408818901>"
TOP_1_EMOJI = "<:1stplace:1499791803086405703>"
TOP_2_EMOJI = "<:2ndplace:1499791905884471406>"
TOP_3_EMOJI = "<:3rdplace:1499792046435729578>"
MAFIA_IMMUNITY_EMOJI = "<:mafiaimmunity:1499896444092416160>"
DAILY_BOOST_EMOJI = "<:dailyboost:1499751908754198609>"
WEEKLY_BOOST_EMOJI = "<:weeklyboost:1499751780366684180>"
LUCK_BOOST_EMOJI = "<:luckboost:1499715335253786745>"
WHEEL_SPIN_EMOJI = "<:wheelspin:1499751660006674562>"
TITLE_EMOJI = "<:title:1499751841481752686>"
SANC4OOS_EMOJI = "<:sanc4oos:1499903033042276493>"
DAILY_BOOST_PERCENT = 25
WEEKLY_BOOST_PERCENT = 20
# Optional: paste direct Discord/CDN image links here later for shop item thumbnails.
# The images you uploaded to ChatGPT cannot be used directly by the bot on Railway.
LOOT_CRATE_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499628974966444052/CCEE5E4A-7174-4490-AAFC-11C0EBE59404.png?ex=69f57dd1&is=69f42c51&hm=de07d24e7036229395f24221f8ce35b03dbb9917ecadf019dd98464b9317b396"
LEGENDARY_CRATE_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499628950811447426/80D3C92F-BF33-4F0A-998C-4D6D076D1678.png"
MAFIA_IMMUNITY_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499896615417417728/61BD24E4-0CF4-4673-A48F-CDFCAC7F71ED.png"
DAILY_BOOST_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499878356836024330/11DB2281-7A7A-4C48-8165-1D62D4FDCBD1.png"
WEEKLY_BOOST_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499878854502650068/95EFFB37-547A-4BBE-A436-1A2ED3777FC0.png"
LUCK_BOOST_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499879293239558285/B7FDEBBC-39D3-4FD0-862D-2F7D53C3AFDF.png"
WHEEL_SPIN_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499879748657221682/BECC68AE-295F-4D03-BCFA-AED03E1C3BB1.png"
TITLE_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499880391606145244/19EC808A-8F5C-4990-9C1A-49AB16C156A2.png"
SANC4OOS_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499902115605123243/0CC3FA91-214E-4938-B2A0-49605AD35984.png"
SHOP_ICON_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499880843756437625/Black_and_White_Geometri_Open_Here_Square_Sticker.png"
INVENTORY_ICON_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1499889754936840380/E46DF3DB-5008-48CE-B80B-645CBA562354.png"
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
    "mafiaimmunity": {
        "name": "Mafia Immunity",
        "price": 3500,
        "description": "Grants immunity for your next Mafia game. Staff must confirm and track usage.",
        "category": "Game Items",
        "manual_item": True
    },
    "dailyboost": {
        "name": "Daily Boost",
        "price": 500,
        "description": "Boosts your next daily claim by 25%. One use only.",
        "category": "Boosts",
        "boost_type": "daily",
        "duration_seconds": 24 * 60 * 60
    },
    "weeklyboost": {
        "name": "Weekly Boost",
        "price": 1500,
        "description": "Boosts your next weekly claim by 20%. One use only.",
        "category": "Boosts",
        "boost_type": "weekly",
        "duration_seconds": 7 * 24 * 60 * 60
    },
    "wheelentry": {
        "name": "Wheel Bonus Entry",
        "price": 1000,
        "description": "Grants one extra entry on a prize wheel you are already in. Staff must apply it manually.",
        "category": "Game Items",
        "manual_item": True
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
    "goosexchange": {
        "name": "Sanc to Goos Exchange",
        "price": 0,
        "description": "Exchange Sancs for Goos. Choose an amount from the item details.",
        "category": "Exchange",
        "exchange_menu": True
    },
    "goos100": {
        "name": "100 Goos Exchange",
        "price": 2500,
        "description": "Request 100 Goos. Staff must fulfill this manually.",
        "category": "Hidden",
        "goos_amount": 100
    },
    "goos250": {
        "name": "250 Goos Exchange",
        "price": 6000,
        "description": "Request 250 Goos. Staff must fulfill this manually.",
        "category": "Hidden",
        "goos_amount": 250
    },
    "goos500": {
        "name": "500 Goos Exchange",
        "price": 11000,
        "description": "Request 500 Goos. Staff must fulfill this manually.",
        "category": "Hidden",
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
            ALTER TABLE goos_exchange_requests
            ADD COLUMN IF NOT EXISTS claimed_by BIGINT;
        """)

        await conn.execute("""
            ALTER TABLE goos_exchange_requests
            ADD COLUMN IF NOT EXISTS completed_by BIGINT;
        """)

        await conn.execute("""
            ALTER TABLE goos_exchange_requests
            ADD COLUMN IF NOT EXISTS claimed_at TIMESTAMP;
        """)

        await conn.execute("""
            ALTER TABLE goos_exchange_requests
            ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id BIGINT PRIMARY KEY,
                staff_role_id BIGINT
            );
        """)

        await conn.execute("""
            ALTER TABLE server_settings
            ADD COLUMN IF NOT EXISTS goos_log_channel_id BIGINT;
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



async def get_goos_log_channel(guild_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT goos_log_channel_id FROM server_settings WHERE guild_id=$1",
            guild_id
        )


async def set_goos_log_channel_db(guild_id, channel_id):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO server_settings (guild_id, goos_log_channel_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET goos_log_channel_id=$2
        """, guild_id, channel_id)

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


def create_goos_log_embed_from_values(buyer_id, request_id, goos_amount, sancs_cost, claimed_by=None, completed_by=None):
    description = (
        f"**User:** <@{buyer_id}>\n"
        f"**Requested:** {goos_amount} Goos\n"
        f"**Cost:** {format_coins(sancs_cost)}"
    )

    if claimed_by:
        description += f"\n**Claimed by:** <@{claimed_by}>"

    if completed_by:
        description += f"\n**Completed by:** <@{completed_by}>"

    embed = discord.Embed(
        title="New Goos Exchange Request",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_footer(text="This request was created automatically after the user paid.")

    return embed

async def send_goos_log(interaction: discord.Interaction, request_id, shop_item):
    if not interaction.guild:
        return False

    channel_id = await get_goos_log_channel(interaction.guild.id)
    if not channel_id:
        return False

    channel = interaction.guild.get_channel(channel_id)
    if channel is None:
        channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception:
            return False

    staff_ping = await get_staff_ping(interaction)

    embed = create_goos_log_embed_from_values(
        buyer_id=interaction.user.id,
        request_id=request_id,
        goos_amount=shop_item["goos_amount"],
        sancs_cost=shop_item["price"]
    )

    await channel.send(
        content=staff_ping,
        embed=embed,
        view=GoosRequestView(
            request_id=request_id,
            buyer_id=interaction.user.id,
            goos_amount=shop_item["goos_amount"],
            sancs_cost=shop_item["price"]
        ),
        allowed_mentions=discord.AllowedMentions(roles=True, users=True)
    )

    return True

# ---------------- GOOS REQUEST STAFF VIEW ----------------

class GoosRequestView(discord.ui.View):
    def __init__(self, request_id, buyer_id, goos_amount, sancs_cost):
        super().__init__(timeout=None)
        self.request_id = request_id
        self.buyer_id = buyer_id
        self.goos_amount = goos_amount
        self.sancs_cost = sancs_cost
        self.claimed_by = None
        self.completed_by = None

    def build_embed(self):
        return create_goos_log_embed_from_values(
            buyer_id=self.buyer_id,
            request_id=self.request_id,
            goos_amount=self.goos_amount,
            sancs_cost=self.sancs_cost,
            claimed_by=self.claimed_by,
            completed_by=self.completed_by
        )

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary)
    async def claim_request(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await is_staff_member(interaction):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        success, message = await claim_goos_request(self.request_id, interaction.user.id)

        if not success:
            return await interaction.response.send_message(message, ephemeral=True)

        self.claimed_by = interaction.user.id
        button.disabled = True

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @discord.ui.button(label="Complete", style=discord.ButtonStyle.success)
    async def complete_request(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await is_staff_member(interaction):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        success, message = await complete_goos_request(self.request_id, interaction.user.id)

        if not success:
            return await interaction.response.send_message(message, ephemeral=True)

        self.completed_by = interaction.user.id

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

# ---------------- SHOP UI ----------------
class GoosExchangeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="100 Goos", value="goos100", description="2,500 Sancs"),
            discord.SelectOption(label="250 Goos", value="goos250", description="6,000 Sancs"),
            discord.SelectOption(label="500 Goos", value="goos500", description="11,000 Sancs"),
        ]

        super().__init__(
            placeholder="Choose a Goos exchange amount...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        item_key = self.values[0]
        shop_item = SHOP_ITEMS[item_key]
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
            """, interaction.user.id, item_key, shop_item["name"], shop_item["price"])

        request_id = await create_goos_request(
            interaction.user.id,
            shop_item["goos_amount"],
            shop_item["price"]
        )

        await interaction.response.send_message(
            f"{SANC4OOS_EMOJI} Goos exchange request created!\n"
            f"Request ID: **#{request_id}**\n"
            f"Requested: **{shop_item['goos_amount']} Goos**\n"
            f"Cost: **{format_coins(shop_item['price'])}**\n"
            f"A staff member will need to fulfill this manually. Please open a ticket and include your request ID.",
            ephemeral=True
        )

        await send_goos_log(interaction, request_id, shop_item)

        if not log_sent:
            await interaction.followup.send(
                "Heads up: no Goos log channel is set or I could not send to it. Please ask an admin to run `/setgooslogchannel`.",
                ephemeral=True
            )

class ExchangeItemView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(GoosExchangeSelect())

    @discord.ui.button(label="Back to Shop", style=discord.ButtonStyle.secondary)
    async def back_to_shop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=create_shop_embed(), view=ShopView())


class ShopSelect(discord.ui.Select):
    def __init__(self):
        options = []

        for key, item in SHOP_ITEMS.items():
            if item.get("category") == "Hidden":
                continue

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

        if item_key == "goosexchange":
            await interaction.response.edit_message(embed=embed, view=ExchangeItemView())
        else:
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
        if key != "goosexchange" and (current.lower() in item["name"].lower() or current.lower() in key.lower())
    ][:25]


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
    boost_bonus = 0
    if await get_active_boost(user_id, "daily"):
        boost_bonus = int(amount * DAILY_BOOST_PERCENT / 100)
        await clear_boost(user_id, "daily")
    total = amount + bonus + boost_bonus
    await add_balance(user_id, total)
    if found_crate:
        await add_loot_crate(user_id, "regular", 1)
    message = (
        f"{CURRENCY_EMOJI} | Take your Sancs and go! "
        f"**{total} {CURRENCY_EMOJI}**"
    )
    if streak >= 3:
        message += f" [{STREAK_EMOJI} {streak}]"
    if bonus > 0:
        message += f"\nMilestone bonus: **{format_coins(bonus)}**"
    if boost_bonus > 0:
        message += f"\n{DAILY_BOOST_EMOJI} Daily Boost bonus: **{format_coins(boost_bonus)}**"
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
    boost_bonus = 0
    if await get_active_boost(user_id, "weekly"):
        boost_bonus = int(amount * WEEKLY_BOOST_PERCENT / 100)
        await clear_boost(user_id, "weekly")
    total = amount + boost_bonus
    await add_balance(user_id, total)
    await add_loot_crate(user_id, "regular", 1)
    await set_cooldown(user_id, "weekly")
    message = (
        f"{WEEKLY_BOX_EMOJI} | Your Weekly Box is unsealing!\n"
        f"You received **{format_coins(total)}** and **1 {LOOT_CRATE_EMOJI} Loot Crate**."
    )
    if boost_bonus > 0:
        message += f"\n{WEEKLY_BOOST_EMOJI} Weekly Boost bonus: **{format_coins(boost_bonus)}**"
    await interaction.response.send_message(message)

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
            LIMIT 25
        """)
    if not rows:
        return await interaction.response.send_message("No balances yet.")
    place_emojis = {
        1: TOP_1_EMOJI,
        2: TOP_2_EMOJI,
        3: TOP_3_EMOJI,
    }
    text = ""
    for index, row in enumerate(rows, start=1):
        place = place_emojis.get(index, f"#{index}")
        user_mention = f"<@{row['user_id']}>"
        title = await get_title(row["user_id"])
        title_text = f" {title}" if title else ""
        text += f"{place} {user_mention}{title_text}\n"
        text += f"{BULLET_EMOJI} {format_coins(row['balance'])}\n"
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
    if shop_item.get("boost_type"):
        boost_type = shop_item["boost_type"]
        expires_at = await set_boost(
            interaction.user.id,
            boost_type,
            shop_item.get("duration_seconds", 3600)
        )
        if boost_type == "luck":
            boost_message = "Luck Boost activated for **1 hour**! Crate odds are improved"
        elif boost_type == "daily":
            boost_message = "Daily Boost activated! It will apply to your next /daily claim"
        elif boost_type == "weekly":
            boost_message = "Weekly Boost activated! It will apply to your next /weekly claim"
        else:
            boost_message = f"{shop_item['name']} activated"
        return await interaction.response.send_message(
            f"{boost_message} until <t:{expires_at}:t>."
        )
    if "title_text" in shop_item:
        await set_title(interaction.user.id, shop_item["title_text"])
        return await interaction.response.send_message(
            f"{interaction.user.mention} bought the title **{shop_item['title_text']}** for **{format_coins(shop_item['price'])}**!"
        )
    if shop_item.get("manual_item"):
        return await interaction.response.send_message(
            f"{interaction.user.mention} bought **{get_shop_item_emoji(shop_item)} {shop_item['name']}** for **{format_coins(shop_item['price'])}**! Staff will manually apply this reward."
        )
    if "goos_amount" in shop_item:
        request_id = await create_goos_request(
            interaction.user.id,
            shop_item["goos_amount"],
            shop_item["price"]
        )
        await interaction.response.send_message(
            f"{SANC4OOS_EMOJI} Goos exchange request created!\n"
            f"Request ID: **#{request_id}**\n"
            f"Requested: **{shop_item['goos_amount']} Goos**\n"
            f"Cost: **{format_coins(shop_item['price'])}**\n"
            f"A staff member will need to fulfill this manually. Please open a ticket and include your request ID.",
            ephemeral=True
        )

        await send_goos_log(interaction, request_id, shop_item)

        if not log_sent:
            await interaction.followup.send(
                "Heads up: no Goos log channel is set or I could not send to it. Please ask an admin to run `/setgooslogchannel`.",
                ephemeral=True
            )
        return
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
    embed.set_thumbnail(url=INVENTORY_ICON_URL)

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

@bot.tree.command(name="gooslogtest", description="Admin only: test the Goos log channel.")
async def gooslogtest(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "Only server administrators can test the Goos log channel.",
            ephemeral=True
        )

    channel_id = await get_goos_log_channel(interaction.guild.id)

    if not channel_id:
        return await interaction.response.send_message(
            "No Goos log channel is set. Run `/setgooslogchannel #channel` first.",
            ephemeral=True
        )

    channel = interaction.guild.get_channel(channel_id)

    if channel is None:
        channel = bot.get_channel(channel_id)

    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception:
            return await interaction.response.send_message(
                "I could not access that Goos log channel. Make sure I can view and send messages there.",
                ephemeral=True
            )

    await channel.send(
        f"{BULLET_EMOJI} Goos log test successful. This channel is connected."
    )

    await interaction.response.send_message(
        f"Goos log test sent to {channel.mention}.",
        ephemeral=True
    )


@bot.tree.command(name="setgooslogchannel", description="Admin only: set the staff log channel for Goos exchange requests.")
@app_commands.describe(channel="Channel where Goos exchange requests should be logged")
async def setgooslogchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "Only server administrators can set the Goos log channel.",
            ephemeral=True
        )

    await set_goos_log_channel_db(interaction.guild.id, channel.id)

    try:
        await channel.send(f"{BULLET_EMOJI} Goos exchange log channel connected.")
    except Exception:
        return await interaction.response.send_message(
            "I saved that channel, but I could not send a test message there. Please check my channel permissions.",
            ephemeral=True
        )

    await interaction.response.send_message(
        f"Goos exchange log channel set to {channel.mention}.",
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
