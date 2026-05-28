import os
import random
import time
import asyncio
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
WEEKLY_DAILY_BOOST_CHANCE = 15
WEEKLY_LUCK_BOOST_CHANCE = 10
WEEKLY_WEEKLY_BOOST_CHANCE = 5
CLAIM_LOOT_CRATE_CHANCE = 5  # 5% chance
REGULAR_CRATE_MIN = 100
REGULAR_CRATE_MAX = 500
LEGENDARY_CRATE_MIN = 500
LEGENDARY_CRATE_MAX = 1500
LEGENDARY_SECOND_CARD_CHANCE = 20  # 20% chance
CURRENCY_EMOJI = "<:sancs:1499174670568788018>"
STREAK_EMOJI = "<:sancstreak:1499522539209359440>"
WEEKLY_BOX_EMOJI = "<:weeklybox:1500637762074837012>"
WEEKLY_OPENED_EMOJI = "<:weeklyopened:1500637809084731443>"
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
CUSTOM_EMOJI_SHOP = "<:customemoji:1499912654528053329>"
TOGGLE_ON_EMOJI = "<:toggleon:1501644856764797038>"
TOGGLE_OFF_EMOJI = "<:toggleoff:1501644991188172954>"
SNIPE_EMOJI = "<:snipe:1501413204939641025>"
LEGENDARY_SNIPER_EMOJI = "<:legendarysnipe:1501572128544391249>"
BUSH_1_EMOJI = "<:bush:1501411561758003313>"
BUSH_2_EMOJI = "<:bush:1501411561758003313>"
BUSH_3_EMOJI = "<:bush:1501411561758003313>"
SNIPE_HIT_EMOJI = "<:bang:1501411689776808067>"
SNIPE_MISS_EMOJI = "<:safe:1501411804025327797>"
DAILY_BOOST_PERCENT = 25
WEEKLY_BOOST_PERCENT = 20
SNIPE_PRICE = 2500
SNIPE_COOLDOWN = 10 * 60
SNIPE_MUTE_MINUTES = 5
MAX_TRADES_PER_DAY = 5
MAX_GIVECURRENCY_PER_DAY = 25000
MAX_GIVECURRENCY_PER_TRANSFER = 10000
OWNER_PROTECTION_MESSAGES = [
    "{target} SHOULD have been muted. Discord chose peace instead of violence.",
    "{target} was eliminated spiritually because Discord refused the paperwork.",
    "Direct hit on {target}! Unfortunately, Discord said 'absolutely not.'",
    "{target} got saved by corporate intervention. Booo!",
]

SNIPE_SUCCESS_MESSAGES = [
    "{target} got caught lacking, pack it up immediately!",
    "{target} never even saw it coming.",
    "{target}? Folded instantly.",
    "{target}, geesh you should’ve hid better!",
]

SNIPE_MISS_MESSAGES = [
    "{target} escaped safely. Haha you missed!",
    "{target} escaped. That shot needs to be investigated.",
    "{target} escaped while {sniper} hit absolutely nothing.",
    "{target} escaped and immediately started talking trash.",
]
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
CUSTOM_EMOJI_IMAGE_URL = "https://cdn.discordapp.com/attachments/1493341908246859967/1500015304888029194/4273C882-7CD2-4AE3-A92C-0EEA5EF8A730.png"
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
    "sniper": {
        "name": "Sniper",
        "price": SNIPE_PRICE,
        "description": "Start a snipe attempt against another user. If your shot hits, they are muted for 5 minutes.",
        "category": "Game Items",
        "snipe_item": "regular"
    },

    "legendarysniper": {
        "name": "Legendary Sniper",
        "price": 7500,
        "description": "A stronger sniper with only 3 bushes to search.",
        "category": "Game Items",
        "snipe_item": "legendary"
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
        "price": 0,
        "description": "Buy preset titles to show after your name in leaderboard and inventory.",
        "category": "Cosmetics",
        "title_menu": True
    },
    "profileemoji": {
        "name": "Profile Emoji",
        "price": 0,
        "description": "Buy preset emojis to show after your name in leaderboard and inventory.",
        "category": "Cosmetics",
        "profile_emoji_menu": True
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
        "price": 7500,
        "description": "Request 100 Goos. Staff must fulfill this manually.",
        "category": "Hidden",
        "goos_amount": 100
    },
    "goos250": {
        "name": "250 Goos Exchange",
        "price": 18000,
        "description": "Request 250 Goos. Staff must fulfill this manually.",
        "category": "Hidden",
        "goos_amount": 250
    },
    "goos500": {
        "name": "500 Goos Exchange",
        "price": 35000,
        "description": "Request 500 Goos. Staff must fulfill this manually.",
        "category": "Hidden",
        "goos_amount": 500
    },
}
last_claim_times = {}
last_auto_drop_times = {}
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
            CREATE TABLE IF NOT EXISTS user_daily_limits (
                user_id BIGINT NOT NULL,
                action_name TEXT NOT NULL,
                day_number BIGINT NOT NULL,
                count_value BIGINT NOT NULL DEFAULT 0,
                amount_value BIGINT NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, action_name, day_number)
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
            CREATE TABLE IF NOT EXISTS user_custom_emojis (
                user_id BIGINT PRIMARY KEY,
                emoji TEXT NOT NULL
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS profile_emojis (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                emoji TEXT NOT NULL,
                price BIGINT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_owned_profile_emojis (
                user_id BIGINT NOT NULL,
                profile_emoji_id INTEGER NOT NULL REFERENCES profile_emojis(id),
                PRIMARY KEY (user_id, profile_emoji_id)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_owned_titles (
                user_id BIGINT NOT NULL,
                title TEXT NOT NULL,
                PRIMARY KEY (user_id, title)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS shop_titles (
                id SERIAL PRIMARY KEY,
                title TEXT UNIQUE NOT NULL,
                price BIGINT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_emoji_requests (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                emoji TEXT NOT NULL,
                price BIGINT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by BIGINT,
                reviewed_at TIMESTAMP,
                reason TEXT
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
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS drop_channels (
                guild_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                PRIMARY KEY (guild_id, channel_id)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS drop_settings (
                guild_id BIGINT PRIMARY KEY,
                auto_drop_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                auto_drop_minutes INTEGER NOT NULL DEFAULT 30,
                auto_drop_chance INTEGER NOT NULL DEFAULT 40,
                claim_cooldown_seconds INTEGER NOT NULL DEFAULT 30
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS economy_settings (
                guild_id BIGINT PRIMARY KEY,
                daily_min INTEGER NOT NULL DEFAULT 75,
                daily_max INTEGER NOT NULL DEFAULT 195,
                weekly_min INTEGER NOT NULL DEFAULT 500,
                weekly_max INTEGER NOT NULL DEFAULT 900,
                daily_streak_bonus_every INTEGER NOT NULL DEFAULT 10,
                daily_streak_bonus_amount INTEGER NOT NULL DEFAULT 500,
                daily_loot_crate_chance INTEGER NOT NULL DEFAULT 2,
                weekly_daily_boost_chance INTEGER NOT NULL DEFAULT 15,
                weekly_luck_boost_chance INTEGER NOT NULL DEFAULT 10,
                weekly_weekly_boost_chance INTEGER NOT NULL DEFAULT 5
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS crate_settings (
                guild_id BIGINT PRIMARY KEY,
                regular_crate_min INTEGER NOT NULL DEFAULT 100,
                regular_crate_max INTEGER NOT NULL DEFAULT 500,
                legendary_crate_min INTEGER NOT NULL DEFAULT 500,
                legendary_crate_max INTEGER NOT NULL DEFAULT 1500,
                legendary_second_card_chance INTEGER NOT NULL DEFAULT 20,
                claim_loot_crate_chance INTEGER NOT NULL DEFAULT 5
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS snipe_items (
                user_id BIGINT PRIMARY KEY,
                regular_count INTEGER NOT NULL DEFAULT 0,
                legendary_count INTEGER NOT NULL DEFAULT 0
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS snipe_settings (
                guild_id BIGINT PRIMARY KEY,
                staff_snipe_enabled BOOLEAN NOT NULL DEFAULT TRUE
            );
        """)

        await conn.execute("""
            ALTER TABLE snipe_settings
            ADD COLUMN IF NOT EXISTS snipe_cooldown_seconds BIGINT DEFAULT 300;
        """)

        await conn.execute("""
            ALTER TABLE snipe_settings
            ADD COLUMN IF NOT EXISTS snipe_mute_minutes BIGINT DEFAULT 5;
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

    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            guild_id
        )

    async with db_pool.acquire() as conn:
        await conn.execute("""
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
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

async def get_drop_settings(guild_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT auto_drop_enabled, auto_drop_minutes, auto_drop_chance, claim_cooldown_seconds FROM drop_settings WHERE guild_id=$1",
            guild_id
        )

        if not row:
            await conn.execute("""
                INSERT INTO drop_settings (guild_id, auto_drop_enabled, auto_drop_minutes, auto_drop_chance, claim_cooldown_seconds)
                VALUES ($1, TRUE, $2, $3, $4)
                ON CONFLICT (guild_id) DO NOTHING
            """, guild_id, AUTO_DROP_MINUTES, AUTO_DROP_CHANCE, CLAIM_COOLDOWN)

            return {
                "auto_drop_enabled": True,
                "auto_drop_minutes": AUTO_DROP_MINUTES,
                "auto_drop_chance": AUTO_DROP_CHANCE,
                "claim_cooldown_seconds": CLAIM_COOLDOWN
            }

        return {
            "auto_drop_enabled": row["auto_drop_enabled"],
            "auto_drop_minutes": row["auto_drop_minutes"] or AUTO_DROP_MINUTES,
            "auto_drop_chance": row["auto_drop_chance"] or AUTO_DROP_CHANCE,
            "claim_cooldown_seconds": row["claim_cooldown_seconds"] or CLAIM_COOLDOWN
        }

async def set_auto_drop_enabled_db(guild_id, enabled: bool):
    settings = await get_drop_settings(guild_id)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO drop_settings (guild_id, auto_drop_enabled, auto_drop_minutes, auto_drop_chance, claim_cooldown_seconds)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id)
            DO UPDATE SET auto_drop_enabled = EXCLUDED.auto_drop_enabled
        """, guild_id, enabled, settings["auto_drop_minutes"], settings["auto_drop_chance"], settings["claim_cooldown_seconds"])

async def set_auto_drop_minutes_db(guild_id, minutes: int):
    settings = await get_drop_settings(guild_id)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO drop_settings (guild_id, auto_drop_enabled, auto_drop_minutes, auto_drop_chance, claim_cooldown_seconds)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id)
            DO UPDATE SET auto_drop_minutes = EXCLUDED.auto_drop_minutes
        """, guild_id, settings["auto_drop_enabled"], minutes, settings["auto_drop_chance"], settings["claim_cooldown_seconds"])

async def set_auto_drop_chance_db(guild_id, chance: int):
    settings = await get_drop_settings(guild_id)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO drop_settings (guild_id, auto_drop_enabled, auto_drop_minutes, auto_drop_chance, claim_cooldown_seconds)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id)
            DO UPDATE SET auto_drop_chance = EXCLUDED.auto_drop_chance
        """, guild_id, settings["auto_drop_enabled"], settings["auto_drop_minutes"], chance, settings["claim_cooldown_seconds"])

async def set_claim_cooldown_db(guild_id, seconds: int):
    settings = await get_drop_settings(guild_id)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO drop_settings (guild_id, auto_drop_enabled, auto_drop_minutes, auto_drop_chance, claim_cooldown_seconds)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id)
            DO UPDATE SET claim_cooldown_seconds = EXCLUDED.claim_cooldown_seconds
        """, guild_id, settings["auto_drop_enabled"], settings["auto_drop_minutes"], settings["auto_drop_chance"], seconds)

async def get_economy_settings(guild_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT daily_min, daily_max, weekly_min, weekly_max,
                   daily_streak_bonus_every, daily_streak_bonus_amount,
                   daily_loot_crate_chance, weekly_daily_boost_chance,
                   weekly_luck_boost_chance, weekly_weekly_boost_chance
            FROM economy_settings
            WHERE guild_id=$1
        """, guild_id)

        if not row:
            await conn.execute("""
                INSERT INTO economy_settings (
                    guild_id, daily_min, daily_max, weekly_min, weekly_max,
                    daily_streak_bonus_every, daily_streak_bonus_amount,
                    daily_loot_crate_chance, weekly_daily_boost_chance,
                    weekly_luck_boost_chance, weekly_weekly_boost_chance
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (guild_id) DO NOTHING
            """, guild_id, DAILY_MIN, DAILY_MAX, WEEKLY_MIN, WEEKLY_MAX,
                 DAILY_STREAK_BONUS_EVERY, DAILY_STREAK_BONUS_AMOUNT,
                 DAILY_LOOT_CRATE_CHANCE, WEEKLY_DAILY_BOOST_CHANCE,
                 WEEKLY_LUCK_BOOST_CHANCE, WEEKLY_WEEKLY_BOOST_CHANCE)

            return {
                "daily_min": DAILY_MIN,
                "daily_max": DAILY_MAX,
                "weekly_min": WEEKLY_MIN,
                "weekly_max": WEEKLY_MAX,
                "daily_streak_bonus_every": DAILY_STREAK_BONUS_EVERY,
                "daily_streak_bonus_amount": DAILY_STREAK_BONUS_AMOUNT,
                "daily_loot_crate_chance": DAILY_LOOT_CRATE_CHANCE,
                "weekly_daily_boost_chance": WEEKLY_DAILY_BOOST_CHANCE,
                "weekly_luck_boost_chance": WEEKLY_LUCK_BOOST_CHANCE,
                "weekly_weekly_boost_chance": WEEKLY_WEEKLY_BOOST_CHANCE
            }

        return dict(row)

async def set_economy_setting_db(guild_id, column, value: int):
    allowed_columns = {
        "daily_min",
        "daily_max",
        "weekly_min",
        "weekly_max",
        "daily_streak_bonus_every",
        "daily_streak_bonus_amount",
        "daily_loot_crate_chance",
        "weekly_daily_boost_chance",
        "weekly_luck_boost_chance",
        "weekly_weekly_boost_chance"
    }

    if column not in allowed_columns:
        raise ValueError("Invalid economy setting.")

    await get_economy_settings(guild_id)

    async with db_pool.acquire() as conn:
        await conn.execute(
            f"UPDATE economy_settings SET {column}=$1 WHERE guild_id=$2",
            value,
            guild_id
        )

async def get_crate_settings(guild_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT regular_crate_min, regular_crate_max,
                   legendary_crate_min, legendary_crate_max,
                   legendary_second_card_chance, claim_loot_crate_chance
            FROM crate_settings
            WHERE guild_id=$1
        """, guild_id)

        if not row:
            await conn.execute("""
                INSERT INTO crate_settings (
                    guild_id, regular_crate_min, regular_crate_max,
                    legendary_crate_min, legendary_crate_max,
                    legendary_second_card_chance, claim_loot_crate_chance
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (guild_id) DO NOTHING
            """, guild_id, REGULAR_CRATE_MIN, REGULAR_CRATE_MAX,
                 LEGENDARY_CRATE_MIN, LEGENDARY_CRATE_MAX,
                 LEGENDARY_SECOND_CARD_CHANCE, CLAIM_LOOT_CRATE_CHANCE)

            return {
                "regular_crate_min": REGULAR_CRATE_MIN,
                "regular_crate_max": REGULAR_CRATE_MAX,
                "legendary_crate_min": LEGENDARY_CRATE_MIN,
                "legendary_crate_max": LEGENDARY_CRATE_MAX,
                "legendary_second_card_chance": LEGENDARY_SECOND_CARD_CHANCE,
                "claim_loot_crate_chance": CLAIM_LOOT_CRATE_CHANCE
            }

        return dict(row)

async def set_crate_setting_db(guild_id, column, value: int):
    allowed_columns = {
        "regular_crate_min",
        "regular_crate_max",
        "legendary_crate_min",
        "legendary_crate_max",
        "legendary_second_card_chance",
        "claim_loot_crate_chance"
    }

    if column not in allowed_columns:
        raise ValueError("Invalid crate setting.")

    await get_crate_settings(guild_id)

    async with db_pool.acquire() as conn:
        await conn.execute(
            f"UPDATE crate_settings SET {column}=$1 WHERE guild_id=$2",
            value,
            guild_id
        )

async def is_staff_member(interaction: discord.Interaction):
    if not interaction.guild or not isinstance(interaction.user, discord.Member):
        return False
    if interaction.user.guild_permissions.administrator:
        return True
    saved_staff_role_id = await get_staff_role(interaction.guild.id)
    if saved_staff_role_id:
        return any(role.id == saved_staff_role_id for role in interaction.user.roles)
    return is_staff(interaction.user)

async def get_staff_ping(interaction: discord.Interaction):
    if not interaction.guild:
        return ""

    saved_staff_role_id = await get_staff_role(interaction.guild.id)

    if saved_staff_role_id:
        return f"<@&{saved_staff_role_id}>"

    return f"<@&{STAFF_ROLE_ID}>"

def create_goos_log_embed_from_values(buyer_id, goos_amount, sancs_cost, claimed_by=None, completed_by=None):
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

    if not channel_id:
        print("No Goos log channel is set for this server.")
        return False

    channel = interaction.guild.get_channel(channel_id)

    if channel is None:
        channel = bot.get_channel(channel_id)

    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as e:
            print(f"Could not fetch Goos log channel {channel_id}: {e}")
            return False

    staff_ping = await get_staff_ping(interaction)

    embed = create_goos_log_embed_from_values(
        buyer_id=interaction.user.id,
        goos_amount=shop_item["goos_amount"],
        sancs_cost=shop_item["price"]
    )

    try:
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
    except Exception as e:
        print(f"Could not send Goos log message to channel {channel_id}: {e}")
        return False

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
    if item.get("boost_type") == "luck":
        return LUCK_BOOST_EMOJI
    if item.get("boost_type") == "daily":
        return DAILY_BOOST_EMOJI
    if item.get("boost_type") == "weekly":
        return WEEKLY_BOOST_EMOJI
    if item.get("name") == "Mafia Immunity":
        return MAFIA_IMMUNITY_EMOJI
    if item.get("name") == "Wheel Bonus Entry":
        return WHEEL_SPIN_EMOJI
    if "title_text" in item or item.get("title_menu"):
        return TITLE_EMOJI
    if item.get("exchange_menu") or "goos_amount" in item:
        return SANC4OOS_EMOJI
    if item.get("profile_emoji_menu"):
        return CUSTOM_EMOJI_SHOP
    if item.get("snipe_item"):
        return SNIPE_EMOJI
    return ""

def get_shop_item_image(item_key):
    if item_key == "lootcrate":
        return LOOT_CRATE_IMAGE_URL
    if item_key == "legendarycrate":
        return LEGENDARY_CRATE_IMAGE_URL
    if item_key == "mafiaimmunity":
        return MAFIA_IMMUNITY_IMAGE_URL
    if item_key == "dailyboost":
        return DAILY_BOOST_IMAGE_URL
    if item_key == "weeklyboost":
        return WEEKLY_BOOST_IMAGE_URL
    if item_key == "luckboost":
        return LUCK_BOOST_IMAGE_URL
    if item_key == "wheelentry":
        return WHEEL_SPIN_IMAGE_URL
    if item_key == "title":
        return TITLE_IMAGE_URL
    if item_key == "goosexchange" or item_key.startswith("goos"):
        return SANC4OOS_IMAGE_URL
    if item_key == "profileemoji":
        return CUSTOM_EMOJI_IMAGE_URL
    return ""

def create_shop_embed():
    categories = ["Crates", "Boosts", "Game Items", "Cosmetics", "Exchange"]
    text = ""

    for category in categories:
        items = [
            (key, item)
            for key, item in SHOP_ITEMS.items()
            if item.get("category") == category and item.get("category") != "Hidden"
        ]

        if not items:
            continue

        text += f"**{category}**\n"

        for key, item in items:
            emoji = get_shop_item_emoji(item)
            emoji_text = f"{emoji} " if emoji else ""
            if item.get("price", 0) > 0:
                price_text = f" [{format_coins(item['price'])}]"
            else:
                price_text = ""
            text += f"{BULLET_EMOJI} {emoji_text}`{item['name']}`{price_text}\n"

    embed = discord.Embed(
        title="Shop",
        description=text or "The shop is currently empty.",
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_thumbnail(url=SHOP_ICON_URL)
    embed.set_footer(text="Choose an item below to view details.")

    return embed

def create_shop_item_embed(item_key):
    item = SHOP_ITEMS[item_key]
    emoji = get_shop_item_emoji(item)
    image_url = get_shop_item_image(item_key)

    if item.get("exchange_menu"):
        details = "**Exchange Options:**\n"
        details += f"{BULLET_EMOJI} 100 Goos [{format_coins(SHOP_ITEMS['goos100']['price'])}]\n"
        details += f"{BULLET_EMOJI} 250 Goos [{format_coins(SHOP_ITEMS['goos250']['price'])}]\n"
        details += f"{BULLET_EMOJI} 500 Goos [{format_coins(SHOP_ITEMS['goos500']['price'])}]\n"
        details += f"{BULLET_EMOJI} Staff must fulfill Goos manually\n"
        details += "Choose an amount from the dropdown below."
    else:
        details = f"**Price:** [{format_coins(item['price'])}]\n"
        details += f"**Info:** {item['description']}\n\n"

        if item.get("crate_type") == "regular":
            details += (
                "**Contains:**\n"
                f"{BULLET_EMOJI} {format_coins(REGULAR_CRATE_MIN)} to {REGULAR_CRATE_MAX:,}\n"
                f"{BULLET_EMOJI} 1 random card\n"
            )
        elif item.get("crate_type") == "legendary":
            details += (
                "**Contains:**\n"
                f"{BULLET_EMOJI} {format_coins(LEGENDARY_CRATE_MIN)} to {LEGENDARY_CRATE_MAX:,}\n"
                f"{BULLET_EMOJI} Higher rarity card odds\n"
                f"{BULLET_EMOJI} {LEGENDARY_SECOND_CARD_CHANCE}% chance for a bonus card\n"
            )
        elif item.get("boost_type") == "luck":
            details += (
                "**Effect:**\n"
                f"{BULLET_EMOJI} Lasts 1 hour\n"
                f"{BULLET_EMOJI} Improves crate rarity odds while active\n"
            )
        elif item.get("boost_type") == "daily":
            details += (
                "**Effect:**\n"
                f"{BULLET_EMOJI} Adds {DAILY_BOOST_PERCENT}% to your next daily claim\n"
                f"{BULLET_EMOJI} Used automatically the next time you claim /daily\n"
            )
        elif item.get("boost_type") == "weekly":
            details += (
                "**Effect:**\n"
                f"{BULLET_EMOJI} Adds {WEEKLY_BOOST_PERCENT}% to your next weekly claim\n"
                f"{BULLET_EMOJI} Used automatically the next time you claim /weekly\n"
            )
        elif item.get("title_menu"):
            details += (
                "**How it works:**\n"
                f"{BULLET_EMOJI} Buy preset titles from `/buy`\n"
                f"{BULLET_EMOJI} Use `/equiptitle` to change your active title\n"
                f"{BULLET_EMOJI} Equipped titles show after your name in /leaderboard and /inventory\n"
            )
        elif "title_text" in item:
            details += (
                "**Title:**\n"
                f"{BULLET_EMOJI} {item['title_text']}\n"
                f"{BULLET_EMOJI} Shows in /inventory and /leaderboard\n"
            )
        elif item.get("profile_emoji_menu"):
            details += (
                "**How it works:**\n"
                f"{BULLET_EMOJI} Buy preset profile emojis from `/buy`\n"
                f"{BULLET_EMOJI} Use `/equipemoji` to change your active emoji\n"
                f"{BULLET_EMOJI} Equipped emojis show after your name in /leaderboard and /inventory\n"
            )
        elif item.get("snipe_item"):
            details += (
                "**How it works:**\n"
                f"{BULLET_EMOJI} Buy this item to receive 1 Sniper\n"
                f"{BULLET_EMOJI} Use `/snipe` to target another user\n"
                f"{BULLET_EMOJI} The target hides in a bush, then you guess where they hid\n"
                f"{BULLET_EMOJI} If your shot hits, they are muted for {SNIPE_MUTE_MINUTES} minutes\n"
                f"{BULLET_EMOJI} Snipers are consumable and disappear after use\n"
            )
        elif item.get("manual_item"):
            details += (
                "**How it works:**\n"
                f"{BULLET_EMOJI} This purchase is logged for staff\n"
                f"{BULLET_EMOJI} Staff will manually apply or confirm this reward\n"
            )
        elif "goos_amount" in item:
            details += (
                "**Exchange:**\n"
                f"{BULLET_EMOJI} Requests {item['goos_amount']} Goos\n"
                f"{BULLET_EMOJI} Staff must fulfill this manually\n"
            )

        details += f"Use `/buy` and choose `{item['name']}` to purchase."

    embed_title = f"{emoji} {item['name']}" if emoji else item["name"]

    embed = discord.Embed(
        title=embed_title,
        description=details,
        color=discord.Color.from_str("#9e659d")
    )

    if image_url:
        embed.set_thumbnail(url=image_url)

    embed.set_footer(text="Use the button below to return to the full shop list.")

    return embed

async def create_title_shop_embed():
    rows = await get_active_shop_titles()

    if not rows:
        details = "No titles are available right now."
    else:
        grouped = {}

        for row in rows:
            grouped.setdefault(row["price"], []).append(row)

        lines = []

        for price in sorted(grouped.keys()):
            lines.append(f"{format_coins(price)}")

            for row in grouped[price]:
                lines.append(f"{row['title']}")

            lines.append("")

        details = "```text\n" + "\n".join(lines).strip() + "\n```"
        details += "\nUse `/buy` and choose `Special Title` to purchase."

    embed = discord.Embed(
        title=f"{TITLE_EMOJI} Title Shop",
        description=details,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_thumbnail(url=TITLE_IMAGE_URL)

    return embed

async def create_profile_emoji_shop_embed():
    rows = await get_active_profile_emojis()

    if not rows:
        details = "No profile emojis are available right now."
    else:
        grouped = {}

        for row in rows:
            grouped.setdefault(row["price"], []).append(row)

        lines = []

        for price in sorted(grouped.keys()):
            lines.append(f"{CURRENCY_EMOJI} **{price:,}**")

            emojis = [row["emoji"] for row in grouped[price]]

            for index in range(0, len(emojis), 2):
                pair = "      ".join(emojis[index:index + 2])
                lines.append(pair)

            lines.append("")

        details = "\n".join(lines).strip()
        details += "\n\nUse `/buy` and choose `Profile Emoji` to purchase."

    embed = discord.Embed(
        title="Profile Emoji Shop",
        description=details,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_thumbnail(url=CUSTOM_EMOJI_IMAGE_URL)

    return embed

def card_label(card):
    return f"**ID:** `{card['id']}` {card['name']} ({card['rarity']})"

def format_card_line(card, amount=None, limited_note=""):
    amount_text = f" x{amount}" if amount is not None else ""
    return f"**ID:** `{card['id']}` {card['name']} ({card['rarity']}){amount_text}{limited_note}"

def clean_card_ref(card_ref: str):
    return card_ref.strip().replace("#", "").replace("ID", "").replace("id", "").strip()

def create_card_embed(card):
    embed = discord.Embed(
        title=f"{card['rarity']} Card Drop!",
        description=f"**{card['name']}** appeared!\n**ID:** `{card['id']}`",
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

async def get_daily_limit_row(user_id, action_name):
    today = eastern_day_number()

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT count_value, amount_value FROM user_daily_limits WHERE user_id=$1 AND action_name=$2 AND day_number=$3",
            user_id,
            action_name,
            today
        )

        if not row:
            await conn.execute("""
                INSERT INTO user_daily_limits (user_id, action_name, day_number, count_value, amount_value)
                VALUES ($1, $2, $3, 0, 0)
                ON CONFLICT DO NOTHING
            """, user_id, action_name, today)

            return {"count_value": 0, "amount_value": 0}

        return {
            "count_value": int(row["count_value"]),
            "amount_value": int(row["amount_value"])
        }

async def add_daily_limit_usage(user_id, action_name, count_add=0, amount_add=0):
    today = eastern_day_number()

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_daily_limits (user_id, action_name, day_number, count_value, amount_value)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id, action_name, day_number)
            DO UPDATE SET
                count_value = user_daily_limits.count_value + $4,
                amount_value = user_daily_limits.amount_value + $5
        """, user_id, action_name, today, count_add, amount_add)

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

async def clear_boost(user_id, boost_type):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM user_boosts WHERE user_id=$1 AND boost_type=$2",
            user_id,
            boost_type
        )

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

async def set_user_custom_emoji(user_id, emoji):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_custom_emojis (user_id, emoji)
            VALUES ($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET emoji=$2
        """, user_id, emoji)

async def get_user_custom_emoji(user_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT emoji FROM user_custom_emojis WHERE user_id=$1",
            user_id
        )

async def add_profile_emoji_to_shop(name, emoji, price):
    async with db_pool.acquire() as conn:
        return await conn.fetchval("""
            INSERT INTO profile_emojis (name, emoji, price, is_active)
            VALUES ($1, $2, $3, TRUE)
            ON CONFLICT (name)
            DO UPDATE SET emoji=$2, price=$3, is_active=TRUE
            RETURNING id
        """, name, emoji, price)

async def remove_profile_emoji_from_shop(name):
    async with db_pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE profile_emojis SET is_active=FALSE WHERE LOWER(name)=LOWER($1)",
            name
        )
        return result.endswith("1")

async def get_active_profile_emojis():
    async with db_pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM profile_emojis WHERE is_active=TRUE ORDER BY price, name"
        )

async def get_profile_emoji_by_id(profile_emoji_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM profile_emojis WHERE id=$1 AND is_active=TRUE",
            profile_emoji_id
        )

async def user_owns_profile_emoji(user_id, profile_emoji_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT 1 FROM user_owned_profile_emojis WHERE user_id=$1 AND profile_emoji_id=$2",
            user_id,
            profile_emoji_id
        )

async def add_profile_emoji_to_user(user_id, profile_emoji_id):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_owned_profile_emojis (user_id, profile_emoji_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
        """, user_id, profile_emoji_id)

async def get_user_owned_profile_emojis(user_id):
    async with db_pool.acquire() as conn:
        return await conn.fetch("""
            SELECT profile_emojis.id, profile_emojis.name, profile_emojis.emoji, profile_emojis.price
            FROM user_owned_profile_emojis
            JOIN profile_emojis ON profile_emojis.id = user_owned_profile_emojis.profile_emoji_id
            WHERE user_owned_profile_emojis.user_id=$1
            AND profile_emojis.is_active=TRUE
            ORDER BY profile_emojis.price, profile_emojis.name
        """, user_id)

async def add_owned_title(user_id, title):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_owned_titles (user_id, title)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
        """, user_id, title)

async def get_user_owned_titles(user_id):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT title FROM user_owned_titles WHERE user_id=$1 ORDER BY title",
            user_id
        )
        return [row["title"] for row in rows]

async def add_title_to_shop(title, price):
    async with db_pool.acquire() as conn:
        return await conn.fetchval("""
            INSERT INTO shop_titles (title, price, is_active)
            VALUES ($1, $2, TRUE)
            ON CONFLICT (title)
            DO UPDATE SET price=$2, is_active=TRUE
            RETURNING id
        """, title, price)

async def remove_title_from_shop(title):
    async with db_pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE shop_titles SET is_active=FALSE WHERE LOWER(title)=LOWER($1)",
            title
        )
        return result.endswith("1")

async def get_active_shop_titles():
    async with db_pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM shop_titles WHERE is_active=TRUE ORDER BY price, title"
        )

async def get_shop_title_by_id(title_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM shop_titles WHERE id=$1 AND is_active=TRUE",
            title_id
        )

async def user_owns_title(user_id, title):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT 1 FROM user_owned_titles WHERE user_id=$1 AND title=$2",
            user_id,
            title
        )

async def create_custom_emoji_request(user_id, emoji, price):
    async with db_pool.acquire() as conn:
        return await conn.fetchval("""
            INSERT INTO custom_emoji_requests (user_id, emoji, price)
            VALUES ($1, $2, $3)
            RETURNING id
        """, user_id, emoji, price)

async def approve_custom_emoji_request(request_id, staff_id):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT user_id, emoji, status FROM custom_emoji_requests WHERE id=$1 FOR UPDATE",
                request_id
            )

            if not row:
                return False, "That custom emoji request was not found.", None

            if row["status"] != "pending":
                return False, "That custom emoji request has already been reviewed.", None

            await conn.execute("""
                UPDATE custom_emoji_requests
                SET status='approved', reviewed_by=$1, reviewed_at=CURRENT_TIMESTAMP
                WHERE id=$2
            """, staff_id, request_id)

            await conn.execute("""
                INSERT INTO user_custom_emojis (user_id, emoji)
                VALUES ($1, $2)
                ON CONFLICT (user_id)
                DO UPDATE SET emoji=$2
            """, row["user_id"], row["emoji"])

            return True, "Custom emoji approved.", row

async def deny_custom_emoji_request(request_id, staff_id, reason="No reason provided."):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT user_id, emoji, price, status FROM custom_emoji_requests WHERE id=$1 FOR UPDATE",
                request_id
            )

            if not row:
                return False, "That custom emoji request was not found.", None

            if row["status"] != "pending":
                return False, "That custom emoji request has already been reviewed.", None

            await conn.execute("""
                UPDATE custom_emoji_requests
                SET status='denied', reviewed_by=$1, reviewed_at=CURRENT_TIMESTAMP, reason=$2
                WHERE id=$3
            """, staff_id, reason, request_id)

            await conn.execute("""
                INSERT INTO balances (user_id, balance)
                VALUES ($1, $2)
                ON CONFLICT (user_id)
                DO UPDATE SET balance = balances.balance + $2
            """, row["user_id"], row["price"])

            return True, "Custom emoji denied and refunded.", row

async def create_goos_request(user_id, goos_amount, cost):
    async with db_pool.acquire() as conn:
        return await conn.fetchval("""
            INSERT INTO goos_exchange_requests (user_id, goos_amount, sancs_cost)
            VALUES ($1, $2, $3)
            RETURNING id
        """, user_id, goos_amount, cost)

async def claim_goos_request(request_id, staff_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT status, claimed_by FROM goos_exchange_requests WHERE id=$1",
            request_id
        )

        if not row:
            return False, "That request was not found."

        if row["status"] == "completed":
            return False, "That request is already completed."

        if row["claimed_by"]:
            return False, "That request has already been claimed."

        await conn.execute("""
            UPDATE goos_exchange_requests
            SET status='claimed', claimed_by=$1, claimed_at=CURRENT_TIMESTAMP
            WHERE id=$2
        """, staff_id, request_id)

        return True, "Request claimed."

async def complete_goos_request(request_id, staff_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT status FROM goos_exchange_requests WHERE id=$1",
            request_id
        )

        if not row:
            return False, "That request was not found."

        if row["status"] == "completed":
            return False, "That request is already completed."

        await conn.execute("""
            UPDATE goos_exchange_requests
            SET status='completed', completed_by=$1, completed_at=CURRENT_TIMESTAMP
            WHERE id=$2
        """, staff_id, request_id)

        return True, "Request completed."

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

async def get_snipe_items(user_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT regular_count, legendary_count FROM snipe_items WHERE user_id=$1",
            user_id
        )

        if not row:
            await conn.execute(
                "INSERT INTO snipe_items (user_id, regular_count, legendary_count) VALUES ($1, 0, 0) ON CONFLICT (user_id) DO NOTHING",
                user_id
            )
            return 0, 0

        return row["regular_count"], row["legendary_count"]

async def add_snipe_item(user_id, snipe_type="regular", amount=1):
    column = "legendary_count" if snipe_type == "legendary" else "regular_count"

    async with db_pool.acquire() as conn:
        await conn.execute(f"""
            INSERT INTO snipe_items (user_id, {column})
            VALUES ($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET {column} = snipe_items.{column} + $2
        """, user_id, amount)

async def remove_snipe_item(user_id, snipe_type="regular"):
    column = "legendary_count" if snipe_type == "legendary" else "regular_count"

    async with db_pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchval(
                f"SELECT {column} FROM snipe_items WHERE user_id=$1 FOR UPDATE",
                user_id
            )

            if count is None:
                await conn.execute(
                    "INSERT INTO snipe_items (user_id, regular_count, legendary_count) VALUES ($1, 0, 0) ON CONFLICT (user_id) DO NOTHING",
                    user_id
                )
                return False

            if count <= 0:
                return False

            await conn.execute(
                f"UPDATE snipe_items SET {column} = {column} - 1 WHERE user_id=$1",
                user_id
            )

            return True

async def get_staff_snipe_enabled(guild_id):
    async with db_pool.acquire() as conn:
        value = await conn.fetchval(
            "SELECT staff_snipe_enabled FROM snipe_settings WHERE guild_id=$1",
            guild_id
        )

        if value is None:
            await conn.execute(
                "INSERT INTO snipe_settings (guild_id, staff_snipe_enabled) VALUES ($1, TRUE) ON CONFLICT (guild_id) DO NOTHING",
                guild_id
            )
            return True

        return value

async def set_staff_snipe_enabled(guild_id, enabled: bool):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO snipe_settings (guild_id, staff_snipe_enabled)
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET staff_snipe_enabled = EXCLUDED.staff_snipe_enabled
        """, guild_id, enabled)

async def get_snipe_settings(guild_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT staff_snipe_enabled, snipe_cooldown_seconds, snipe_mute_minutes FROM snipe_settings WHERE guild_id=$1",
            guild_id
        )

        if not row:
            await conn.execute("""
                INSERT INTO snipe_settings (guild_id, staff_snipe_enabled, snipe_cooldown_seconds, snipe_mute_minutes)
                VALUES ($1, TRUE, $2, $3)
                ON CONFLICT (guild_id) DO NOTHING
            """, guild_id, SNIPE_COOLDOWN, SNIPE_MUTE_MINUTES)

            return {
                "staff_snipe_enabled": True,
                "snipe_cooldown_seconds": SNIPE_COOLDOWN,
                "snipe_mute_minutes": SNIPE_MUTE_MINUTES
            }

        return {
            "staff_snipe_enabled": row["staff_snipe_enabled"],
            "snipe_cooldown_seconds": row["snipe_cooldown_seconds"] or SNIPE_COOLDOWN,
            "snipe_mute_minutes": row["snipe_mute_minutes"] or SNIPE_MUTE_MINUTES
        }

async def set_staff_snipe_enabled(guild_id, enabled: bool):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO snipe_settings (guild_id, staff_snipe_enabled, snipe_cooldown_seconds, snipe_mute_minutes)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (guild_id)
            DO UPDATE SET staff_snipe_enabled = EXCLUDED.staff_snipe_enabled
        """, guild_id, enabled, SNIPE_COOLDOWN, SNIPE_MUTE_MINUTES)

async def set_snipe_cooldown_db(guild_id, minutes: int):
    seconds = minutes * 60

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO snipe_settings (guild_id, staff_snipe_enabled, snipe_cooldown_seconds, snipe_mute_minutes)
            VALUES ($1, TRUE, $2, $3)
            ON CONFLICT (guild_id)
            DO UPDATE SET snipe_cooldown_seconds = EXCLUDED.snipe_cooldown_seconds
        """, guild_id, seconds, SNIPE_MUTE_MINUTES)

async def set_snipe_mute_minutes_db(guild_id, minutes: int):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO snipe_settings (guild_id, staff_snipe_enabled, snipe_cooldown_seconds, snipe_mute_minutes)
            VALUES ($1, TRUE, $2, $3)
            ON CONFLICT (guild_id)
            DO UPDATE SET snipe_mute_minutes = EXCLUDED.snipe_mute_minutes
        """, guild_id, SNIPE_COOLDOWN, minutes)

async def get_staff_snipe_enabled(guild_id):
    settings = await get_snipe_settings(guild_id)
    return settings["staff_snipe_enabled"]

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
        if key != "goosexchange"
        and (current.lower() in item["name"].lower() or current.lower() in key.lower())
    ][:25]

async def owned_profile_emoji_autocomplete(interaction: discord.Interaction, current: str):
    rows = await get_user_owned_profile_emojis(interaction.user.id)

    return [
        app_commands.Choice(name=f"{row['emoji']} {row['name']}", value=str(row["id"]))
        for row in rows
        if current.lower() in row["name"].lower() or current.lower() in row["emoji"].lower()
    ][:25]

async def owned_title_autocomplete(interaction: discord.Interaction, current: str):
    titles = await get_user_owned_titles(interaction.user.id)

    return [
        app_commands.Choice(name=title, value=title)
        for title in titles
        if current.lower() in title.lower()
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

@tasks.loop(minutes=1)
async def auto_drop():
    now = int(time.time())

    for guild in bot.guilds:
        settings = await get_drop_settings(guild.id)

        if not settings["auto_drop_enabled"]:
            continue

        interval_seconds = int(settings["auto_drop_minutes"]) * 60
        last_drop = last_auto_drop_times.get(guild.id, 0)

        if now - last_drop < interval_seconds:
            continue

        last_auto_drop_times[guild.id] = now

        if random.randint(1, 100) > int(settings["auto_drop_chance"]):
            continue

        saved_channel_ids = await get_drop_channels_db(guild.id)
        possible_channel_ids = saved_channel_ids or DROP_CHANNEL_IDS

        if not possible_channel_ids:
            continue

        available_channels = []

        for channel_id in possible_channel_ids:
            channel = guild.get_channel(channel_id) or bot.get_channel(channel_id)

            if channel:
                available_channels.append(channel)

        if not available_channels:
            continue

        channel = random.choice(available_channels)
        card = await choose_random_card()

        if not card:
            continue

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
        claim_cooldown = CLAIM_COOLDOWN

        if interaction.guild:
            drop_settings = await get_drop_settings(interaction.guild.id)
            claim_cooldown = int(drop_settings["claim_cooldown_seconds"])

        if uid in last_claim_times:
            if now - last_claim_times[uid] < claim_cooldown:
                remaining = int(claim_cooldown - (now - last_claim_times[uid]))
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
        claim_crate_chance = CLAIM_LOOT_CRATE_CHANCE

        if interaction.guild:
            crate_settings = await get_crate_settings(interaction.guild.id)
            claim_crate_chance = int(crate_settings["claim_loot_crate_chance"])

        found_crate = random.randint(1, 100) <= claim_crate_chance
        if found_crate:
            await add_loot_crate(uid, "regular", 1)
        content = f"{interaction.user.mention} claimed **{self.card['name']}**! **ID:** `{self.card['id']}`"
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
        await add_daily_limit_usage(self.requester.id, "trade", count_add=1)
        await add_daily_limit_usage(self.target.id, "trade", count_add=1)

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
                f"**{self.card['name']}** **ID:** `{self.card['id']}` has been removed from future drops and card lists.\n"
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

# ---------------- SNIPE GAME ----------------

def get_bush_emoji(bush_number):
    return {
        1: BUSH_1_EMOJI,
        2: BUSH_2_EMOJI,
        3: BUSH_3_EMOJI,
    }.get(bush_number, BUSH_1_EMOJI)

class SnipeGameView(discord.ui.View):
    def __init__(self, sniper, target, snipe_type="regular", mute_minutes=SNIPE_MUTE_MINUTES):
        super().__init__(timeout=120)
        self.sniper = sniper
        self.target = target
        self.snipe_type = snipe_type
        self.mute_minutes = mute_minutes
        self.bush_count = 3 if snipe_type == "legendary" else 5
        self.phase = "hide"
        self.hidden_bush = None
        self.guessed_bush = None
        self.finished = False

        for bush_number in range(1, self.bush_count + 1):
            self.add_item(SnipeGameButton(bush_number))

    async def on_timeout(self):
        self.finished = True

        for child in self.children:
            child.disabled = True

    async def handle_choice(self, interaction: discord.Interaction, bush_number: int):
        if self.finished:
            return await interaction.response.send_message("This snipe is already finished.", ephemeral=True)

        if self.phase == "hide":
            if interaction.user.id != self.target.id:
                return await interaction.response.send_message(
                    "Only the target can choose where to hide.",
                    ephemeral=True
                )

            self.hidden_bush = bush_number
            self.phase = "guess"

            await interaction.response.edit_message(
                content=(
                    f"{SNIPE_EMOJI} | {self.target.mention} has hidden.\n"
                    f"{self.sniper.mention}, take your shot."
                ),
                view=self
            )
            return

        if self.phase == "guess":
            if interaction.user.id != self.sniper.id:
                return await interaction.response.send_message(
                    "Only the sniper can take the shot.",
                    ephemeral=True
                )

            self.guessed_bush = bush_number
            self.finished = True

            for child in self.children:
                child.disabled = True

            removed = await remove_snipe_item(self.sniper.id, self.snipe_type)

            if not removed:
                return await interaction.response.edit_message(
                    content=(
                        f"{SNIPE_MISS_EMOJI} | {self.sniper.mention} no longer has a Sniper. "
                        f"The snipe was cancelled."
                    ),
                    view=self
                )

            await set_cooldown(self.sniper.id, "snipe")

            if self.guessed_bush == self.hidden_bush:
                timeout_until = discord.utils.utcnow() + timedelta(minutes=self.mute_minutes)
                mute_text = random.choice(SNIPE_SUCCESS_MESSAGES).format(
                    target=self.target.mention,
                    sniper=self.sniper.mention
                )
                mute_text += f" Muted for {self.mute_minutes} minutes."

                try:
                    await self.target.timeout(timeout_until, reason=f"Snipe hit by {self.sniper}")
                except Exception:
                    mute_text = random.choice(OWNER_PROTECTION_MESSAGES).format(
                        target=self.target.mention,
                        sniper=self.sniper.mention
                    )

                return await interaction.response.edit_message(
                    content=(
                        f"{SNIPE_HIT_EMOJI} **SHOT HIT!**\n"
                        f"{mute_text}"
                    ),
                    view=self
                )

            miss_text = random.choice(SNIPE_MISS_MESSAGES).format(
                target=self.target.mention,
                sniper=self.sniper.mention
            )

            return await interaction.response.edit_message(
                content=(
                    f"{SNIPE_MISS_EMOJI} **SHOT MISSED!**\n"
                    f"{miss_text}"
                ),
                view=self
            )

class SnipeGameButton(discord.ui.Button):
    def __init__(self, bush_number):
        super().__init__(
            label=f"Bush {bush_number}",
            emoji=discord.PartialEmoji.from_str(get_bush_emoji(bush_number)),
            style=discord.ButtonStyle.secondary
        )
        self.bush_number = bush_number

    async def callback(self, interaction: discord.Interaction):
        await self.view.handle_choice(interaction, self.bush_number)

# ---------------- CUSTOM EMOJI REQUEST STAFF VIEW ----------------

class CustomEmojiRequestView(discord.ui.View):
    def __init__(self, request_id, buyer_id, emoji, price):
        super().__init__(timeout=None)
        self.request_id = request_id
        self.buyer_id = buyer_id
        self.emoji = emoji
        self.price = price

    def build_embed(self, status="Pending", reviewed_by=None, reason=None):
        description = (
            f"**User:** <@{self.buyer_id}>\n"
            f"**Requested Emoji:** {self.emoji}\n"
            f"**Cost:** {format_coins(self.price)}\n"
            f"**Status:** {status}"
        )

        if reviewed_by:
            description += f"\n**Reviewed by:** <@{reviewed_by}>"

        if reason:
            description += f"\n**Reason:** {reason}"

        embed = discord.Embed(
            title="Custom Name Emoji Request",
            description=description,
            color=discord.Color.from_str("#9e659d")
        )
        embed.set_footer(text="Approve to add this emoji to the user's leaderboard and inventory display.")

        return embed

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve_request(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await is_staff_member(interaction):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        success, message, row = await approve_custom_emoji_request(self.request_id, interaction.user.id)

        if not success:
            return await interaction.response.send_message(message, ephemeral=True)

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            embed=self.build_embed("Approved", reviewed_by=interaction.user.id),
            view=self
        )

        try:
            user = await bot.fetch_user(self.buyer_id)
            await user.send(f"Your custom name emoji was approved: {self.emoji}")
        except Exception:
            pass

    @discord.ui.button(label="Deny + Refund", style=discord.ButtonStyle.danger)
    async def deny_request(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await is_staff_member(interaction):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        reason = "Denied by staff."
        success, message, row = await deny_custom_emoji_request(self.request_id, interaction.user.id, reason)

        if not success:
            return await interaction.response.send_message(message, ephemeral=True)

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            embed=self.build_embed("Denied and Refunded", reviewed_by=interaction.user.id, reason=reason),
            view=self
        )

        try:
            user = await bot.fetch_user(self.buyer_id)
            await user.send(f"Your custom name emoji request was denied and refunded. Reason: {reason}")
        except Exception:
            pass

async def send_custom_emoji_log(interaction: discord.Interaction, request_id, emoji, price):
    if not interaction.guild:
        return False

    if not channel_id:
        print("No staff log channel is set for custom emoji requests.")
        return False

    channel = interaction.guild.get_channel(channel_id) or bot.get_channel(channel_id)

    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as e:
            print(f"Could not fetch staff log channel {channel_id}: {e}")
            return False

    staff_ping = await get_staff_ping(interaction)

    view = CustomEmojiRequestView(
        request_id=request_id,
        buyer_id=interaction.user.id,
        emoji=emoji,
        price=price
    )

    try:
        await channel.send(
            content=staff_ping,
            embed=view.build_embed(),
            view=view,
            allowed_mentions=discord.AllowedMentions(roles=True, users=True)
        )
        return True
    except Exception as e:
        print(f"Could not send custom emoji request to channel {channel_id}: {e}")
        return False

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
            discord.SelectOption(label="100 Goos", value="goos100", description="7,500 Sancs"),
            discord.SelectOption(label="250 Goos", value="goos250", description="18,000 Sancs"),
            discord.SelectOption(label="500 Goos", value="goos500", description="35,000 Sancs"),
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
            f"Requested: **{shop_item['goos_amount']} Goos**\n"
            f"Cost: **{format_coins(shop_item['price'])}**\n"
            f"A staff member will need to fulfill this manually. Please open a ticket and include your request ID.",
            ephemeral=True
        )

        log_sent = await send_goos_log(interaction, request_id, shop_item)

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
        elif item_key == "profileemoji":
            await interaction.response.edit_message(embed=await create_profile_emoji_shop_embed(), view=BackToShopView())
        elif item_key == "title":
            await interaction.response.edit_message(embed=await create_title_shop_embed(), view=BackToShopView())
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

# ---------------- COSMETIC BUY VIEWS ----------------

class ProfileEmojiBuySelect(discord.ui.Select):
    def __init__(self, rows):
        options = [
            discord.SelectOption(
                label=f"{row['name']} - {row['price']:,} Sancs",
                value=str(row["id"]),
                emoji=discord.PartialEmoji.from_str(row["emoji"])
            )
            for row in rows[:25]
        ]

        super().__init__(
            placeholder="Choose a profile emoji to buy...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        profile_emoji_id = int(self.values[0])
        profile_emoji = await get_profile_emoji_by_id(profile_emoji_id)

        if not profile_emoji:
            return await interaction.response.send_message("That profile emoji does not exist anymore.", ephemeral=True)

        if await user_owns_profile_emoji(interaction.user.id, profile_emoji_id):
            return await interaction.response.send_message(
                f"You already own **{profile_emoji['name']}** {profile_emoji['emoji']}. Use `/equipemoji` to equip it.",
                ephemeral=True
            )

        success = await subtract_balance(interaction.user.id, profile_emoji["price"])

        if not success:
            return await interaction.response.send_message(
                f"You do not have enough currency. This costs **{format_coins(profile_emoji['price'])}**.",
                ephemeral=True
            )

        await add_profile_emoji_to_user(interaction.user.id, profile_emoji_id)
        await set_user_custom_emoji(interaction.user.id, profile_emoji["emoji"])

        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO purchases (user_id, item_key, item_name, price)
                VALUES ($1, $2, $3, $4)
            """, interaction.user.id, f"profileemoji:{profile_emoji_id}", profile_emoji["name"], profile_emoji["price"])

        await interaction.response.send_message(
            f"{interaction.user.mention} bought and equipped **{profile_emoji['name']}** {profile_emoji['emoji']} for **{format_coins(profile_emoji['price'])}**!"
        )

class ProfileEmojiBuyView(discord.ui.View):
    def __init__(self, rows):
        super().__init__(timeout=180)
        self.add_item(ProfileEmojiBuySelect(rows))

class TitleBuySelect(discord.ui.Select):
    def __init__(self, rows):
        options = [
            discord.SelectOption(
                label=f"{row['title']} - {row['price']:,} Sancs",
                value=str(row["id"])
            )
            for row in rows[:25]
        ]

        super().__init__(
            placeholder="Choose a title to buy...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        title_id = int(self.values[0])
        shop_title = await get_shop_title_by_id(title_id)

        if not shop_title:
            return await interaction.response.send_message("That title does not exist anymore.", ephemeral=True)

        if await user_owns_title(interaction.user.id, shop_title["title"]):
            return await interaction.response.send_message(
                f"You already own **{shop_title['title']}**. Use `/equiptitle` to equip it.",
                ephemeral=True
            )

        success = await subtract_balance(interaction.user.id, shop_title["price"])

        if not success:
            return await interaction.response.send_message(
                f"You do not have enough currency. This costs **{format_coins(shop_title['price'])}**.",
                ephemeral=True
            )

        await add_owned_title(interaction.user.id, shop_title["title"])
        await set_title(interaction.user.id, shop_title["title"])

        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO purchases (user_id, item_key, item_name, price)
                VALUES ($1, $2, $3, $4)
            """, interaction.user.id, f"title:{title_id}", shop_title["title"], shop_title["price"])

        await interaction.response.send_message(
            f"{interaction.user.mention} bought and equipped the title **{shop_title['title']}** for **{format_coins(shop_title['price'])}**!"
        )

class TitleBuyView(discord.ui.View):
    def __init__(self, rows):
        super().__init__(timeout=180)
        self.add_item(TitleBuySelect(rows))

# ---------------- SANCTION SETTINGS UI ----------------

def format_on_off(value: bool):
    return TOGGLE_ON_EMOJI if value else TOGGLE_OFF_EMOJI

async def create_settings_home_embed(guild_id):
    settings = await get_snipe_settings(guild_id)

    description = (
        f"{format_on_off(settings['staff_snipe_enabled'])} **Snipe Settings**\n"
        f"{TOGGLE_ON_EMOJI} **Card Drop Settings**\n"
        f"{TOGGLE_ON_EMOJI} **Economy Settings**\n"
        f"{TOGGLE_ON_EMOJI} **Crate Settings**\n"
        f"{TOGGLE_ON_EMOJI} **Cosmetic Settings**\n"
        f"{TOGGLE_ON_EMOJI} **Staff Settings**"
    )

    embed = discord.Embed(
        title="Sanction Settings",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_footer(text="Choose a settings category below.")

    return embed

async def create_snipe_settings_embed(guild_id):
    settings = await get_snipe_settings(guild_id)

    cooldown_minutes = int(settings["snipe_cooldown_seconds"] // 60)
    mute_minutes = int(settings["snipe_mute_minutes"])

    description = (
        f"{format_on_off(settings['staff_snipe_enabled'])} **Staff Sniping**\n"
        f"{TOGGLE_ON_EMOJI} **Snipe Cooldown:** {cooldown_minutes} minutes\n"
        f"{TOGGLE_ON_EMOJI} **Snipe Mute Time:** {mute_minutes} minutes\n"
        f"{TOGGLE_ON_EMOJI} **Regular Sniper Bushes:** 5\n"
        f"{TOGGLE_ON_EMOJI} **Legendary Sniper Bushes:** 3"
    )

    embed = discord.Embed(
        title="Sanction Settings — Snipe",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_footer(text="Use the dropdown below to edit snipe settings.")

    return embed

async def create_drop_settings_embed(guild_id):
    settings = await get_drop_settings(guild_id)
    channels = await get_drop_channels_db(guild_id)
    channel_text = "None set"

    if channels:
        channel_text = "\n".join([f"<#{channel_id}>" for channel_id in channels])

    description = (
        f"{format_on_off(settings['auto_drop_enabled'])} **Auto Drops**\n"
        f"{TOGGLE_ON_EMOJI} **Auto Drop Interval:** {int(settings['auto_drop_minutes'])} minutes\n"
        f"{TOGGLE_ON_EMOJI} **Auto Drop Chance:** {int(settings['auto_drop_chance'])}%\n"
        f"{TOGGLE_ON_EMOJI} **Claim Cooldown:** {int(settings['claim_cooldown_seconds'])} seconds\n"
        f"\n**Drop Channels**\n{channel_text}"
    )

    embed = discord.Embed(
        title="Sanction Settings — Card Drops",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_footer(text="Use the dropdown below to edit card drop settings.")

    return embed

async def create_economy_settings_embed(guild_id):
    settings = await get_economy_settings(guild_id)

    description = (
        f"{TOGGLE_ON_EMOJI} **Daily Reward:** {int(settings['daily_min']):,} - {int(settings['daily_max']):,} Sancs\n"
        f"{TOGGLE_ON_EMOJI} **Weekly Reward:** {int(settings['weekly_min']):,} - {int(settings['weekly_max']):,} Sancs\n"
        f"{TOGGLE_ON_EMOJI} **Daily Streak Bonus:** {int(settings['daily_streak_bonus_amount']):,} every {int(settings['daily_streak_bonus_every'])} days\n"
        f"{TOGGLE_ON_EMOJI} **Daily Loot Crate Chance:** {int(settings['daily_loot_crate_chance'])}%\n"
        f"{TOGGLE_ON_EMOJI} **Weekly Daily Boost Chance:** {int(settings['weekly_daily_boost_chance'])}%\n"
        f"{TOGGLE_ON_EMOJI} **Weekly Luck Boost Chance:** {int(settings['weekly_luck_boost_chance'])}%\n"
        f"{TOGGLE_ON_EMOJI} **Weekly Boost Chance:** {int(settings['weekly_weekly_boost_chance'])}%"
    )

    embed = discord.Embed(
        title="Sanction Settings — Economy",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_footer(text="Use the dropdown below to edit economy settings.")

    return embed

class EconomyNumberModal(discord.ui.Modal):
    def __init__(self, title_text, setting_key, label, placeholder, min_value, max_value):
        super().__init__(title=title_text)
        self.setting_key = setting_key
        self.min_value = min_value
        self.max_value = max_value

        self.value_input = discord.ui.TextInput(
            label=label,
            placeholder=placeholder,
            min_length=1,
            max_length=7
        )

        self.add_item(self.value_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            value = int(str(self.value_input).strip())
        except ValueError:
            return await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

        if value < self.min_value or value > self.max_value:
            return await interaction.response.send_message(
                f"Value must be between {self.min_value:,} and {self.max_value:,}.",
                ephemeral=True
            )

        await set_economy_setting_db(interaction.guild.id, self.setting_key, value)

        settings = await get_economy_settings(interaction.guild.id)

        if int(settings["daily_min"]) > int(settings["daily_max"]):
            await set_economy_setting_db(interaction.guild.id, "daily_max", int(settings["daily_min"]))

        if int(settings["weekly_min"]) > int(settings["weekly_max"]):
            await set_economy_setting_db(interaction.guild.id, "weekly_max", int(settings["weekly_min"]))

        await interaction.response.edit_message(
            embed=await create_economy_settings_embed(interaction.guild.id),
            view=EconomySettingsView()
        )

class EconomySettingsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Set Daily Minimum", value="daily_min", description="Change the lowest /daily reward"),
            discord.SelectOption(label="Set Daily Maximum", value="daily_max", description="Change the highest /daily reward"),
            discord.SelectOption(label="Set Weekly Minimum", value="weekly_min", description="Change the lowest /weekly reward"),
            discord.SelectOption(label="Set Weekly Maximum", value="weekly_max", description="Change the highest /weekly reward"),
            discord.SelectOption(label="Set Streak Bonus Every", value="daily_streak_bonus_every", description="Change the streak milestone interval"),
            discord.SelectOption(label="Set Streak Bonus Amount", value="daily_streak_bonus_amount", description="Change the streak milestone bonus"),
            discord.SelectOption(label="Set Daily Crate Chance", value="daily_loot_crate_chance", description="Chance for /daily to drop a crate"),
            discord.SelectOption(label="Set Weekly Daily Boost Chance", value="weekly_daily_boost_chance", description="Chance weekly gives daily boost"),
            discord.SelectOption(label="Set Weekly Luck Boost Chance", value="weekly_luck_boost_chance", description="Chance weekly gives luck boost"),
            discord.SelectOption(label="Set Weekly Boost Chance", value="weekly_weekly_boost_chance", description="Chance weekly gives weekly boost"),
        ]

        super().__init__(
            placeholder="Choose an economy setting to edit...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can edit settings.", ephemeral=True)

        choice = self.values[0]

        modal_settings = {
            "daily_min": ("Set Daily Minimum", "Daily minimum reward", "Example: 75", 0, 1000000),
            "daily_max": ("Set Daily Maximum", "Daily maximum reward", "Example: 195", 0, 1000000),
            "weekly_min": ("Set Weekly Minimum", "Weekly minimum reward", "Example: 500", 0, 1000000),
            "weekly_max": ("Set Weekly Maximum", "Weekly maximum reward", "Example: 900", 0, 1000000),
            "daily_streak_bonus_every": ("Set Streak Bonus Every", "Every how many days?", "Example: 10", 1, 365),
            "daily_streak_bonus_amount": ("Set Streak Bonus Amount", "Bonus amount", "Example: 500", 0, 1000000),
            "daily_loot_crate_chance": ("Set Daily Crate Chance", "Chance percentage", "Example: 2", 0, 100),
            "weekly_daily_boost_chance": ("Set Weekly Daily Boost Chance", "Chance percentage", "Example: 15", 0, 100),
            "weekly_luck_boost_chance": ("Set Weekly Luck Boost Chance", "Chance percentage", "Example: 10", 0, 100),
            "weekly_weekly_boost_chance": ("Set Weekly Boost Chance", "Chance percentage", "Example: 5", 0, 100),
        }

        title_text, label, placeholder, min_value, max_value = modal_settings[choice]

        return await interaction.response.send_modal(
            EconomyNumberModal(title_text, choice, label, placeholder, min_value, max_value)
        )

class EconomySettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(EconomySettingsSelect())

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can use this.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_settings_home_embed(interaction.guild.id),
            view=SanctionSettingsView()
        )

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can refresh settings.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_economy_settings_embed(interaction.guild.id),
            view=EconomySettingsView()
        )

async def create_crate_settings_embed(guild_id):
    settings = await get_crate_settings(guild_id)

    description = (
        f"{TOGGLE_ON_EMOJI} **Regular Crate Rewards:** {int(settings['regular_crate_min']):,} - {int(settings['regular_crate_max']):,} Sancs\n"
        f"{TOGGLE_ON_EMOJI} **Legendary Crate Rewards:** {int(settings['legendary_crate_min']):,} - {int(settings['legendary_crate_max']):,} Sancs\n"
        f"{TOGGLE_ON_EMOJI} **Legendary Bonus Card Chance:** {int(settings['legendary_second_card_chance'])}%\n"
        f"{TOGGLE_ON_EMOJI} **Claim Loot Crate Chance:** {int(settings['claim_loot_crate_chance'])}%"
    )

    embed = discord.Embed(
        title="Sanction Settings — Crates",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_footer(text="Use the dropdown below to edit crate settings.")

    return embed

class CrateNumberModal(discord.ui.Modal):
    def __init__(self, title_text, setting_key, label, placeholder, min_value, max_value):
        super().__init__(title=title_text)
        self.setting_key = setting_key
        self.min_value = min_value
        self.max_value = max_value

        self.value_input = discord.ui.TextInput(
            label=label,
            placeholder=placeholder,
            min_length=1,
            max_length=7
        )

        self.add_item(self.value_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            value = int(str(self.value_input).strip())
        except ValueError:
            return await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

        if value < self.min_value or value > self.max_value:
            return await interaction.response.send_message(
                f"Value must be between {self.min_value:,} and {self.max_value:,}.",
                ephemeral=True
            )

        await set_crate_setting_db(interaction.guild.id, self.setting_key, value)

        settings = await get_crate_settings(interaction.guild.id)

        if int(settings["regular_crate_min"]) > int(settings["regular_crate_max"]):
            await set_crate_setting_db(interaction.guild.id, "regular_crate_max", int(settings["regular_crate_min"]))

        if int(settings["legendary_crate_min"]) > int(settings["legendary_crate_max"]):
            await set_crate_setting_db(interaction.guild.id, "legendary_crate_max", int(settings["legendary_crate_min"]))

        await interaction.response.edit_message(
            embed=await create_crate_settings_embed(interaction.guild.id),
            view=CrateSettingsView()
        )

class CrateSettingsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Set Regular Crate Minimum", value="regular_crate_min", description="Lowest Sanc reward from regular crates"),
            discord.SelectOption(label="Set Regular Crate Maximum", value="regular_crate_max", description="Highest Sanc reward from regular crates"),
            discord.SelectOption(label="Set Legendary Crate Minimum", value="legendary_crate_min", description="Lowest Sanc reward from legendary crates"),
            discord.SelectOption(label="Set Legendary Crate Maximum", value="legendary_crate_max", description="Highest Sanc reward from legendary crates"),
            discord.SelectOption(label="Set Legendary Bonus Card Chance", value="legendary_second_card_chance", description="Chance legendary crates give a bonus card"),
            discord.SelectOption(label="Set Claim Loot Crate Chance", value="claim_loot_crate_chance", description="Chance card claims give a loot crate"),
        ]

        super().__init__(
            placeholder="Choose a crate setting to edit...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can edit settings.", ephemeral=True)

        choice = self.values[0]

        modal_settings = {
            "regular_crate_min": ("Set Regular Crate Minimum", "Regular crate minimum Sancs", "Example: 100", 0, 1000000),
            "regular_crate_max": ("Set Regular Crate Maximum", "Regular crate maximum Sancs", "Example: 500", 0, 1000000),
            "legendary_crate_min": ("Set Legendary Crate Minimum", "Legendary crate minimum Sancs", "Example: 500", 0, 1000000),
            "legendary_crate_max": ("Set Legendary Crate Maximum", "Legendary crate maximum Sancs", "Example: 1500", 0, 1000000),
            "legendary_second_card_chance": ("Set Bonus Card Chance", "Chance percentage", "Example: 20", 0, 100),
            "claim_loot_crate_chance": ("Set Claim Loot Crate Chance", "Chance percentage", "Example: 5", 0, 100),
        }

        title_text, label, placeholder, min_value, max_value = modal_settings[choice]

        return await interaction.response.send_modal(
            CrateNumberModal(title_text, choice, label, placeholder, min_value, max_value)
        )

class CrateSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(CrateSettingsSelect())

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can use this.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_settings_home_embed(interaction.guild.id),
            view=SanctionSettingsView()
        )

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can refresh settings.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_crate_settings_embed(interaction.guild.id),
            view=CrateSettingsView()
        )

async def create_cosmetic_settings_embed(guild_id):
    profile_emojis = await get_active_profile_emojis()
    titles = await get_active_shop_titles()

    description = (
        f"{TOGGLE_ON_EMOJI} **Profile Emoji Shop:** {len(profile_emojis)} active options\n"
        f"{TOGGLE_ON_EMOJI} **Title Shop:** {len(titles)} active options\n"
        f"\nUse `/addprofileemoji`, `/removeprofileemoji`, `/listprofileemojis`.\n"
        f"Use `/addtitle`, `/removetitle`, `/listtitles`."
    )

    embed = discord.Embed(
        title="Sanction Settings — Cosmetics",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_footer(text="Choose a category to continue editing settings.")

    return embed

async def create_staff_settings_embed(guild_id):
    staff_role_id = await get_staff_role(guild_id)

    staff_role_text = f"<@&{staff_role_id}>" if staff_role_id else "`Not Set`"
    goos_channel_text = f"<#{goos_channel_id}>" if goos_channel_id else "`Not Set`"

    description = (
        f"**Staff Role**\n"
        f"{staff_role_text}\n"
        f"`/setstaffrole role:@RoleName`\n\n"
        f"**Goos / Staff Log Channel**\n"
        f"{goos_channel_text}\n"
        f"`/setgooslogchannel channel:#channel`\n\n"
        f"**Test Log Channel**\n"
        f"`/gooslogtest`"
    )

    embed = discord.Embed(
        title="Sanction Settings — Staff",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )

    return embed

async def create_settings_embed(guild_id):
    return await create_settings_home_embed(guild_id)

class SnipeCooldownModal(discord.ui.Modal, title="Set Snipe Cooldown"):
    minutes = discord.ui.TextInput(
        label="Cooldown in minutes",
        placeholder="Example: 5",
        min_length=1,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            minutes = int(str(self.minutes).strip())
        except ValueError:
            return await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

        if minutes < 1 or minutes > 120:
            return await interaction.response.send_message("Cooldown must be between 1 and 120 minutes.", ephemeral=True)

        await set_snipe_cooldown_db(interaction.guild.id, minutes)

        await interaction.response.edit_message(
            embed=await create_snipe_settings_embed(interaction.guild.id),
            view=SnipeSettingsView()
        )

class SnipeMuteModal(discord.ui.Modal, title="Set Snipe Mute Time"):
    minutes = discord.ui.TextInput(
        label="Mute time in minutes",
        placeholder="Example: 5",
        min_length=1,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            minutes = int(str(self.minutes).strip())
        except ValueError:
            return await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

        if minutes < 1 or minutes > 60:
            return await interaction.response.send_message("Mute time must be between 1 and 60 minutes.", ephemeral=True)

        await set_snipe_mute_minutes_db(interaction.guild.id, minutes)

        await interaction.response.edit_message(
            embed=await create_snipe_settings_embed(interaction.guild.id),
            view=SnipeSettingsView()
        )

class AutoDropIntervalModal(discord.ui.Modal, title="Set Auto Drop Interval"):
    minutes = discord.ui.TextInput(
        label="Minutes between auto drop checks",
        placeholder="Example: 30",
        min_length=1,
        max_length=4
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            minutes = int(str(self.minutes).strip())
        except ValueError:
            return await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

        if minutes < 1 or minutes > 1440:
            return await interaction.response.send_message("Auto drop interval must be between 1 and 1440 minutes.", ephemeral=True)

        await set_auto_drop_minutes_db(interaction.guild.id, minutes)

        await interaction.response.edit_message(
            embed=await create_drop_settings_embed(interaction.guild.id),
            view=DropSettingsView()
        )

class AutoDropChanceModal(discord.ui.Modal, title="Set Auto Drop Chance"):
    chance = discord.ui.TextInput(
        label="Chance percentage",
        placeholder="Example: 40",
        min_length=1,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            chance = int(str(self.chance).strip())
        except ValueError:
            return await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

        if chance < 0 or chance > 100:
            return await interaction.response.send_message("Chance must be between 0 and 100.", ephemeral=True)

        await set_auto_drop_chance_db(interaction.guild.id, chance)

        await interaction.response.edit_message(
            embed=await create_drop_settings_embed(interaction.guild.id),
            view=DropSettingsView()
        )

class ClaimCooldownModal(discord.ui.Modal, title="Set Claim Cooldown"):
    seconds = discord.ui.TextInput(
        label="Claim cooldown in seconds",
        placeholder="Example: 30",
        min_length=1,
        max_length=4
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            seconds = int(str(self.seconds).strip())
        except ValueError:
            return await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

        if seconds < 0 or seconds > 3600:
            return await interaction.response.send_message("Claim cooldown must be between 0 and 3600 seconds.", ephemeral=True)

        await set_claim_cooldown_db(interaction.guild.id, seconds)

        await interaction.response.edit_message(
            embed=await create_drop_settings_embed(interaction.guild.id),
            view=DropSettingsView()
        )

class DropSettingsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Toggle Auto Drops", value="toggle_auto_drops", description="Turn automatic card drops on or off"),
            discord.SelectOption(label="Set Auto Drop Interval", value="set_auto_drop_interval", description="Change minutes between auto drop checks"),
            discord.SelectOption(label="Set Auto Drop Chance", value="set_auto_drop_chance", description="Change auto drop chance percentage"),
            discord.SelectOption(label="Set Claim Cooldown", value="set_claim_cooldown", description="Change claim cooldown in seconds"),
        ]

        super().__init__(
            placeholder="Choose a card drop setting to edit...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can edit settings.", ephemeral=True)

        choice = self.values[0]

        if choice == "toggle_auto_drops":
            settings = await get_drop_settings(interaction.guild.id)
            new_value = not settings["auto_drop_enabled"]
            await set_auto_drop_enabled_db(interaction.guild.id, new_value)

            return await interaction.response.edit_message(
                embed=await create_drop_settings_embed(interaction.guild.id),
                view=DropSettingsView()
            )

        if choice == "set_auto_drop_interval":
            return await interaction.response.send_modal(AutoDropIntervalModal())

        if choice == "set_auto_drop_chance":
            return await interaction.response.send_modal(AutoDropChanceModal())

        if choice == "set_claim_cooldown":
            return await interaction.response.send_modal(ClaimCooldownModal())

class DropSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(DropSettingsSelect())

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can use this.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_settings_home_embed(interaction.guild.id),
            view=SanctionSettingsView()
        )

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can refresh settings.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_drop_settings_embed(interaction.guild.id),
            view=DropSettingsView()
        )

class StaffSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "Only administrators can use this.",
                ephemeral=True
            )

        await interaction.response.edit_message(
            embed=await create_settings_home_embed(interaction.guild.id),
            view=SanctionSettingsView()
        )

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "Only administrators can refresh settings.",
                ephemeral=True
            )

        await interaction.response.edit_message(
            embed=await create_staff_settings_embed(interaction.guild.id),
            view=StaffSettingsView()
        )

class SettingsCategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Snipe Settings", value="snipe", description="Staff sniping, cooldown, mute time"),
            discord.SelectOption(label="Card Drop Settings", value="drops", description="Auto drops, claim cooldown, drop channels"),
            discord.SelectOption(label="Economy Settings", value="economy", description="Daily, weekly, and currency settings"),
            discord.SelectOption(label="Crate Settings", value="crates", description="Loot crate rewards and odds"),
            discord.SelectOption(label="Cosmetic Settings", value="cosmetics", description="Profile emojis and titles"),
            discord.SelectOption(label="Staff Settings", value="staff", description="Staff role and log channels"),
        ]

        super().__init__(
            placeholder="Choose a settings category...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can edit settings.", ephemeral=True)

        choice = self.values[0]

        if choice == "snipe":
            return await interaction.response.edit_message(
                embed=await create_snipe_settings_embed(interaction.guild.id),
                view=SnipeSettingsView()
            )

        if choice == "drops":
            return await interaction.response.edit_message(
                embed=await create_drop_settings_embed(interaction.guild.id),
                view=DropSettingsView()
            )

        if choice == "economy":
            return await interaction.response.edit_message(
                embed=await create_economy_settings_embed(interaction.guild.id),
                view=EconomySettingsView()
            )

        if choice == "crates":
            return await interaction.response.edit_message(
                embed=await create_crate_settings_embed(interaction.guild.id),
                view=CrateSettingsView()
            )

        if choice == "cosmetics":
            return await interaction.response.edit_message(
                embed=await create_cosmetic_settings_embed(interaction.guild.id),
                view=SettingsBackView()
            )

        if choice == "staff":
            return await interaction.response.edit_message(
                embed=await create_staff_settings_embed(interaction.guild.id),
                view=StaffSettingsView()
            )

class SanctionSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SettingsCategorySelect())

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can refresh settings.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_settings_home_embed(interaction.guild.id),
            view=SanctionSettingsView()
        )

class SettingsBackView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can use this.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_settings_home_embed(interaction.guild.id),
            view=SanctionSettingsView()
        )

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can use this.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_settings_home_embed(interaction.guild.id),
            view=SanctionSettingsView()
        )

class SnipeSettingsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Toggle Staff Sniping", value="toggle_staff_snipe", description="Turn staff sniping on or off"),
            discord.SelectOption(label="Set Snipe Cooldown", value="set_cooldown", description="Change cooldown time in minutes"),
            discord.SelectOption(label="Set Snipe Mute Time", value="set_mute", description="Change mute time in minutes"),
        ]

        super().__init__(
            placeholder="Choose a snipe setting to edit...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can edit settings.", ephemeral=True)

        choice = self.values[0]

        if choice == "toggle_staff_snipe":
            settings = await get_snipe_settings(interaction.guild.id)
            new_value = not settings["staff_snipe_enabled"]
            await set_staff_snipe_enabled(interaction.guild.id, new_value)

            return await interaction.response.edit_message(
                embed=await create_snipe_settings_embed(interaction.guild.id),
                view=SnipeSettingsView()
            )

        if choice == "set_cooldown":
            return await interaction.response.send_modal(SnipeCooldownModal())

        if choice == "set_mute":
            return await interaction.response.send_modal(SnipeMuteModal())

class SnipeSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SnipeSettingsSelect())

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can use this.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_settings_home_embed(interaction.guild.id),
            view=SanctionSettingsView()
        )

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can refresh settings.", ephemeral=True)

        await interaction.response.edit_message(
            embed=await create_snipe_settings_embed(interaction.guild.id),
            view=SnipeSettingsView()
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
@bot.tree.command(name="settings", description="Admin only: view and edit bot game settings.")
@app_commands.default_permissions(administrator=True)
async def settings(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use settings.", ephemeral=True)

    await interaction.response.send_message(
        embed=await create_settings_home_embed(interaction.guild.id),
        view=SanctionSettingsView(),
        ephemeral=True
    )

@bot.tree.command(name="ping", description="Staff only: check if the bot is online.")
@app_commands.default_permissions(manage_messages=True)
async def ping(interaction: discord.Interaction):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    await interaction.response.send_message("Online!", ephemeral=True)

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
    economy_settings = await get_economy_settings(interaction.guild.id)
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
    amount = random.randint(int(economy_settings["daily_min"]), int(economy_settings["daily_max"]))
    streak = await update_daily_streak(user_id)
    bonus = 0
    if streak % int(economy_settings["daily_streak_bonus_every"]) == 0:
        bonus = int(economy_settings["daily_streak_bonus_amount"])
    found_crate = random.randint(1, 100) <= int(economy_settings["daily_loot_crate_chance"])
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
    economy_settings = await get_economy_settings(interaction.guild.id)
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

    await interaction.response.send_message(
        f"{WEEKLY_BOX_EMOJI} | Your Weekly Box is unsealing!"
    )

    await asyncio.sleep(2)

    amount = random.randint(int(economy_settings["weekly_min"]), int(economy_settings["weekly_max"]))
    boost_bonus = 0

    if await get_active_boost(user_id, "weekly"):
        boost_bonus = int(amount * WEEKLY_BOOST_PERCENT / 100)
        await clear_boost(user_id, "weekly")

    total = amount + boost_bonus

    await add_balance(user_id, total)
    await add_loot_crate(user_id, "regular", 1)
    await set_cooldown(user_id, "weekly")

    reward_lines = [
        f"{BULLET_EMOJI} **Sancs:** {format_coins(total)}",
        f"{BULLET_EMOJI} **Loot Crate:** 1 {LOOT_CRATE_EMOJI}",
    ]

    if boost_bonus > 0:
        reward_lines.append(
            f"{BULLET_EMOJI} {WEEKLY_BOOST_EMOJI} **Weekly Boost bonus:** {format_coins(boost_bonus)}"
        )

    found_daily_boost = random.randint(1, 100) <= int(economy_settings["weekly_daily_boost_chance"])
    found_luck_boost = random.randint(1, 100) <= int(economy_settings["weekly_luck_boost_chance"])
    found_weekly_boost = random.randint(1, 100) <= int(economy_settings["weekly_weekly_boost_chance"])

    if found_daily_boost:
        await set_boost(user_id, "daily", 24 * 60 * 60)
        reward_lines.append(f"{BULLET_EMOJI} {DAILY_BOOST_EMOJI} **Daily Boost:** applies to your next /daily")

    if found_luck_boost:
        await set_boost(user_id, "luck", 60 * 60)
        reward_lines.append(f"{BULLET_EMOJI} {LUCK_BOOST_EMOJI} **Luck Boost:** active for 1 hour")

    if found_weekly_boost:
        await set_boost(user_id, "weekly", 7 * 24 * 60 * 60)
        reward_lines.append(f"{BULLET_EMOJI} {WEEKLY_BOOST_EMOJI} **Weekly Boost:** applies to your next /weekly")

    rewards_text = "\n".join(reward_lines)

    await interaction.edit_original_response(
        content=rewards_text
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

    if amount > MAX_GIVECURRENCY_PER_TRANSFER:
        return await interaction.response.send_message(
            f"You can only send up to **{format_coins(MAX_GIVECURRENCY_PER_TRANSFER)}** at once.",
            ephemeral=True
        )

    daily_usage = await get_daily_limit_row(interaction.user.id, "givecurrency")

    if daily_usage["amount_value"] + amount > MAX_GIVECURRENCY_PER_DAY:
        remaining = max(0, MAX_GIVECURRENCY_PER_DAY - daily_usage["amount_value"])
        return await interaction.response.send_message(
            f"You can only send **{format_coins(MAX_GIVECURRENCY_PER_DAY)}** per day. "
            f"You have **{format_coins(remaining)}** left today.",
            ephemeral=True
        )

    success = await transfer_balance(interaction.user.id, user.id, amount)
    if not success:
        return await interaction.response.send_message(
            "You do not have enough currency.",
            ephemeral=True
        )
    await add_daily_limit_usage(interaction.user.id, "givecurrency", amount_add=amount)

    await interaction.response.send_message(
        f"{interaction.user.mention} gave {user.mention} **{format_coins(amount)}**."
    )

@bot.tree.command(name="addbal", description="Staff only: add currency to a user's balance.")
@app_commands.default_permissions(manage_messages=True)
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
        custom_emoji = await get_user_custom_emoji(row["user_id"])
        emoji_text = f" {custom_emoji}" if custom_emoji else ""
        text += f"{place} {user_mention}{emoji_text}{title_text}\n"
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

@bot.tree.command(name="viewtitles", description="View titles available for purchase.")
async def viewtitles(interaction: discord.Interaction):
    await interaction.response.send_message(embed=await create_title_shop_embed())

@bot.tree.command(name="buy", description="Buy an item from the shop.")
@app_commands.describe(item="Choose an item to buy")
@app_commands.autocomplete(item=shop_autocomplete)
async def buy(interaction: discord.Interaction, item: str):
    if item == "profileemoji":
        rows = await get_active_profile_emojis()

        if not rows:
            return await interaction.response.send_message("No profile emojis are available right now.", ephemeral=True)

        return await interaction.response.send_message(
            embed=await create_profile_emoji_shop_embed(),
            view=ProfileEmojiBuyView(rows),
            ephemeral=True
        )

    if item == "title":
        rows = await get_active_shop_titles()

        if not rows:
            return await interaction.response.send_message("No titles are available right now.", ephemeral=True)

        return await interaction.response.send_message(
            embed=await create_title_shop_embed(),
            view=TitleBuyView(rows),
            ephemeral=True
        )

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
    if shop_item.get("snipe_item"):
        await add_snipe_item(interaction.user.id, shop_item["snipe_item"], 1)
        return await interaction.response.send_message(
            f"{interaction.user.mention} bought **1 {SNIPE_EMOJI} {shop_item['name']}** for **{format_coins(shop_item['price'])}**! Use `/snipe` to start a snipe."
        )

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
            f"Requested: **{shop_item['goos_amount']} Goos**\n"
            f"Cost: **{format_coins(shop_item['price'])}**\n"
            f"A staff member will need to fulfill this manually. Please open a ticket and include your request ID.",
            ephemeral=True
        )

        log_sent = await send_goos_log(interaction, request_id, shop_item)

        if not log_sent:
            await interaction.followup.send(
                "Heads up: no Goos log channel is set or I could not send to it. Please ask an admin to run `/setgooslogchannel`.",
                ephemeral=True
            )
        return
    await interaction.response.send_message(
        f"{interaction.user.mention} bought **{shop_item['name']}** for **{format_coins(shop_item['price'])}**!"
    )

@bot.tree.command(name="togglestaffsnipe", description="Enable or disable sniping staff members.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(enabled="Turn staff sniping on or off")
@app_commands.checks.has_permissions(administrator=True)
async def togglestaffsnipe(interaction: discord.Interaction, enabled: bool):
    await set_staff_snipe_enabled(interaction.guild.id, enabled)

    if enabled:
        message = "Staff members can now be sniped."
    else:
        message = "Staff members can no longer be sniped."

    await interaction.response.send_message(
        f"{SNIPE_EMOJI} | {message}"
    )

@bot.tree.command(name="snipe", description="Use a Sniper to target another user.")
@app_commands.describe(user="User to snipe")
async def snipe(interaction: discord.Interaction, user: discord.Member):
    sniper = interaction.user
    target = user
    sniper_id = sniper.id
    target_id = target.id
    snipe_settings = await get_snipe_settings(interaction.guild.id)
    snipe_cooldown = int(snipe_settings["snipe_cooldown_seconds"])
    snipe_mute_minutes = int(snipe_settings["snipe_mute_minutes"])

    if target.bot:
        return await interaction.response.send_message("You cannot snipe a bot.", ephemeral=True)

    staff_snipe_enabled = snipe_settings["staff_snipe_enabled"]

    saved_staff_role_id = await get_staff_role(interaction.guild.id)

    if not staff_snipe_enabled and saved_staff_role_id:
        if any(role.id == saved_staff_role_id for role in target.roles):
            return await interaction.response.send_message(
                "Staff sniping is currently disabled in settings.",
                ephemeral=True
            )

    if target_id == sniper_id:
        return await interaction.response.send_message("You cannot snipe yourself.", ephemeral=True)

    if target.timed_out_until and target.timed_out_until > discord.utils.utcnow():
        return await interaction.response.send_message("That user is already muted.", ephemeral=True)

    now = int(time.time())
    last_used = await get_cooldown(sniper_id, "snipe")

    if last_used and now - last_used < snipe_cooldown:
        remaining = snipe_cooldown - (now - last_used)
        minutes = remaining // 60
        seconds = remaining % 60

        return await interaction.response.send_message(
            f"You are on snipe cooldown. Try again in {minutes}m {seconds}s.",
            ephemeral=True
        )

    regular_snipers, legendary_snipers = await get_snipe_items(sniper_id)

    if regular_snipers <= 0 and legendary_snipers <= 0:
        return await interaction.response.send_message(
            f"You do not have any {SNIPE_EMOJI} Snipers. Buy one from `/shop` first.",
            ephemeral=True
        )

    snipe_type = "legendary" if legendary_snipers > 0 else "regular"
    view = SnipeGameView(sniper=sniper, target=target, snipe_type=snipe_type, mute_minutes=snipe_mute_minutes)

    await interaction.response.send_message(
        f"{SNIPE_EMOJI} | {target.mention} is being targeted by {sniper.mention}.\n"
        f"{target.mention}, choose a bush to hide in.",
        view=view
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
    crate_settings = await get_crate_settings(interaction.guild.id)
    selected_type = crate_type.value
    removed = await remove_loot_crate(user_id, selected_type)
    if not removed:
        crate_name = "Legendary Loot Crate" if selected_type == "legendary" else "Loot Crate"
        return await interaction.response.send_message(
            f"You do not have any **{crate_name}s** to open.",
            ephemeral=True
        )
    if selected_type == "legendary":
        coins = random.randint(int(crate_settings["legendary_crate_min"]), int(crate_settings["legendary_crate_max"]))
        first_card = await choose_legendary_crate_card(user_id)
        second_card = None
        if random.randint(1, 100) <= int(crate_settings["legendary_second_card_chance"]):
            second_card = await choose_legendary_crate_card(user_id)
        crate_emoji = LEGENDARY_CRATE_EMOJI
        crate_name = "Legendary Loot Crate"
    else:
        coins = random.randint(int(crate_settings["regular_crate_min"]), int(crate_settings["regular_crate_max"]))
        first_card = await choose_regular_crate_card(user_id)
        second_card = None
        crate_emoji = LOOT_CRATE_EMOJI
        crate_name = "Loot Crate"
    await add_balance(user_id, coins)
    rewards = f"**Sancs:** {format_coins(coins)}"
    if first_card:
        await add_card_to_inventory(user_id, first_card["id"])
        rewards += f"\n**Card:** **ID:** `{first_card['id']}` {first_card['name']} ({first_card['rarity']})"
    if second_card:
        await add_card_to_inventory(user_id, second_card["id"])
        rewards += f"\n**Bonus Card:** **ID:** `{second_card['id']}` {second_card['name']} ({second_card['rarity']})"
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
                text += f"{BULLET_EMOJI} **ID:** `{card['id']}` {card['name']} ({card['rarity']})\n"
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
    regular_snipers, legendary_snipers = await get_snipe_items(user.id)
    title = await get_title(user.id)
    custom_emoji = await get_user_custom_emoji(user.id)
    owned_profile_emojis = await get_user_owned_profile_emojis(user.id)
    owned_titles = await get_user_owned_titles(user.id)
    emoji_text = f" {custom_emoji}" if custom_emoji else ""
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
    text += f"{BULLET_EMOJI} {LEGENDARY_CRATE_EMOJI} **Legendary Loot Crates:** {legendary_crates}\n"

    if regular_snipers > 0:
        text += f"{BULLET_EMOJI} {SNIPE_EMOJI} **Snipers:** {regular_snipers}\n"

    if legendary_snipers > 0:
        text += f"{BULLET_EMOJI} {LEGENDARY_SNIPER_EMOJI} **Legendary Snipers:** {legendary_snipers}\n"

    if owned_profile_emojis:
        text += "\n**Owned Profile Emojis**\n"

        for owned_emoji in owned_profile_emojis:
            text += f"{BULLET_EMOJI} {owned_emoji['emoji']} `{owned_emoji['name']}`\n"

    if owned_titles:
        text += "\n**Owned Titles**\n"

        for owned_title in owned_titles:
            text += f"{BULLET_EMOJI} `{owned_title}`\n"

    text += "\n"
    if not rows:
        text += "No cards yet."
    else:
        for r in rows:
            limited_note = "" if r["is_active"] else " *(unobtainable)*"
            text += f"{BULLET_EMOJI} **ID:** `{r['id']}` {r['name']} ({r['rarity']}) x{r['amount']}{limited_note}\n"
    inventory_title = f"{title} {user.display_name}{emoji_text}'s Inventory" if title else f"{user.display_name}{emoji_text}'s Inventory"
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
    requester_trade_usage = await get_daily_limit_row(interaction.user.id, "trade")
    target_trade_usage = await get_daily_limit_row(user.id, "trade")

    if requester_trade_usage["count_value"] >= MAX_TRADES_PER_DAY:
        return await interaction.response.send_message(
            f"You have reached your daily trade limit of **{MAX_TRADES_PER_DAY}** trades.",
            ephemeral=True
        )

    if target_trade_usage["count_value"] >= MAX_TRADES_PER_DAY:
        return await interaction.response.send_message(
            f"{user.display_name} has reached their daily trade limit of **{MAX_TRADES_PER_DAY}** trades.",
            ephemeral=True
        )

    view = TradeView(interaction.user, user, your_card_data, their_card_data)
    embed = discord.Embed(
        title="Trade Request",
        description=(
            f"{interaction.user.mention} offers **{your_card_data['name']}** `**ID:** `{your_card_data['id']}``\n"
            f"in exchange for **{their_card_data['name']}** `**ID:** `{their_card_data['id']}`` from {user.mention}\n\n"
            f"{user.mention}, accept or decline this trade."
        ),
        color=discord.Color.from_str("#9e659d")
    )
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="addcard", description="Staff only: add or reactivate a collectible card.")
@app_commands.default_permissions(manage_messages=True)
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
                f"Reactivated/updated **{name}** as a **{rarity.value}** card. `**ID:** `{existing_card['id']}``"
            )
        new_id = await conn.fetchval(
            "INSERT INTO cards (name, rarity, image, is_active) VALUES ($1,$2,$3, TRUE) RETURNING id",
            name,
            rarity.value,
            image
        )
    await interaction.response.send_message(f"Added **{name}** as a **{rarity.value}** card. `**ID:** `{new_id}``")

@bot.tree.command(name="dropcard", description="Staff only: drop a card.")
@app_commands.default_permissions(manage_messages=True)
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
@app_commands.default_permissions(manage_messages=True)
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
            f"Are you sure you want to remove **{card['name']}** **ID:** `{card['id']}` from future drops and card lists?\n\n"
            f"Members who already own it will **keep it**."
        ),
        color=discord.Color.red()
    )
    await interaction.response.send_message(
        embed=embed,
        view=RemoveCardView(interaction.user, card),
        ephemeral=True
    )

@bot.tree.command(name="addtitle", description="Staff only: add a preset title to the shop.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(
    title="Title text to sell",
    price="Price in Sancs"
)
async def addtitle(interaction: discord.Interaction, title: str, price: int):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    if price <= 0:
        return await interaction.response.send_message("Price must be greater than 0.", ephemeral=True)

    title_id = await add_title_to_shop(title, price)

    await interaction.response.send_message(
        f"Added title **{title}** for **{format_coins(price)}**. **ID:** `{title_id}`"
    )

@bot.tree.command(name="removetitle", description="Staff only: remove a preset title from the shop.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(title="Title to remove")
async def removetitle(interaction: discord.Interaction, title: str):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    removed = await remove_title_from_shop(title)

    if not removed:
        return await interaction.response.send_message("That title was not found.", ephemeral=True)

    await interaction.response.send_message(f"Removed **{title}** from the title shop.")

@bot.tree.command(name="listtitles", description="View all preset titles in the shop.")
async def listtitles(interaction: discord.Interaction):
    rows = await get_active_shop_titles()

    if not rows:
        return await interaction.response.send_message("No titles are in the shop yet.")

    grouped = {}

    for row in rows:
        grouped.setdefault(row["price"], []).append(row)

    text = ""

    for price in sorted(grouped.keys()):
        text += f"**{format_coins(price)}**\n"

        for row in grouped[price]:
            text += f"{BULLET_EMOJI} `{row['title']}` — {format_coins(row['price'])}\n"

        text += "\n"

    embed = discord.Embed(
        title="Title Shop List",
        description=text,
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="addprofileemoji", description="Staff only: add a preset profile emoji to the shop.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(
    name="Emoji display name",
    emoji="Emoji to sell",
    price="Price in Sancs"
)
async def addprofileemoji(interaction: discord.Interaction, name: str, emoji: str, price: int):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    if price <= 0:
        return await interaction.response.send_message("Price must be greater than 0.", ephemeral=True)

    emoji_id = await add_profile_emoji_to_shop(name, emoji, price)

    await interaction.response.send_message(
        f"Added profile emoji **{name}** {emoji} for **{format_coins(price)}**. **ID:** `{emoji_id}`"
    )

@bot.tree.command(name="removeprofileemoji", description="Staff only: remove a preset profile emoji from the shop.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(name="Profile emoji name to remove")
async def removeprofileemoji(interaction: discord.Interaction, name: str):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    removed = await remove_profile_emoji_from_shop(name)

    if not removed:
        return await interaction.response.send_message("That profile emoji was not found.", ephemeral=True)

    await interaction.response.send_message(f"Removed **{name}** from the profile emoji shop.")

@bot.tree.command(name="listprofileemojis", description="View all preset profile emojis in the shop.")
async def listprofileemojis(interaction: discord.Interaction):
    rows = await get_active_profile_emojis()

    if not rows:
        return await interaction.response.send_message("No profile emojis are in the shop yet.")

    grouped = {}

    for row in rows:
        grouped.setdefault(row["price"], []).append(row)

    text = ""

    for price in sorted(grouped.keys()):
        text += f"**{format_coins(price)}**\n"

        for row in grouped[price]:
            text += f"{BULLET_EMOJI} {row['emoji']} `{row['name']}` — {format_coins(row['price'])}\n"

        text += "\n"

    embed = discord.Embed(
        title="Profile Emoji Shop List",
        description=text,
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="equipemoji", description="Equip one of your owned profile emojis.")
@app_commands.describe(emoji="Choose an emoji you own")
@app_commands.autocomplete(emoji=owned_profile_emoji_autocomplete)
async def equipemoji(interaction: discord.Interaction, emoji: str):
    try:
        profile_emoji_id = int(emoji)
    except ValueError:
        return await interaction.response.send_message("That profile emoji was not found.", ephemeral=True)

    if not await user_owns_profile_emoji(interaction.user.id, profile_emoji_id):
        return await interaction.response.send_message("You do not own that profile emoji.", ephemeral=True)

    profile_emoji = await get_profile_emoji_by_id(profile_emoji_id)

    if not profile_emoji:
        return await interaction.response.send_message("That profile emoji is no longer available.", ephemeral=True)

    await set_user_custom_emoji(interaction.user.id, profile_emoji["emoji"])

    await interaction.response.send_message(
        f"Equipped **{profile_emoji['name']}** {profile_emoji['emoji']}."
    )

@bot.tree.command(name="equiptitle", description="Equip one of your owned titles.")
@app_commands.describe(title="Choose a title you own")
@app_commands.autocomplete(title=owned_title_autocomplete)
async def equiptitle(interaction: discord.Interaction, title: str):
    owned_titles = await get_user_owned_titles(interaction.user.id)

    if title not in owned_titles:
        return await interaction.response.send_message("You do not own that title.", ephemeral=True)

    await set_title(interaction.user.id, title)

    await interaction.response.send_message(f"Equipped title **{title}**.")

@bot.tree.command(name="setstaffrole", description="Admin only: set the staff role for this server.")
@app_commands.default_permissions(administrator=True)
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

@bot.tree.command(name="addropchannel", description="Staff only: add a channel for automatic card drops.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(channel="Channel where automatic drops can happen")
async def addropchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)
    await add_drop_channel_db(interaction.guild.id, channel.id)
    await interaction.response.send_message(
        f"Added {channel.mention} as a drop channel."
    )

@bot.tree.command(name="removedropchannel", description="Staff only: remove a channel from automatic card drops.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(channel="Channel to remove from automatic drops")
async def removedropchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)
    await remove_drop_channel_db(interaction.guild.id, channel.id)
    await interaction.response.send_message(
        f"Removed {channel.mention} from drop channels."
    )

@bot.tree.command(name="listdropchannels", description="Staff only: view this server's automatic card drop channels.")
@app_commands.default_permissions(manage_messages=True)
async def listdropchannels(interaction: discord.Interaction):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

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

@bot.tree.command(name="givesniper", description="Staff only: give sniper items.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(
    user="User to give snipers to",
    amount="Amount to give",
    sniper_type="Choose regular or legendary"
)
@app_commands.choices(
    sniper_type=[
        app_commands.Choice(name="Regular", value="regular"),
        app_commands.Choice(name="Legendary", value="legendary"),
    ]
)
async def givesniper(
    interaction: discord.Interaction,
    user: discord.Member,
    amount: app_commands.Range[int, 1, 100] = 1,
    sniper_type: app_commands.Choice[str] = None
):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    sniper_value = sniper_type.value if sniper_type else "regular"

    await add_snipe_item(user.id, sniper_value, amount)

    sniper_name = "Legendary Sniper" if sniper_value == "legendary" else "Sniper"

    await interaction.response.send_message(
        f"Gave {user.mention} **{amount}x {sniper_name}**."
    )

@bot.tree.command(name="givecrate", description="Staff only: give loot crates.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(
    user="User to give crates to",
    amount="Amount to give",
    crate_type="Choose regular or legendary"
)
@app_commands.choices(
    crate_type=[
        app_commands.Choice(name="Regular", value="regular"),
        app_commands.Choice(name="Legendary", value="legendary"),
    ]
)
async def givecrate(
    interaction: discord.Interaction,
    user: discord.Member,
    amount: app_commands.Range[int, 1, 100] = 1,
    crate_type: app_commands.Choice[str] = None
):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    crate_value = crate_type.value if crate_type else "regular"

    await add_loot_crate(user.id, crate_value, amount)

    crate_name = "Legendary Loot Crate" if crate_value == "legendary" else "Loot Crate"

    await interaction.response.send_message(
        f"Gave {user.mention} **{amount}x {crate_name}**."
    )

@bot.tree.command(name="help", description="View member commands and bot help.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Sanction Bot Help",
        description="Here’s everything you need to survive.",
        color=discord.Color.from_str("#9e659d")
    )

    embed.add_field(
        name="Currency",
        value=(
            "`/balance` — View your Sancs balance\n"
            "`/daily` — Claim your daily Sancs\n"
            "`/weekly` — Claim your weekly reward\n"
            "`/givecurrency` — Give Sancs to another member\n"
            "`/leaderboard` — View the richest members\n"
            "`/shop` — Open the shop\n"
            "`/buy` — Buy an item\n"
            "`/sell` — Sell one of your cards"
        ),
        inline=False
    )

    embed.add_field(
        name="Cards",
        value=(
            "`/cards` — View obtainable cards\n"
            "`/viewcard` — View a specific card\n"
            "`/inventory` — View your inventory\n"
            "`/trade` — Trade cards with another member\n"
            "`/opencrate` — Open a loot crate"
        ),
        inline=False
    )

    embed.add_field(
        name="Cosmetics",
        value=(
            "`/listtitles` — View available titles\n"
            "`/equiptitle` — Equip a title you own\n"
            "`/listprofileemojis` — View available profile emojis\n"
            "`/equipemoji` — Equip a profile emoji you own"
        ),
        inline=False
    )

    embed.add_field(
        name="Snipe",
        value="`/snipe` — Use a sniper against another member",
        inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="staffhelp", description="Staff only: view staff and admin commands.")
@app_commands.default_permissions(manage_messages=True)
async def staffhelp(interaction: discord.Interaction):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    embed = discord.Embed(
        title="Staff Help",
        description="Staff and admin command reference.",
        color=discord.Color.from_str("#9e659d")
    )

    embed.add_field(
        name="Staff Currency / Rewards",
        value=(
            "`/addbal` — Add Sancs to a member\n"
            "`/givesniper` — Give regular or legendary snipers\n"
            "`/givecrate` — Give regular or legendary crates"
        ),
        inline=False
    )

    embed.add_field(
        name="Staff Cards",
        value=(
            "`/addcard` — Add or reactivate a card\n"
            "`/dropcard` — Manually drop a card\n"
            "`/removecard` — Remove a card from future drops"
        ),
        inline=False
    )

    embed.add_field(
        name="Drop Channels",
        value=(
            "`/addropchannel` — Add an auto-drop channel\n"
            "`/removedropchannel` — Remove an auto-drop channel\n"
            "`/listdropchannels` — View auto-drop channels"
        ),
        inline=False
    )

    embed.add_field(
        name="Cosmetics",
        value=(
            "`/addtitle` — Add a title to the shop\n"
            "`/removetitle` — Remove a title from the shop\n"
            "`/addprofileemoji` — Add a profile emoji to the shop\n"
            "`/removeprofileemoji` — Remove a profile emoji from the shop"
        ),
        inline=False
    )

    embed.add_field(
        name="Admin / Setup",
        value=(
            "`/settings` — Open Sanction Settings\n"
            "`/setstaffrole` — Set the staff command role\n"
            "`/togglestaffsnipe` — Toggle staff sniping\n"
            "`/ping` — Check if the bot is online"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

# ---------------- RUN ----------------
bot.run(TOKEN)
