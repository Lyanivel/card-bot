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
EVENT_REWARD_BOOST_PERCENT = 25
SNIPE_PRICE = 2500
SNIPE_COOLDOWN = 10 * 60
SNIPE_MUTE_MINUTES = 5
MAX_TRADES_PER_DAY = 5
MAX_GIVECURRENCY_PER_DAY = 25000
MAX_GIVECURRENCY_PER_TRANSFER = 10000

DAILY_CLAIM_MESSAGES = [
    "You shook the money tree and found {amount} Sancs.",
    "You checked under the couch cushions and found {amount} Sancs.",
    "The Sanction treasury grants you {amount} Sancs.",
    "Another day, another sanc! {amount}",
    "Take your Sancs and go!",
    "You found {amount} Sancs. Please stop looking for more.",
    "Congratulations. You are now {amount} Sancs richer.",
    "You discovered {amount} Sancs hiding in plain sight.",
    "The treasury sighs and gives you {amount} Sancs.",
    "Someone left {amount} Sancs unattended. They're yours now.",
    "You got {amount} Sancs. Don't spend it all in one place.",
    "Your reward for existing: {amount} Sancs.",
]

WEEKLY_CLAIM_MESSAGES = [
    "Another week, another reward.",
    "Let's see if the wait was worth it.",
    "A week's worth of patience pays off.",
    "Seven days later...",
    "Let's find out what fate had planned this week.",
    "You survived another week. Barely.",
    "Congratulations! You remembered to claim it.",
    "We kept this crate warm for you.",
]

LOOT_CRATE_OPEN_MESSAGES = [
    "You crack open a loot crate...",
    "Let's see what fate has in store.",
    "You unlock the crate and peek inside.",
    "The crate creaks open.",
    "Fingers crossed.",
    "Whatever happens next is between you and fate.",
    "The crate opens. Good luck.",
]

CARD_DROP_MESSAGES = [
    "A mysterious card has appeared!",
    "A new discovery has surfaced.",
    "Fortune has revealed a card.",
    "Something valuable has appeared.",
    "Opportunity knocks. Who will answer?",
    "Finders keepers!",
    "A card has wandered into the chat.",
]

RARE_CARD_DROP_MESSAGES = [
    "A rare find has been spotted!",
    "Something rare is waiting to be claimed.",
]

SNIPE_HIT_MESSAGES = [
    "Bullseye!",
    "Direct hit!",
    "A perfect shot!",
    "Yoink!",
    "Fastest fingers in the west.",
    "Skill issue for everyone else.",
    "Right between the eyes.",
]

SNIPE_MISS_ROTATING_MESSAGES = [
    "Not even close.",
    "The sniper found absolutely nothing.",
    "Wrong place, wrong time.",
    "The sniper checks the area. Nothing.",
    "The target remains one step ahead.",
    "Have you tried opening your eyes?",
    "The target thanks you for checking the wrong spot.",
]

SNIPE_HIDE_SUCCESS_MESSAGES = [
    "Safe... for now.",
    "Your location remains unknown.",
    "The sniper walks right past.",
    "Your hiding spot held strong.",
    "Even we're surprised they didn't find you.",
    "The sniper needs glasses.",
    "Somehow, it worked.",
    "You're either lucky or invisible.",
    "Hide and seek champion.",
]

SNIPE_FOUND_MESSAGES = [
    "Your hiding place has been compromised.",
    "Your cover is blown.",
    "The sniper found their mark.",
    "The sniper found you!",
    "You really thought that would work?",
    "The sniper found you immediately.",
    "The bushes sold you out.",
    "Hiding is harder than it looks.",
    "You got caught in 4K.",
]

EVENT_CARD_LOCKED_MESSAGE = "This event card belongs to a chosen few."
COLLECTION_COMPLETE_TEXT_TEMPLATE = "{emoji} ᴄᴏʟʟᴇᴄᴛɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇ! ʏᴏᴜ ᴄᴏᴍᴘʟᴇᴛᴇᴅ sᴇᴛ {set_name}. ᴘʟᴇᴀsᴇ ᴏᴘᴇɴ ᴀ ᴛɪᴄᴋᴇᴛ ᴛᴏ ᴄʟᴀɪᴍ ʏᴏᴜʀ ʀᴇᴡᴀʀᴅ! {ticket_channel}"
OWNER_PROTECTION_MESSAGES = [
    "{target} SHOULD have been muted. Discord chose peace instead of violence.",
    "{target} was eliminated spiritually because Discord refused the paperwork.",
    "Direct hit on {target}! Unfortunately, Discord said 'absolutely not.'",
    "{target} got saved by corporate intervention. Booo!",
]

SNIPE_SUCCESS_MESSAGES = [
    "{message} {target}",
]

SNIPE_MISS_MESSAGES = [
    "{message} {target}",
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
            ALTER TABLE cards
            ADD COLUMN IF NOT EXISTS custom_type TEXT;
        """)
        await conn.execute("""
            ALTER TABLE cards
            ADD COLUMN IF NOT EXISTS event_name TEXT;
        """)
        await conn.execute("""
            ALTER TABLE cards
            ADD COLUMN IF NOT EXISTS is_event_card BOOLEAN NOT NULL DEFAULT FALSE;
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
            ADD COLUMN IF NOT EXISTS staff_log_channel_id BIGINT;
        """)
        await conn.execute("""
            ALTER TABLE server_settings
            ADD COLUMN IF NOT EXISTS admin_role_id BIGINT;
        """)
        await conn.execute("""
            ALTER TABLE server_settings
            ADD COLUMN IF NOT EXISTS mod_role_id BIGINT;
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
            CREATE TABLE IF NOT EXISTS rarity_settings (
                guild_id BIGINT PRIMARY KEY,
                common_chance INTEGER NOT NULL DEFAULT 70,
                rare_chance INTEGER NOT NULL DEFAULT 20,
                epic_chance INTEGER NOT NULL DEFAULT 8,
                legendary_chance INTEGER NOT NULL DEFAULT 2,
                custom_chance INTEGER NOT NULL DEFAULT 0
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS event_settings (
                guild_id BIGINT PRIMARY KEY,
                event_name TEXT DEFAULT 'Untitled Event',
                event_theme TEXT DEFAULT 'No theme set',
                event_launched BOOLEAN NOT NULL DEFAULT FALSE,
                event_type TEXT DEFAULT 'Custom',
                event_only_drops BOOLEAN NOT NULL DEFAULT FALSE,
                event_boosts_enabled BOOLEAN NOT NULL DEFAULT FALSE
            );
        """)
        await conn.execute("""
            ALTER TABLE event_settings
            ADD COLUMN IF NOT EXISTS event_card_chance INTEGER NOT NULL DEFAULT 10;
        """)

        await conn.execute("""
            ALTER TABLE event_settings
            ADD COLUMN IF NOT EXISTS event_type TEXT DEFAULT 'Custom';
        """)
        await conn.execute("""
            ALTER TABLE event_settings
            ADD COLUMN IF NOT EXISTS event_only_drops BOOLEAN NOT NULL DEFAULT FALSE;
        """)
        await conn.execute("""
            ALTER TABLE event_settings
            ADD COLUMN IF NOT EXISTS event_boosts_enabled BOOLEAN NOT NULL DEFAULT FALSE;
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

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS card_sets (
                id SERIAL PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                name TEXT NOT NULL,
                reward_text TEXT DEFAULT 'Open a ticket to claim your reward.',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (guild_id, name)
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS card_set_cards (
                set_id INTEGER NOT NULL REFERENCES card_sets(id) ON DELETE CASCADE,
                card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
                PRIMARY KEY (set_id, card_id)
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS completed_card_sets (
                guild_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                set_id INTEGER NOT NULL REFERENCES card_sets(id) ON DELETE CASCADE,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, user_id, set_id)
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS collection_settings (
                guild_id BIGINT PRIMARY KEY,
                ticket_channel_id BIGINT,
                completion_emoji TEXT DEFAULT '🎉'
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

async def get_admin_role(guild_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT admin_role_id FROM server_settings WHERE guild_id=$1",
            guild_id
        )

async def set_admin_role_db(guild_id, role_id):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO server_settings (guild_id, admin_role_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET admin_role_id=$2
        """, guild_id, role_id)

async def get_mod_role(guild_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT mod_role_id FROM server_settings WHERE guild_id=$1",
            guild_id
        )

async def set_mod_role_db(guild_id, role_id):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO server_settings (guild_id, mod_role_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET mod_role_id=$2
        """, guild_id, role_id)

async def get_staff_log_channel(guild_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT staff_log_channel_id FROM server_settings WHERE guild_id=$1",
            guild_id
        )

async def set_staff_log_channel_db(guild_id, channel_id):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO server_settings (guild_id, staff_log_channel_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET staff_log_channel_id=$2
        """, guild_id, channel_id)

async def send_staff_log(guild, title, description, color=None):
    if not guild:
        return False

    channel_id = await get_staff_log_channel(guild.id)

    if not channel_id:
        return False

    channel = guild.get_channel(channel_id) or bot.get_channel(channel_id)

    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as e:
            print(f"Could not fetch staff log channel {channel_id}: {e}")
            return False

    embed = discord.Embed(
        title=title,
        description=description,
        color=color or discord.Color.from_str("#9e659d")
    )
    embed.timestamp = discord.utils.utcnow()

    try:
        await channel.send(embed=embed)
        return True
    except Exception as e:
        print(f"Could not send staff log: {e}")
        return False

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

async def get_rarity_settings(guild_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT common_chance, rare_chance, epic_chance, legendary_chance, custom_chance
            FROM rarity_settings
            WHERE guild_id=$1
        """, guild_id)

        if not row:
            await conn.execute("""
                INSERT INTO rarity_settings (guild_id, common_chance, rare_chance, epic_chance, legendary_chance, custom_chance)
                VALUES ($1, 70, 20, 8, 2, 0)
                ON CONFLICT (guild_id) DO NOTHING
            """, guild_id)

            return {
                "common_chance": 70,
                "rare_chance": 20,
                "epic_chance": 8,
                "legendary_chance": 2,
                "custom_chance": 0,
            }

        return dict(row)

async def set_rarity_setting_db(guild_id, column, value: int):
    allowed_columns = {
        "common_chance",
        "rare_chance",
        "epic_chance",
        "legendary_chance",
    }

    if column not in allowed_columns:
        raise ValueError("Invalid rarity setting.")

    await get_rarity_settings(guild_id)

    async with db_pool.acquire() as conn:
        await conn.execute(
            f"UPDATE rarity_settings SET {column}=$1 WHERE guild_id=$2",
            value,
            guild_id
        )

def choose_rarity_from_settings(settings, allowed_rarities=None):
    weights = {
        "Common": int(settings.get("common_chance", 70)),
        "Rare": int(settings.get("rare_chance", 20)),
        "Epic": int(settings.get("epic_chance", 8)),
        "Legendary": int(settings.get("legendary_chance", 2)),
    }

    if allowed_rarities is not None:
        weights = {rarity: weight for rarity, weight in weights.items() if rarity in allowed_rarities}

    weights = {rarity: max(0, weight) for rarity, weight in weights.items()}

    if not weights or sum(weights.values()) <= 0:
        fallback = allowed_rarities[0] if allowed_rarities else "Common"
        return fallback

    return random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]

async def choose_drop_card(cards, guild_id):
    if not cards:
        return None

    event_settings = await get_event_settings(guild_id)
    event_drops_on = bool(event_settings.get("event_only_drops", False) or event_settings.get("event_launched", False))
    event_chance = int(event_settings.get("event_card_chance", 10))

    event_cards = [
        card for card in cards
        if bool(get_record_value(card, "is_event_card", False))
    ]

    normal_cards = [
        card for card in cards
        if not bool(get_record_value(card, "is_event_card", False)) and card["rarity"] != "Custom"
    ]

    if event_drops_on and event_cards and random.randint(1, 100) <= event_chance:
        return random.choice(event_cards)

    if normal_cards:
        return await choose_card_from_pool(normal_cards, guild_id)

    return random.choice(cards)

async def choose_card_from_pool(cards, guild_id=None):
    if not cards:
        return None

    if not guild_id:
        return random.choice(cards)

    rarity_settings = await get_rarity_settings(guild_id)
    normal_cards = [
        card for card in cards
        if card["rarity"] != "Custom" and not bool(get_record_value(card, "is_event_card", False))
    ]

    if normal_cards:
        cards = normal_cards

    available_rarities = sorted(set(card["rarity"] for card in cards))

    for _ in range(12):
        chosen_rarity = choose_rarity_from_settings(rarity_settings, available_rarities)
        rarity_cards = [card for card in cards if card["rarity"] == chosen_rarity]

        if rarity_cards:
            return random.choice(rarity_cards)

    return random.choice(cards)

def choose_drop_message(rarity):
    if rarity in ("Rare", "Epic", "Legendary", "Custom") and random.randint(1, 100) <= 45:
        return random.choice(RARE_CARD_DROP_MESSAGES)

    return random.choice(CARD_DROP_MESSAGES)

async def get_event_settings(guild_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT event_name, event_theme, event_launched, event_type, event_only_drops, event_boosts_enabled FROM event_settings WHERE guild_id=$1",
            guild_id
        )
        if not row:
            await conn.execute("""
                INSERT INTO event_settings (guild_id, event_name, event_theme, event_launched, event_type, event_only_drops, event_boosts_enabled)
                VALUES ($1, 'Untitled Event', 'No theme set', FALSE, 'Custom', FALSE, FALSE)
                ON CONFLICT (guild_id) DO NOTHING
            """, guild_id)
            return {
                "event_name": "Untitled Event",
                "event_theme": "No theme set",
                "event_launched": False,
                "event_type": "Custom",
                "event_only_drops": False,
                "event_boosts_enabled": False
            }
        return dict(row)

async def set_event_card_chance_db(guild_id, chance: int):
    chance = max(0, min(100, int(chance)))
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO event_settings (guild_id, event_card_chance)
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET event_card_chance=$2
        """, guild_id, chance)

async def set_event_setting_db(guild_id, column, value):
    allowed_columns = {
        "event_name",
        "event_theme",
        "event_launched",
        "event_type",
        "event_only_drops",
        "event_boosts_enabled"
    }

    if column not in allowed_columns:
        raise ValueError("Invalid event setting.")

    await get_event_settings(guild_id)

    async with db_pool.acquire() as conn:
        await conn.execute(f"UPDATE event_settings SET {column}=$1 WHERE guild_id=$2", value, guild_id)

async def reset_event_settings_db(guild_id):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO event_settings (guild_id, event_name, event_theme, event_launched, event_type, event_only_drops, event_boosts_enabled)
            VALUES ($1, 'Untitled Event', 'No theme set', FALSE, 'Custom', FALSE, FALSE)
            ON CONFLICT (guild_id)
            DO UPDATE SET
                event_name='Untitled Event',
                event_theme='No theme set',
                event_launched=FALSE,
                event_type='Custom',
                event_only_drops=FALSE,
                event_boosts_enabled=FALSE
        """, guild_id)

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
        "Custom": discord.Color.from_str("#ff2ea6"),
    }.get(rarity, discord.Color.blurple())

def format_coins(amount: int):
    return f"{CURRENCY_EMOJI} {amount:,}"

def cooldown_ready_timestamp(last_used, cooldown_seconds):
    return int(last_used) + int(cooldown_seconds)

def cooldown_ready_text(last_used, cooldown_seconds):
    return f"<t:{cooldown_ready_timestamp(last_used, cooldown_seconds)}:R>"

def format_cooldown_timestamp(last_used, cooldown_seconds):
    ready_at = int(last_used) + int(cooldown_seconds)
    return f"<t:{ready_at}:R>"

def eastern_day_number():
    now = datetime.now(ZoneInfo("America/New_York"))
    return int(now.strftime("%Y%m%d"))

async def get_event_reward_multiplier(guild_id):
    if not guild_id:
        return 1.0

    settings = await get_event_settings(guild_id)

    if settings["event_launched"] and settings["event_boosts_enabled"]:
        return 1 + (EVENT_REWARD_BOOST_PERCENT / 100)

    return 1.0

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
                price_text = f" **{format_coins(item['price'])}**"
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
        details = f"**Price:** **{format_coins(item['price'])}**\n"
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
            lines.append(f"{CURRENCY_EMOJI} **{price:,}**")

            for row in grouped[price]:
                lines.append(f"{BULLET_EMOJI} {row['title']}")

            lines.append("")

        details = "\n".join(lines).strip()
        details += "\n\nUse `/buy` and choose `Special Title` to purchase."

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
            lines.append(f"**{format_coins(price)}**")
            lines.append("")

            items = [f"{row['emoji']} `{row['name']}`" for row in grouped[price]]

            for index in range(0, len(items), 2):
                pair = "      ".join(items[index:index + 2])
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

def plain_card_label(card):
    return f"ID {card['id']} • {card['name']}"

def plain_card_label_with_rarity(card):
    return f"ID {card['id']} • {card['name']} ({format_card_type_public(card)})"

def card_label(card):
    return f"**ID:** `{card['id']}` {card['name']} ({format_card_type_public(card)})"

def format_card_line(card, amount=None, limited_note=""):
    amount_text = f" x{amount}" if amount is not None else ""
    return f"**ID:** `{card['id']}` {card['name']} ({card['rarity']}){amount_text}{limited_note}"

def get_record_value(record, key, default=None):
    try:
        if key in record:
            return record[key]
    except Exception:
        pass
    return default

def format_card_type(card):
    rarity = get_record_value(card, "rarity", "Unknown")
    custom_type = get_record_value(card, "custom_type")
    if rarity == "Custom" and custom_type:
        return f"Custom • {custom_type}"
    return rarity

def format_card_type_public(card):
    rarity = get_record_value(card, "rarity", "Unknown")
    custom_type = get_record_value(card, "custom_type")

    if rarity == "Custom":
        if custom_type:
            return f"Limited • {custom_type}"
        return "Limited"

    return rarity

def display_rarity_name(rarity):
    return "Limited" if rarity == "Custom" else rarity

def trade_card_display(card):
    return f"**{card['name']}**\n**ID:** `{card['id']}`\n**Rarity:** {format_card_type_public(card)}"

def trade_card_inline(card):
    return f"**{card['name']}** (**ID:** `{card['id']}`)"

def clean_card_ref(card_ref: str):
    return card_ref.strip().replace("#", "").replace("ID", "").replace("id", "").strip()

def create_card_embed(card):
    card_type = format_card_type(card)
    drop_message = choose_drop_message(card["rarity"])

    embed = discord.Embed(
        title=f"{format_card_type_public(card)} Card Drop!",
        description=f"{drop_message}\n\n**{card['name']}** appeared!\n**ID:** `{card['id']}`",
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

async def get_event_active_cards():
    async with db_pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM cards WHERE is_active = TRUE AND rarity = 'Custom' ORDER BY id"
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

async def get_active_boosts(user_id):
    now = int(time.time())

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT boost_type, expires_at FROM user_boosts WHERE user_id=$1 AND expires_at>$2 ORDER BY expires_at",
            user_id,
            now
        )

    return rows

def format_active_boosts(rows):
    if not rows:
        return "None active"

    names = {
        "daily": f"{DAILY_BOOST_EMOJI} Daily Boost",
        "weekly": f"{WEEKLY_BOOST_EMOJI} Weekly Boost",
        "luck": f"{LUCK_BOOST_EMOJI} Luck Boost",
    }

    lines = []

    for row in rows:
        boost_name = names.get(row["boost_type"], row["boost_type"].title())
        lines.append(f"{BULLET_EMOJI} **{boost_name}** until <t:{int(row['expires_at'])}:R>")

    return "\n".join(lines)

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

async def clear_user_custom_emoji(user_id):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM user_custom_emojis WHERE user_id=$1", user_id)

async def clear_user_title(user_id):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM user_titles WHERE user_id=$1", user_id)

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
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT id, emoji FROM profile_emojis WHERE LOWER(name)=LOWER($1)",
                name
            )

            result = await conn.execute(
                "UPDATE profile_emojis SET is_active=FALSE WHERE LOWER(name)=LOWER($1)",
                name
            )

            if row:
                for query, value in [
                    ("DELETE FROM user_owned_profile_emojis WHERE profile_emoji_id=$1", row["id"]),
                    ("DELETE FROM user_custom_emojis WHERE emoji=$1", row["emoji"]),
                ]:
                    try:
                        await conn.execute(query, value)
                    except Exception:
                        pass

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
        async with conn.transaction():
            result = await conn.execute(
                "UPDATE shop_titles SET is_active=FALSE WHERE LOWER(title)=LOWER($1)",
                title
            )

            for query in [
                "DELETE FROM user_titles WHERE LOWER(title)=LOWER($1)",
                "DELETE FROM user_owned_titles WHERE LOWER(title)=LOWER($1)"
            ]:
                try:
                    await conn.execute(query, title)
                except Exception:
                    pass

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
        app_commands.Choice(name=plain_card_label(card), value=str(card["id"]))
        for card in cards
        if current.lower() in card_label(card).lower()
    ][:25]

async def sell_cards_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_user_owned_cards_for_sell(interaction.user.id)
    return [
        app_commands.Choice(name=plain_card_label(card), value=str(card["id"]))
        for card in cards
        if current.lower() in card_label(card).lower()
    ][:25]

async def all_active_cards_autocomplete(interaction: discord.Interaction, current: str):
    cards = await get_active_cards()
    return [
        app_commands.Choice(name=plain_card_label(card), value=str(card["id"]))
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
        await notify_completed_sets(interaction, uid)
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
def create_trade_result_embed(status, requester, target, requester_card, target_card):
    if status == "accepted":
        return discord.Embed(
            title="<:Accept:1514062817815171175> Trade Accepted",
            description=(
                f"**{requester.display_name}** traded **{requester_card}**\n"
                f"**{target.display_name}** traded **{target_card}**"
            ),
            color=discord.Color.green()
        )

    return discord.Embed(
        title="<:Decline:1514062765956927618> Trade Declined",
        description=(
            f"**{target.display_name}** declined the trade request.\n\n"
            f"**Offered:** {requester_card}\n"
            f"**Requested:** {target_card}"
        ),
        color=discord.Color.red()
    )

class TradeView(discord.ui.View):
    def __init__(self, requester, target, your_card, their_card):
        super().__init__(timeout=120)
        self.requester = requester
        self.target = target
        self.your_card = your_card
        self.their_card = their_card
        self.your_card_name = str(your_card)
        self.their_card_name = str(their_card)
        self.finished = False

    def clear_active_trade_cards(self):
        active_trade_card_ids.discard(self.your_card["id"])
        active_trade_card_ids.discard(self.their_card["id"])

    def create_embed(self):
        embed = discord.Embed(
            title="Trade Request",
            description=f"{self.requester.mention} wants to trade with {self.target.mention}.",
            color=discord.Color.from_str("#9e659d")
        )

        embed.add_field(
            name=f"{self.requester.display_name} is offering",
            value=trade_card_display(self.your_card),
            inline=True
        )

        embed.add_field(
            name=f"{self.target.display_name} would give",
            value=trade_card_display(self.their_card),
            inline=True
        )

        embed.set_footer(text=f"{self.target.display_name} can accept or decline this trade.")
        return embed

    def completed_embed(self):
        embed = discord.Embed(
            title="<:Accept:1514062817815171175> 𝗧𝗥𝗔𝗗𝗘 𝗔𝗖𝗖𝗘𝗣𝗧𝗘𝗗",
            description=(
                f"**{self.requester.display_name}** gave:\n"
                f"{trade_card_display(self.your_card)}\n\n"
                f"**{self.target.display_name}** gave:\n"
                f"{trade_card_display(self.their_card)}"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="The cards have been exchanged successfully.")
        return embed

    
    def declined_embed(self):
        embed = discord.Embed(
            title="<:Decline:1514062765956927618> 𝗧𝗥𝗔𝗗𝗘 𝗗𝗘𝗖𝗟𝗜𝗡𝗘𝗗",
            description=(
                f"**{self.target.display_name}** declined this trade.\n\n"
                f"**Offered:**\n{trade_card_display(self.your_card)}\n\n"
                f"**Requested:**\n{trade_card_display(self.their_card)}"
            ),
            color=discord.Color.red()
        )
        return embed

    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "Only the person receiving this trade can accept or decline it.",
                ephemeral=True
            )
            return False

        if self.finished:
            await interaction.response.send_message(
                "This trade is already finished.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        success, msg = await trade_cards(
            self.requester.id,
            self.your_card["id"],
            self.target.id,
            self.their_card["id"]
        )

        self.finished = True
        self.clear_active_trade_cards()

        for child in self.children:
            child.disabled = True

        if not success:
            embed = discord.Embed(
                title="Trade Failed",
                description=msg,
                color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, view=self)

        await add_daily_limit_usage(self.requester.id, "trade", count_add=1)
        await add_daily_limit_usage(self.target.id, "trade", count_add=1)

        await notify_completed_sets(interaction, self.requester.id)
        await notify_completed_sets(interaction, self.target.id)

        await interaction.edit_original_response(embed=self.completed_embed(), view=self)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.finished = True
        self.clear_active_trade_cards()

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=self.declined_embed(), view=self)

    async def on_timeout(self):
        if self.finished:
            return

        self.finished = True
        self.clear_active_trade_cards()

        for child in self.children:
            child.disabled = True

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

        await send_staff_log(
            interaction.guild,
            "Card Removed From Drops",
            f"**Card:** {self.card['name']}\n**ID:** `{self.card['id']}`\n**Rarity:** {self.card['rarity']}\n**Custom Type:** {get_record_value(self.card, 'custom_type') or 'None'}\n**Removed by:** {interaction.user.mention}",
            discord.Color.red()
        )

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

        await send_staff_log(
            interaction.guild,
            "Economy Setting Updated",
            f"**Setting:** {self.setting_key}\n**New value:** {value:,}\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

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

        await send_staff_log(
            interaction.guild,
            "Crate Setting Updated",
            f"**Setting:** {self.setting_key}\n**New value:** {value:,}\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

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

async def get_status_snapshot(guild_id):
    async def safe_call(coro, default):
        try:
            return await coro
        except Exception:
            return default

    drop_settings = await safe_call(get_drop_settings(guild_id), {})
    rarity_settings = await safe_call(get_rarity_settings(guild_id), {})
    economy_settings = await safe_call(get_economy_settings(guild_id), {})
    crate_settings = await safe_call(get_crate_settings(guild_id), {})
    event_settings = await safe_call(get_event_settings(guild_id), {})
    collection_settings = await safe_call(get_collection_settings(guild_id), {})

    counts = {
        "cards_total": 0,
        "cards_active": 0,
        "event_cards": 0,
        "sets_active": 0,
        "titles_active": 0,
        "profile_emojis_active": 0,
        "drop_channels": 0,
    }

    drop_channels = []

    try:
        async with db_pool.acquire() as conn:
            try:
                counts["cards_total"] = await conn.fetchval("SELECT COUNT(*) FROM cards") or 0
            except Exception:
                pass

            try:
                counts["cards_active"] = await conn.fetchval("SELECT COUNT(*) FROM cards WHERE is_active=TRUE") or 0
            except Exception:
                pass

            try:
                counts["event_cards"] = await conn.fetchval("SELECT COUNT(*) FROM cards WHERE is_event_card=TRUE") or 0
            except Exception:
                pass

            try:
                counts["sets_active"] = await conn.fetchval("SELECT COUNT(*) FROM card_sets WHERE guild_id=$1 AND is_active=TRUE", guild_id) or 0
            except Exception:
                pass

            try:
                counts["titles_active"] = await conn.fetchval("SELECT COUNT(*) FROM shop_titles WHERE is_active=TRUE") or 0
            except Exception:
                pass

            try:
                counts["profile_emojis_active"] = await conn.fetchval("SELECT COUNT(*) FROM profile_emojis WHERE is_active=TRUE") or 0
            except Exception:
                pass

            try:
                rows = await conn.fetch("SELECT channel_id FROM drop_channels WHERE guild_id=$1 ORDER BY channel_id", guild_id)
                drop_channels = [row["channel_id"] for row in rows]
                counts["drop_channels"] = len(drop_channels)
            except Exception:
                pass
    except Exception:
        pass

    return {
        "drop": drop_settings,
        "rarity": rarity_settings,
        "economy": economy_settings,
        "crate": crate_settings,
        "event": event_settings,
        "collection": collection_settings,
        "counts": counts,
        "drop_channels": drop_channels,
    }

def format_status_channel(channel_id):
    if not channel_id:
        return "Not set"
    return f"<#{channel_id}>"

def format_status_role(role_id):
    if not role_id:
        return "Not set"
    return f"<@&{role_id}>"

async def build_bot_status_lines(guild_id):
    status = await get_status_snapshot(guild_id)
    drop = status["drop"]
    rarity = status["rarity"]
    economy = status["economy"]
    crate = status["crate"]
    event = status["event"]
    collection = status["collection"]
    counts = status["counts"]

    staff_role = drop.get("staff_role_id") or drop.get("staff_role") or drop.get("staff_roleid")
    mod_role = drop.get("mod_role_id") or drop.get("moderator_role_id") or drop.get("mod_role")
    admin_role = drop.get("admin_role_id") or drop.get("admin_role")

    rarity_total = (
        int(rarity.get("common_chance", 0))
        + int(rarity.get("rare_chance", 0))
        + int(rarity.get("epic_chance", 0))
        + int(rarity.get("legendary_chance", 0))
    )

    return (
        f"**Bot:** Online\\n"
        f"**Admin Role:** {format_status_role(admin_role)}\\n"
        f"**Mod Role:** {format_status_role(mod_role)}\\n"
        f"**Staff Role:** {format_status_role(staff_role)}\\n"
        f"**Staff Log:** {format_status_channel(drop.get('staff_log_channel_id'))}\\n"
        f"**Ticket Channel:** {format_status_channel(collection.get('ticket_channel_id'))}\\n"
        f"**Drop Channels:** {counts['drop_channels']}\\n"
        f"**Cards:** {counts['cards_active']} active / {counts['cards_total']} total\\n"
        f"**Event Cards:** {counts['event_cards']}\\n"
        f"**Active Sets:** {counts['sets_active']}\\n"
        f"**Shop Titles:** {counts['titles_active']}\\n"
        f"**Profile Emojis:** {counts['profile_emojis_active']}\\n"
        f"**Auto Drops:** {drop.get('auto_drop_minutes', 'N/A')}m at {drop.get('auto_drop_chance', 'N/A')}%\\n"
        f"**Claim Cooldown:** {drop.get('claim_cooldown_seconds', 'N/A')}s\\n"
        f"**Rarity Total:** {rarity_total}/100\\n"
        f"**Economy:** Daily {economy.get('daily_min', 'N/A')}-{economy.get('daily_max', 'N/A')} | Weekly {economy.get('weekly_min', 'N/A')}-{economy.get('weekly_max', 'N/A')}\\n"
        f"**Crates:** Regular {crate.get('regular_crate_min', 'N/A')}-{crate.get('regular_crate_max', 'N/A')} | Legendary {crate.get('legendary_crate_min', 'N/A')}-{crate.get('legendary_crate_max', 'N/A')}\\n"
        f"**Event:** {event.get('event_name', 'No Event')} — {event.get('event_theme', 'None')}\\n"
        f"**Launched:** {format_on_off(event.get('event_launched', False))}\\n"
        f"**Event Drops:** {format_on_off(event.get('event_only_drops', False))}\\n"
        f"**Event Boosts:** {format_on_off(event.get('event_boosts_enabled', False))}\\n"
        f"**Event Card Chance:** {event.get('event_card_chance', 10)}%"
    )

async def create_settings_embed(guild_id, section="status"):
    snapshot = await get_settings_snapshot(guild_id)
    titles = {
        "status": "Settings Status",
        "drops": "Drops Settings",
        "rarity": "Rarity Settings",
        "economy": "Economy Settings",
        "crates": "Crate Settings",
        "events": "Event Settings",
        "collections": "Collection Settings",
    }

    embed = discord.Embed(
        title=titles.get(section, "Settings"),
        color=discord.Color.from_str("#9e659d")
    )

    if section == "status":
        embed.description = "Use the dropdown to view each section."
        status = await get_status_snapshot(guild_id)
        drop = status["drop"]
        rarity = status["rarity"]
        economy = status["economy"]
        crate = status["crate"]
        event = status["event"]
        collection = status["collection"]
        counts = status["counts"]
        drop_channels = status["drop_channels"]

        staff_role = drop.get("staff_role_id") or drop.get("staff_role") or drop.get("staff_roleid")
        mod_role = drop.get("mod_role_id") or drop.get("moderator_role_id") or drop.get("mod_role")
        admin_role = drop.get("admin_role_id") or drop.get("admin_role")

        rarity_total = (
            int(rarity.get("common_chance", 0))
            + int(rarity.get("rare_chance", 0))
            + int(rarity.get("epic_chance", 0))
            + int(rarity.get("legendary_chance", 0))
        )

        if drop_channels:
            drop_channel_text = ", ".join(f"<#{channel_id}>" for channel_id in drop_channels[:8])
            if len(drop_channels) > 8:
                drop_channel_text += f" +{len(drop_channels) - 8} more"
        else:
            drop_channel_text = "Not set"

        embed.add_field(
            name="Roles",
            value=(
                f"**Admin:** {format_status_role(admin_role)}\n"
                f"**Mod:** {format_status_role(mod_role)}\n"
                f"**Staff:** {format_status_role(staff_role)}"
            ),
            inline=False
        )
        embed.add_field(
            name="Channels",
            value=(
                f"**Staff Log:** {format_status_channel(drop.get('staff_log_channel_id'))}\n"
                f"**Ticket:** {format_status_channel(collection.get('ticket_channel_id'))}\n"
                f"**Drops:** {drop_channel_text}"
            ),
            inline=False
        )
        embed.add_field(
            name="Drops",
            value=(
                f"**Auto Drops:** Every {drop.get('auto_drop_minutes', 'N/A')} minutes\n"
                f"**Drop Chance:** {drop.get('auto_drop_chance', 'N/A')}%\n"
                f"**Claim Cooldown:** {drop.get('claim_cooldown_seconds', 'N/A')} seconds"
            ),
            inline=False
        )
        embed.add_field(
            name="Cards & Shop",
            value=(
                f"**Cards:** {counts['cards_active']} active / {counts['cards_total']} total\n"
                f"**Event Cards:** {counts['event_cards']}\n"
                f"**Active Sets:** {counts['sets_active']}\n"
                f"**Titles:** {counts['titles_active']}\n"
                f"**Profile Emojis:** {counts['profile_emojis_active']}"
            ),
            inline=False
        )
        embed.add_field(
            name="Rarity",
            value=(
                f"**Total:** {rarity_total}/100\n"
                f"**Common:** {rarity.get('common_chance', 'N/A')}\n"
                f"**Rare:** {rarity.get('rare_chance', 'N/A')}\n"
                f"**Epic:** {rarity.get('epic_chance', 'N/A')}\n"
                f"**Legendary:** {rarity.get('legendary_chance', 'N/A')}"
            ),
            inline=False
        )
        embed.add_field(
            name="Economy & Crates",
            value=(
                f"**Daily:** {economy.get('daily_min', 'N/A')} - {economy.get('daily_max', 'N/A')} Sancs\n"
                f"**Weekly:** {economy.get('weekly_min', 'N/A')} - {economy.get('weekly_max', 'N/A')} Sancs\n"
                f"**Regular Crate:** {crate.get('regular_crate_min', 'N/A')} - {crate.get('regular_crate_max', 'N/A')} Sancs\n"
                f"**Legendary Crate:** {crate.get('legendary_crate_min', 'N/A')} - {crate.get('legendary_crate_max', 'N/A')} Sancs"
            ),
            inline=False
        )
        embed.add_field(
            name="Event",
            value=(
                f"**Name:** {event.get('event_name', 'No Event')}\n"
                f"**Theme:** {event.get('event_theme', 'None')}\n"
                f"**Launched:** {format_on_off(event.get('event_launched', False))}\n"
                f"**Event Drops:** {format_on_off(event.get('event_only_drops', False))}\n"
                f"**Event Boosts:** {format_on_off(event.get('event_boosts_enabled', False))}\n"
                f"**Event Card Chance:** {event.get('event_card_chance', 10)}%"
            ),
            inline=False
        )

    elif section in SETTING_OPTIONS:
        lines = []

        for key, meta in SETTING_OPTIONS[section]["items"].items():
            current = get_setting_current_value(snapshot, key, meta["kind"])
            lines.append(f"**{meta['label']}:** {current}{meta['suffix']}")

        embed.description = "\n".join(lines)

        if section == "rarity":
            embed.set_footer(text="Common, Rare, Epic, and Legendary should total 100.")
        else:
            embed.set_footer(text="Use the edit dropdown below to change these values.")

    elif section == "events":
        event = snapshot["event"]
        embed.description = (
            f"**Name:** {event['event_name']}\n"
            f"**Theme:** {event['event_theme']}\n"
            f"**Type:** {event['event_type']}\n"
            f"**Launched:** {format_on_off(event['event_launched'])}\n"
            f"**Event Drops:** {format_on_off(event['event_only_drops'])}\n"
            f"**Event Boosts:** {format_on_off(event['event_boosts_enabled'])}\n"
            f"**Event Card Chance:** {event.get('event_card_chance', 10)}%"
        )
        embed.set_footer(text="Use /eventsetup for event name/theme/launch controls.")

    elif section == "collections":
        collection = snapshot["collection"]
        ticket = f"<#{collection['ticket_channel_id']}>" if collection.get("ticket_channel_id") else "Not set"
        embed.description = (
            f"**Ticket Channel:** {ticket}\n"
            f"**Completion Emoji:** {collection.get('completion_emoji') or '🎉'}"
        )
        embed.set_footer(text="Use /collectionsetup for collection controls.")

    return embed

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

        await send_staff_log(
            interaction.guild,
            "Settings Updated: Snipe Cooldown",
            f"**New value:** {minutes} minutes\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

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

        await send_staff_log(
            interaction.guild,
            "Settings Updated: Snipe Mute Time",
            f"**New value:** {minutes} minutes\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

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

        await send_staff_log(
            interaction.guild,
            "Settings Updated: Auto Drop Interval",
            f"**New value:** {minutes} minutes\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

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

        await send_staff_log(
            interaction.guild,
            "Settings Updated: Auto Drop Chance",
            f"**New value:** {chance}%\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

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

        await send_staff_log(
            interaction.guild,
            "Settings Updated: Claim Cooldown",
            f"**New value:** {seconds} seconds\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

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

            await send_staff_log(
                interaction.guild,
                "Settings Updated: Auto Drops",
                f"**New value:** {'Enabled' if new_value else 'Disabled'}\n**Updated by:** {interaction.user.mention}",
                discord.Color.from_str("#9e659d")
            )

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
        super().__init__(timeout=300)

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

            await send_staff_log(
                interaction.guild,
                "Settings Updated: Staff Sniping",
                f"**New value:** {'Enabled' if new_value else 'Disabled'}\n**Updated by:** {interaction.user.mention}",
                discord.Color.from_str("#9e659d")
            )

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

class ResetUserConfirmView(discord.ui.View):
    def __init__(self, requester, target):
        super().__init__(timeout=60)
        self.requester = requester
        self.target = target
        self.finished = False

    @discord.ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
    async def confirm_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.requester.id:
            return await interaction.response.send_message("Only the admin who started this can confirm.", ephemeral=True)

        if self.finished:
            return await interaction.response.send_message("This reset is already finished.", ephemeral=True)

        async with db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM inventory WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM balances WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM cooldowns WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM daily_streaks WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM loot_crates WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM user_boosts WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM user_titles WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM user_custom_emojis WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM user_owned_profile_emojis WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM user_owned_titles WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM snipe_items WHERE user_id=$1", self.target.id)
                await conn.execute("DELETE FROM user_daily_limits WHERE user_id=$1", self.target.id)

        self.finished = True

        for child in self.children:
            child.disabled = True

        await send_staff_log(
            interaction.guild,
            "User Reset",
            f"**User:** {self.target.mention}\n**Reset by:** {interaction.user.mention}",
            discord.Color.red()
        )

        await interaction.response.edit_message(
            content=f"{self.target.mention}'s bot data has been reset.",
            embed=None,
            view=self
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.requester.id:
            return await interaction.response.send_message("Only the admin who started this can cancel.", ephemeral=True)

        self.finished = True

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content="User reset cancelled.",
            embed=None,
            view=self
        )

async def create_eventsetup_home_embed(guild_id):
    settings = await get_event_settings(guild_id)

    launched_text = f"{TOGGLE_ON_EMOJI} Launched" if settings["event_launched"] else f"{TOGGLE_OFF_EMOJI} Not launched"
    drops_text = f"{TOGGLE_ON_EMOJI} Enabled" if settings["event_only_drops"] else f"{TOGGLE_OFF_EMOJI} Disabled"
    boosts_text = f"{TOGGLE_ON_EMOJI} Enabled" if settings["event_boosts_enabled"] else f"{TOGGLE_OFF_EMOJI} Disabled"

    embed = discord.Embed(
        title="Event Setup",
        description="Set up event details and temporary event behavior.",
        color=discord.Color.from_str("#9e659d")
    )

    embed.add_field(
        name="Current Event",
        value=(
            f"**Name:** {settings['event_name']}\n"
            f"**Theme:** {settings['event_theme']}\n"
            f"**Type:** {settings['event_type']}\n"
            f"**Status:** {launched_text}"
        ),
        inline=False
    )

    embed.add_field(
        name="Event Features",
        value=(
            f"**Event Drops:** {drops_text}\n"
            f"**Event Boosts:** {boosts_text}\n"
            f"**Boost Amount:** +{EVENT_REWARD_BOOST_PERCENT}% to `/daily` and `/weekly` while launched"
        ),
        inline=False
    )

    embed.add_field(
        name="Custom Cards",
        value=(
            "Use `/addcard` with rarity **Custom** and type your own custom type.\n"
            "Examples: `Sabotage`, `Team Buff`, `Curse`, `Reward`, `Immunity`, `Trap`"
        ),
        inline=False
    )

    embed.set_footer(text="Use the dropdown or buttons below to edit this event.")
    return embed

def create_eventsetup_info_embed(category):
    embed = discord.Embed(title=f"Event Setup — {category}", color=discord.Color.from_str("#9e659d"))

    if category == "Custom Cards":
        embed.description = (
            "Custom cards use a typed custom type instead of a fixed dropdown.\n\n"
            "**Examples:**\n"
            f"{BULLET_EMOJI} Sabotage\n"
            f"{BULLET_EMOJI} Team Buff\n"
            f"{BULLET_EMOJI} Curse\n"
            f"{BULLET_EMOJI} Trap\n"
            f"{BULLET_EMOJI} Reward\n"
            f"{BULLET_EMOJI} Immunity\n\n"
            "`/addcard name:Sneak Attack rarity:Custom custom_type:Sabotage image:URL`"
        )
    elif category == "Event Drops":
        embed.description = (
            "When this is enabled and the event is launched, auto drops only pull from **Custom** cards.\n\n"
            "This is useful for:\n"
            f"{BULLET_EMOJI} Tournament-only cards\n"
            f"{BULLET_EMOJI} Sabotage cards\n"
            f"{BULLET_EMOJI} Special themed drops\n"
            f"{BULLET_EMOJI} Limited-time event cards"
        )
    elif category == "Event Boosts":
        embed.description = (
            f"When this is enabled and the event is launched, `/daily` and `/weekly` get a **+{EVENT_REWARD_BOOST_PERCENT}%** reward boost.\n\n"
            "This does not add anything to the shop. It only boosts claim rewards during active events."
        )
    elif category == "Event Types":
        embed.description = (
            "**Suggested event types:**\n"
            f"{BULLET_EMOJI} Seasonal\n"
            f"{BULLET_EMOJI} Mafia Tourney\n"
            f"{BULLET_EMOJI} Team Games\n"
            f"{BULLET_EMOJI} Card Hunt\n"
            f"{BULLET_EMOJI} Custom"
        )
    else:
        embed.description = "Choose a valid event category."

    return embed

class EventTextModal(discord.ui.Modal):
    def __init__(self, setting_key, title, label, placeholder, max_length=100):
        super().__init__(title=title)
        self.setting_key = setting_key
        self.input_value = discord.ui.TextInput(label=label, placeholder=placeholder, min_length=1, max_length=max_length)
        self.add_item(self.input_value)

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can edit event setup.", ephemeral=True)

        value = str(self.input_value).strip()
        await set_event_setting_db(interaction.guild.id, self.setting_key, value)

        await send_staff_log(
            interaction.guild,
            "Event Setting Updated",
            f"**Setting:** {self.setting_key}\n**New value:** {value}\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

        await interaction.response.edit_message(
            embed=await create_eventsetup_home_embed(interaction.guild.id),
            view=EventSetupView()
        )

class EventSetupSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Set Event Name", value="set_name", description="Change the event name"),
            discord.SelectOption(label="Set Event Theme", value="set_theme", description="Change the event theme"),
            discord.SelectOption(label="Set Event Type", value="set_type", description="Seasonal, Mafia Tourney, Team Games, etc."),
            discord.SelectOption(label="Custom Cards Info", value="Custom Cards", description="How custom event cards work"),
            discord.SelectOption(label="Event Drops Info", value="Event Drops", description="How event drops work"),
            discord.SelectOption(label="Event Boosts Info", value="Event Boosts", description="How event boosts work"),
            discord.SelectOption(label="Event Types Info", value="Event Types", description="Suggested event types"),
        ]
        super().__init__(placeholder="Choose an event setup option...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can use event setup.", ephemeral=True)

        choice = self.values[0]

        if choice == "set_name":
            return await interaction.response.send_modal(EventTextModal("event_name", "Set Event Name", "Event name", "Example: Sanction Showdown", 80))
        if choice == "set_theme":
            return await interaction.response.send_modal(EventTextModal("event_theme", "Set Event Theme", "Event theme", "Example: Mafia Night / Disney Chaos", 120))
        if choice == "set_type":
            return await interaction.response.send_modal(EventTextModal("event_type", "Set Event Type", "Event type", "Example: Seasonal / Mafia Tourney / Team Games", 80))

        await interaction.response.edit_message(embed=create_eventsetup_info_embed(choice), view=EventSetupView())

class EventSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(EventSetupSelect())

    @discord.ui.button(label="Launch Event", style=discord.ButtonStyle.success)
    async def launch_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can launch events.", ephemeral=True)

        await set_event_setting_db(interaction.guild.id, "event_launched", True)
        settings = await get_event_settings(interaction.guild.id)

        await send_staff_log(
            interaction.guild,
            "Event Launched",
            f"**Name:** {settings['event_name']}\n**Theme:** {settings['event_theme']}\n**Type:** {settings['event_type']}\n**Launched by:** {interaction.user.mention}",
            discord.Color.green()
        )

        await interaction.response.edit_message(embed=await create_eventsetup_home_embed(interaction.guild.id), view=EventSetupView())

    @discord.ui.button(label="Close Event", style=discord.ButtonStyle.secondary)
    async def close_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can close events.", ephemeral=True)

        await set_event_setting_db(interaction.guild.id, "event_launched", False)

        await send_staff_log(
            interaction.guild,
            "Event Closed",
            f"**Closed by:** {interaction.user.mention}",
            discord.Color.orange()
        )

        await interaction.response.edit_message(embed=await create_eventsetup_home_embed(interaction.guild.id), view=EventSetupView())

    @discord.ui.button(label="Event Drops", style=discord.ButtonStyle.primary)
    async def toggle_event_drops(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can edit event drops.", ephemeral=True)

        settings = await get_event_settings(interaction.guild.id)
        new_value = not settings["event_only_drops"]
        await set_event_setting_db(interaction.guild.id, "event_only_drops", new_value)

        await send_staff_log(
            interaction.guild,
            "Event Drops Updated",
            f"**New value:** {'Enabled' if new_value else 'Disabled'}\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

        await interaction.response.edit_message(embed=await create_eventsetup_home_embed(interaction.guild.id), view=EventSetupView())

    @discord.ui.button(label="Event Boosts", style=discord.ButtonStyle.primary)
    async def toggle_event_boosts(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can edit event boosts.", ephemeral=True)

        settings = await get_event_settings(interaction.guild.id)
        new_value = not settings["event_boosts_enabled"]
        await set_event_setting_db(interaction.guild.id, "event_boosts_enabled", new_value)

        await send_staff_log(
            interaction.guild,
            "Event Boosts Updated",
            f"**New value:** {'Enabled' if new_value else 'Disabled'}\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )

        await interaction.response.edit_message(embed=await create_eventsetup_home_embed(interaction.guild.id), view=EventSetupView())

    @discord.ui.button(label="Reset Event", style=discord.ButtonStyle.danger)
    async def reset_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can reset events.", ephemeral=True)

        await reset_event_settings_db(interaction.guild.id)

        await send_staff_log(
            interaction.guild,
            "Event Reset",
            f"**Reset by:** {interaction.user.mention}\nThis did not delete member inventories, cards, balances, or rewards.",
            discord.Color.red()
        )

        await interaction.response.edit_message(embed=await create_eventsetup_home_embed(interaction.guild.id), view=EventSetupView())

def build_cards_page_embed(grouped_cards, rarity, page, per_page=10):
    cards_for_rarity = grouped_cards.get(rarity, [])
    total_pages = max(1, (len(cards_for_rarity) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))

    start_index = page * per_page
    page_cards = cards_for_rarity[start_index:start_index + per_page]

    if not page_cards:
        description = f"No {display_rarity_name(rarity)} cards are currently obtainable."
    else:
        lines = []
        for card in page_cards:
            lines.append(f"{BULLET_EMOJI} **ID:** `{card['id']}` {card['name']} ({format_card_type_public(card)})")
        description = "\n".join(lines)

    embed = discord.Embed(
        title=f"Currently Obtainable Cards — {display_rarity_name(rarity)}",
        description=description,
        color=get_color(rarity)
    )
    embed.set_footer(text=f"{display_rarity_name(rarity)} page {page + 1}/{total_pages}")
    return embed

class CardRaritySelect(discord.ui.Select):
    def __init__(self, view_ref):
        self.view_ref = view_ref
        options = [
            discord.SelectOption(label="Common", value="Common"),
            discord.SelectOption(label="Rare", value="Rare"),
            discord.SelectOption(label="Epic", value="Epic"),
            discord.SelectOption(label="Legendary", value="Legendary"),
            discord.SelectOption(label="Limited", value="Custom"),
        ]
        super().__init__(placeholder="Jump to a rarity...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view_ref.rarity = self.values[0]
        self.view_ref.page = 0
        await interaction.response.edit_message(embed=self.view_ref.current_embed(), view=self.view_ref)

class CardsPaginationView(discord.ui.View):
    def __init__(self, grouped_cards, rarity="Common"):
        super().__init__(timeout=180)
        self.grouped_cards = grouped_cards
        self.rarity = rarity
        self.page = 0
        self.add_item(CardRaritySelect(self))

    def total_pages(self):
        cards_for_rarity = self.grouped_cards.get(self.rarity, [])
        return max(1, (len(cards_for_rarity) + 9) // 10)

    def current_embed(self):
        return build_cards_page_embed(self.grouped_cards, self.rarity, self.page)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page - 1) % self.total_pages()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page + 1) % self.total_pages()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

def build_inventory_embed(title_text, summary_text, rows, page, per_page=10):
    total_pages = max(1, (len(rows) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))

    start_index = page * per_page
    page_rows = rows[start_index:start_index + per_page]

    if not rows:
        card_text = "No cards yet."
    else:
        card_lines = []
        for r in page_rows:
            limited_note = "" if r["is_active"] else " *(unobtainable)*"
            card_lines.append(f"{BULLET_EMOJI} **ID:** `{r['id']}` {r['name']} ({format_card_type_public(r)}) x{r['amount']}{limited_note}")
        card_text = "\n".join(card_lines)

    embed = discord.Embed(
        title=title_text,
        description=summary_text + "\n**Cards**\n" + card_text,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_thumbnail(url=INVENTORY_ICON_URL)
    embed.set_footer(text=f"Cards page {page + 1}/{total_pages}")
    return embed

class InventoryPaginationView(discord.ui.View):
    def __init__(self, title_text, summary_text, rows):
        super().__init__(timeout=180)
        self.title_text = title_text
        self.summary_text = summary_text
        self.rows = rows
        self.page = 0

    def total_pages(self):
        return max(1, (len(self.rows) + 9) // 10)

    def current_embed(self):
        return build_inventory_embed(self.title_text, self.summary_text, self.rows, self.page)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page - 1) % self.total_pages()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page + 1) % self.total_pages()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

async def active_card_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()
    rows = await get_active_cards()
    choices = []

    for card in rows:
        label = plain_card_label(card)

        if current and current not in label.lower() and current not in str(card["id"]):
            continue

        choices.append(app_commands.Choice(name=label[:100], value=str(card["id"])))

        if len(choices) >= 25:
            break

    return choices

async def profile_emoji_shop_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()
    rows = await get_active_profile_emojis()
    choices = []

    for row in rows:
        label = row["name"]

        if current and current not in row["name"].lower() and current not in str(row["emoji"]).lower():
            continue

        choices.append(app_commands.Choice(name=label[:100], value=str(row["id"])))

        if len(choices) >= 25:
            break

    return choices

async def owned_profile_emoji_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()
    rows = await get_user_owned_profile_emojis(interaction.user.id)
    choices = []

    for row in rows:
        label = row["name"]

        if current and current not in row["name"].lower() and current not in str(row["emoji"]).lower():
            continue

        choices.append(app_commands.Choice(name=label[:100], value=str(row["id"])))

        if len(choices) >= 25:
            break

    return choices

async def shop_title_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()
    rows = await get_active_shop_titles()
    choices = []

    for row in rows:
        label = row["title"]

        if current and current not in row["title"].lower():
            continue

        choices.append(app_commands.Choice(name=label[:100], value=str(row["id"])))

        if len(choices) >= 25:
            break

    return choices

async def owned_title_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()
    titles = await get_user_owned_titles(interaction.user.id)
    choices = []

    for title in titles:
        if current and current not in title.lower():
            continue

        choices.append(app_commands.Choice(name=title[:100], value=title))

        if len(choices) >= 25:
            break

    return choices

async def get_profile_emoji_by_ref(ref):
    ref = str(ref).strip()

    async with db_pool.acquire() as conn:
        if ref.isdigit():
            row = await conn.fetchrow("SELECT * FROM profile_emojis WHERE id=$1", int(ref))
            if row:
                return row

        return await conn.fetchrow(
            "SELECT * FROM profile_emojis WHERE LOWER(name)=LOWER($1) OR emoji=$1",
            ref
        )

async def get_shop_title_by_ref(ref):
    ref = str(ref).strip()

    async with db_pool.acquire() as conn:
        if ref.isdigit():
            row = await conn.fetchrow("SELECT * FROM shop_titles WHERE id=$1", int(ref))
            if row:
                return row

        return await conn.fetchrow(
            "SELECT * FROM shop_titles WHERE LOWER(title)=LOWER($1)",
            ref
        )

async def set_card_event_status(card_id, is_event_card: bool, event_name: str = None):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow("""
            UPDATE cards
            SET is_event_card=$1, event_name=$2
            WHERE id=$3
            RETURNING *
        """, is_event_card, event_name if is_event_card else None, int(card_id))

async def is_event_card_locked_for_user(card, user_id, interaction):
    try:
        is_event = bool(card["is_event_card"])
    except Exception:
        is_event = False

    if not is_event:
        return False

    if await is_staff_member(interaction):
        return False

    return not await user_owns_card(user_id, card["id"])

async def get_collection_settings(guild_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT ticket_channel_id, completion_emoji FROM collection_settings WHERE guild_id=$1",
            guild_id
        )
        if not row:
            await conn.execute("""
                INSERT INTO collection_settings (guild_id, ticket_channel_id, completion_emoji)
                VALUES ($1, NULL, '🎉')
                ON CONFLICT (guild_id) DO NOTHING
            """, guild_id)
            return {"ticket_channel_id": None, "completion_emoji": "🎉"}
        return dict(row)

async def set_collection_ticket_channel_db(guild_id, channel_id):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO collection_settings (guild_id, ticket_channel_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET ticket_channel_id=$2
        """, guild_id, channel_id)

async def set_collection_completion_emoji_db(guild_id, emoji):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO collection_settings (guild_id, completion_emoji)
            VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET completion_emoji=$2
        """, guild_id, emoji)

async def get_card_set_by_ref(guild_id, ref):
    ref = str(ref).strip()
    async with db_pool.acquire() as conn:
        if ref.isdigit():
            row = await conn.fetchrow(
                "SELECT * FROM card_sets WHERE guild_id=$1 AND id=$2 AND is_active=TRUE",
                guild_id, int(ref)
            )
            if row:
                return row
        return await conn.fetchrow(
            "SELECT * FROM card_sets WHERE guild_id=$1 AND LOWER(name)=LOWER($2) AND is_active=TRUE",
            guild_id, ref
        )

async def card_set_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, name FROM card_sets WHERE guild_id=$1 AND is_active=TRUE ORDER BY name",
            interaction.guild.id
        )
    choices = []
    for row in rows:
        if current and current not in row["name"].lower():
            continue
        choices.append(app_commands.Choice(name=row["name"][:100], value=str(row["id"])))
        if len(choices) >= 25:
            break
    return choices

async def get_cards_in_set(set_id):
    async with db_pool.acquire() as conn:
        return await conn.fetch("""
            SELECT cards.*
            FROM card_set_cards
            JOIN cards ON cards.id = card_set_cards.card_id
            WHERE card_set_cards.set_id=$1
            ORDER BY cards.rarity, cards.id
        """, set_id)

async def user_owns_all_cards_in_set(user_id, set_id):
    cards = await get_cards_in_set(set_id)
    if not cards:
        return False, 0, 0
    owned_count = 0
    for card in cards:
        if await user_owns_card(user_id, card["id"]):
            owned_count += 1
    return owned_count == len(cards), owned_count, len(cards)

async def mark_set_completed_once(guild_id, user_id, set_id):
    async with db_pool.acquire() as conn:
        result = await conn.execute("""
            INSERT INTO completed_card_sets (guild_id, user_id, set_id)
            VALUES ($1, $2, $3)
            ON CONFLICT DO NOTHING
        """, guild_id, user_id, set_id)
    return result.endswith("1")

async def notify_completed_sets(interaction, user_id):
    if not interaction or not interaction.guild:
        return

    async with db_pool.acquire() as conn:
        sets = await conn.fetch(
            "SELECT * FROM card_sets WHERE guild_id=$1 AND is_active=TRUE ORDER BY name",
            interaction.guild.id
        )

    if not sets:
        return

    settings = await get_collection_settings(interaction.guild.id)
    ticket_channel = f"<#{settings['ticket_channel_id']}>" if settings.get("ticket_channel_id") else ""
    emoji = settings.get("completion_emoji") or "🎉"

    for card_set in sets:
        complete, owned_count, total_count = await user_owns_all_cards_in_set(user_id, card_set["id"])

        if not complete:
            continue

        is_new = await mark_set_completed_once(interaction.guild.id, user_id, card_set["id"])

        if not is_new:
            continue

        message = COLLECTION_COMPLETE_TEXT_TEMPLATE.format(
            emoji=emoji,
            set_name=card_set["name"],
            ticket_channel=ticket_channel
        ).strip()

        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except Exception:
            try:
                member = interaction.guild.get_member(user_id) or await interaction.guild.fetch_member(user_id)
                await member.send(message)
            except Exception:
                pass

async def event_card_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, name, rarity, custom_type
            FROM cards
            WHERE is_event_card=TRUE
            ORDER BY id
        """)

    choices = []

    for card in rows:
        label = plain_card_label(card)

        if current and current not in label.lower() and current not in str(card["id"]):
            continue

        choices.append(app_commands.Choice(name=label[:100], value=str(card["id"])))

        if len(choices) >= 25:
            break

    return choices

async def settings_choice_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()
    options = [
        "drop_chance",
        "drop_minutes",
        "claim_cooldown",
        "common_chance",
        "rare_chance",
        "epic_chance",
        "legendary_chance",
        "daily_min",
        "daily_max",
        "weekly_min",
        "weekly_max",
        "regular_crate_min",
        "regular_crate_max",
        "legendary_crate_min",
        "legendary_crate_max",
        "legendary_second_card_chance",
    ]

    choices = []

    for option in options:
        label = option.replace("_", " ").title()

        if current and current not in option.lower() and current not in label.lower():
            continue

        choices.append(app_commands.Choice(name=label[:100], value=option))

        if len(choices) >= 25:
            break

    return choices

# ---------------- BOT ----------------
class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        global db_pool

        if not TOKEN:
            raise RuntimeError("DISCORD_TOKEN is missing. Add it in Railway Variables.")

        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL is missing. Add it in Railway Variables.")

        print("Startup check: token found.")
        print("Startup check: database URL found.")

        db_pool = await asyncpg.create_pool(DATABASE_URL)
        print("Startup check: database pool created.")

        await setup_database()
        print("Startup check: database tables checked.")

        synced = await self.tree.sync()
        print(f"Startup check: synced {len(synced)} slash commands.")

bot = Bot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Connected guilds: {len(bot.guilds)}")

    for guild in bot.guilds:
        print(f"- {guild.name} ({guild.id})")

    if not auto_drop.is_running():
        auto_drop.start()
        print("Auto drop task started.")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    original_error = getattr(error, "original", error)

    print(f"Command error in /{interaction.command.name if interaction.command else 'unknown'}: {repr(original_error)}")

    try:
        await send_staff_log(
            interaction.guild,
            "Command Error",
            f"**Command:** /{interaction.command.name if interaction.command else 'unknown'}\n"
            f"**User:** {interaction.user.mention if interaction.user else 'Unknown'}\n"
            f"**Error:** `{type(original_error).__name__}: {str(original_error)[:900]}`",
            discord.Color.red()
        )
    except Exception as log_error:
        print(f"Could not send command error log: {log_error}")

    message = "Something went wrong while running that command. Staff has been notified if a staff log channel is set."

    if isinstance(original_error, app_commands.MissingPermissions):
        message = "You do not have permission to use that command."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)

# ---------------- COMMANDS ----------------
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

    event_multiplier = await get_event_reward_multiplier(interaction.guild.id if interaction.guild else None)
    if event_multiplier > 1:
        amount = int(amount * event_multiplier)

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

    daily_message = random.choice(DAILY_CLAIM_MESSAGES).format(amount=f"**{format_coins(total)}**")
    message = f"{CURRENCY_EMOJI} | {daily_message}"

    if streak >= 3:
        message += f" [{STREAK_EMOJI} {streak}]"

    if bonus > 0:
        message += f"\nMilestone bonus: **{format_coins(bonus)}**"

    if boost_bonus > 0:
        message += f"\n{DAILY_BOOST_EMOJI} Daily Boost bonus: **{format_coins(boost_bonus)}**"

    if event_multiplier > 1:
        message += f"\nActive event bonus applied."

    if found_crate:
        message += f"\n{GIFT_BOX_EMOJI} You found a Loot Crate! Use `/opencrate`"

    await interaction.response.send_message(message)

@bot.tree.command(name="weekly", description="Claim your weekly reward.")
async def weekly(interaction: discord.Interaction):
    user_id = interaction.user.id
    last = await get_cooldown(user_id, "weekly")
    now = int(time.time())

    if last and now - int(last) < WEEKLY_COOLDOWN:
        ready_at = int(last) + WEEKLY_COOLDOWN
        return await interaction.response.send_message(
            f"You already claimed your weekly reward. Try again <t:{ready_at}:R>.",
            ephemeral=True
        )

    weekly_message = random.choice(WEEKLY_CLAIM_MESSAGES) if "WEEKLY_CLAIM_MESSAGES" in globals() else "Another week, another reward."

    economy_settings = await get_economy_settings(interaction.guild.id)
    amount = random.randint(int(economy_settings["weekly_min"]), int(economy_settings["weekly_max"]))

    event_multiplier = await get_event_reward_multiplier(interaction.guild.id if interaction.guild else None)
    if event_multiplier > 1:
        amount = int(amount * event_multiplier)

    await add_balance(user_id, amount)
    await set_cooldown(user_id, "weekly")

    bonus_lines = []

    if random.randint(1, 100) <= int(economy_settings["weekly_daily_boost_chance"]):
        await set_boost(user_id, "daily", 24 * 60 * 60)
        bonus_lines.append(f"{DAILY_BOOST_EMOJI} Daily Boost")

    if random.randint(1, 100) <= int(economy_settings["weekly_luck_boost_chance"]):
        await set_boost(user_id, "luck", 60 * 60)
        bonus_lines.append(f"{LUCK_BOOST_EMOJI} Luck Boost")

    if random.randint(1, 100) <= int(economy_settings["weekly_weekly_boost_chance"]):
        await set_boost(user_id, "weekly", 7 * 24 * 60 * 60)
        bonus_lines.append(f"{WEEKLY_BOOST_EMOJI} Weekly Boost")

    await add_loot_crate(user_id, "legendary", 1)

    description = (
        f"{weekly_message}\n\n"
        f"{BULLET_EMOJI} Sancs: **{format_coins(amount)}**\n"
        f"{BULLET_EMOJI} {LEGENDARY_CRATE_EMOJI} Legendary Loot Crate: **1**"
    )

    if event_multiplier > 1:
        description += "\nActive event bonus applied."

    if bonus_lines:
        description += "\n\n**Bonus Perks**\n" + "\n".join(f"{BULLET_EMOJI} {line}" for line in bonus_lines)

    embed = discord.Embed(
        title=f"{WEEKLY_BOX_EMOJI} Weekly Reward",
        description=description,
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_thumbnail(url=LEGENDARY_CRATE_IMAGE_URL)

    await interaction.response.send_message(embed=embed)

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

    await send_staff_log(
        interaction.guild,
        "Currency Added",
        f"**User:** {user.mention}\n**Amount:** {format_coins(amount)}\n**Added by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

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
        title_text = f" **{title}**" if title else ""
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

    await send_staff_log(
        interaction.guild,
        "Staff Sniping Updated",
        f"**New value:** {'Enabled' if enabled else 'Disabled'}\n**Updated by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

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

@bot.tree.command(name="opencrate", description="Open one of your loot crates.")
@app_commands.describe(crate_type="Choose which crate to open")
@app_commands.choices(
    crate_type=[
        app_commands.Choice(name="Loot Crate", value="regular"),
        app_commands.Choice(name="Legendary Loot Crate", value="legendary"),
    ]
)
async def opencrate(interaction: discord.Interaction, crate_type: app_commands.Choice[str]):
    await interaction.response.defer()

    crate_settings = await get_crate_settings(interaction.guild.id)
    regular_count, legendary_count = await get_loot_crates(interaction.user.id)

    if crate_type.value == "regular" and regular_count <= 0:
        return await interaction.followup.send("You do not have any Loot Crates.", ephemeral=True)

    if crate_type.value == "legendary" and legendary_count <= 0:
        return await interaction.followup.send("You do not have any Legendary Loot Crates.", ephemeral=True)

    cards = await get_active_cards()

    if not cards:
        return await interaction.followup.send("There are no active cards to pull from right now.", ephemeral=True)

    if crate_type.value == "legendary":
        sancs_amount = random.randint(int(crate_settings["legendary_crate_min"]), int(crate_settings["legendary_crate_max"]))
        crate_name = "Legendary Loot Crate"
        crate_emoji = LEGENDARY_CRATE_EMOJI
        await remove_loot_crate(interaction.user.id, "legendary")
    else:
        sancs_amount = random.randint(int(crate_settings["regular_crate_min"]), int(crate_settings["regular_crate_max"]))
        crate_name = "Loot Crate"
        crate_emoji = LOOT_CRATE_EMOJI
        await remove_loot_crate(interaction.user.id, "regular")

    selected_card = await choose_drop_card(cards, interaction.guild.id if interaction.guild else None)
    await add_card_to_inventory(interaction.user.id, selected_card["id"])
    await notify_completed_sets(interaction, interaction.user.id)
    await add_balance(interaction.user.id, sancs_amount)

    bonus_card_text = ""

    if crate_type.value == "legendary":
        bonus_chance = int(crate_settings["legendary_second_card_chance"])

        if random.randint(1, 100) <= bonus_chance:
            bonus_card = await choose_card_from_pool(cards, interaction.guild.id if interaction.guild else None)
            await add_card_to_inventory(interaction.user.id, bonus_card["id"])
            await notify_completed_sets(interaction, interaction.user.id)
            bonus_card_text = f"\n{BULLET_EMOJI} Bonus card: **{bonus_card['name']}** (**ID:** `{bonus_card['id']}`)"

    crate_message = random.choice(LOOT_CRATE_OPEN_MESSAGES)

    embed = discord.Embed(
        title=f"{crate_emoji} {crate_name} Opened",
        description=(
            f"{crate_message}\n\n"
            f"{BULLET_EMOJI} Sancs: **{format_coins(sancs_amount)}**\n"
            f"{BULLET_EMOJI} Card: **{selected_card['name']}** (**ID:** `{selected_card['id']}`)"
            f"{bonus_card_text}"
        ),
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_thumbnail(url=LEGENDARY_CRATE_IMAGE_URL if crate_type.value == "legendary" else LOOT_CRATE_IMAGE_URL)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="viewcard", description="View a specific card.")
@app_commands.describe(card="Choose a card by ID or name")
@app_commands.autocomplete(card=all_active_cards_autocomplete)
async def viewcard(interaction: discord.Interaction, card: str):
    c = await get_card_by_ref(card)

    if not c:
        return await interaction.response.send_message("Not found.", ephemeral=True)

    if c.get("is_event_card") and not await user_owns_card(interaction.user.id, c["id"]) and not await is_staff_member(interaction):
        return await interaction.response.send_message(EVENT_CARD_LOCKED_MESSAGE, ephemeral=True)

    active_text = "Currently obtainable" if c["is_active"] else "Unobtainable / limited"
    rarity_text = format_card_type_public(c)

    embed = discord.Embed(
        title=c["name"],
        description=(
            f"**ID:** {c['id']}\n"
            f"**Rarity:** {rarity_text}\n"
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

    starting_rarity = "Common"

    for rarity in ["Common", "Rare", "Epic", "Legendary", "Custom"]:
        if grouped.get(rarity):
            starting_rarity = rarity
            break

    view = CardsPaginationView(grouped, starting_rarity)

    await interaction.response.send_message(embed=view.current_embed(), view=view)

@bot.tree.command(name="inventory", description="View your inventory or another user's inventory.")
async def inventory(interaction: discord.Interaction, user: discord.Member = None):
    await interaction.response.defer()
    user = user or interaction.user

    bal = await get_balance(user.id)
    regular_crates, legendary_crates = await get_loot_crates(user.id)
    regular_snipers, legendary_snipers = await get_snipe_items(user.id)
    active_boosts = await get_active_boosts(user.id)
    title = await get_title(user.id)
    custom_emoji = await get_user_custom_emoji(user.id)
    owned_profile_emojis = await get_user_owned_profile_emojis(user.id)
    owned_titles = await get_user_owned_titles(user.id)

    emoji_text = f" {custom_emoji}" if custom_emoji else ""
    title_text = f" {title}" if title else ""

    description = f"**Balance:** {format_coins(bal)}\n"
    description += f"{BULLET_EMOJI} {LOOT_CRATE_EMOJI} **Loot Crates:** {regular_crates}\n"
    description += f"{BULLET_EMOJI} {LEGENDARY_CRATE_EMOJI} **Legendary Loot Crates:** {legendary_crates}\n"

    if regular_snipers > 0:
        description += f"{BULLET_EMOJI} {SNIPE_EMOJI} **Snipers:** {regular_snipers}\n"

    if legendary_snipers > 0:
        description += f"{BULLET_EMOJI} {LEGENDARY_SNIPER_EMOJI} **Legendary Snipers:** {legendary_snipers}\n"

    description += f"\n**Active Perks**\n{format_active_boosts(active_boosts)}\n"

    description += "\nUse `/cardinventory` to view cards."

    embed = discord.Embed(
        title=f"{user.display_name}{emoji_text}{title_text}'s Inventory",
        description=description.strip(),
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_thumbnail(url=INVENTORY_ICON_URL)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="cardinventory", description="View only your cards or another user's cards.")
async def cardinventory(interaction: discord.Interaction, user: discord.Member = None):
    await interaction.response.defer()
    user = user or interaction.user

    title = await get_title(user.id)
    custom_emoji = await get_user_custom_emoji(user.id)

    emoji_text = f" {custom_emoji}" if custom_emoji else ""
    title_text = f" {title}" if title else ""

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT cards.id, cards.name, cards.rarity, cards.custom_type, cards.is_active, COUNT(*) as amount
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE user_id=$1
            GROUP BY cards.id, cards.name, cards.rarity, cards.custom_type, cards.is_active
            ORDER BY cards.rarity, cards.id
        """, user.id)

    grouped = {
        "Common": [],
        "Rare": [],
        "Epic": [],
        "Legendary": [],
        "Custom": [],
    }

    for row in rows:
        grouped.setdefault(row["rarity"], []).append(row)

    embed = discord.Embed(
        title=f"{user.display_name}{emoji_text}{title_text}'s Card Inventory",
        color=discord.Color.from_str("#9e659d")
    )
    embed.set_thumbnail(url=INVENTORY_ICON_URL)

    has_cards = False

    for rarity in ["Common", "Rare", "Epic", "Legendary", "Custom"]:
        cards_for_rarity = grouped.get(rarity, [])

        if not cards_for_rarity:
            continue

        has_cards = True
        lines = []

        for row in cards_for_rarity[:10]:
            limited_note = "" if row["is_active"] else " *(unobtainable)*"
            lines.append(
                f"{BULLET_EMOJI} **ID:** `{row['id']}` {row['name']} ({format_card_type_public(row)}) x{row['amount']}{limited_note}"
            )

        extra_count = len(cards_for_rarity) - 10
        if extra_count > 0:
            lines.append(f"...and {extra_count} more. Use `/cards` for full card browsing.")

        embed.add_field(
            name=display_rarity_name(rarity),
            value="\n".join(lines),
            inline=False
        )

    if not has_cards:
        embed.description = "No cards yet."

    await interaction.followup.send(embed=embed)

async def user_cards_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT cards.id, cards.name, cards.rarity, cards.custom_type
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE inventory.user_id=$1
            ORDER BY cards.id
        """, interaction.user.id)

    choices = []

    for card in rows:
        label = plain_card_label(card)

        if current and current not in label.lower() and current not in str(card["id"]):
            continue

        choices.append(app_commands.Choice(name=label[:100], value=str(card["id"])))

        if len(choices) >= 25:
            break

    return choices

async def all_cards_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower()

    try:
        target = getattr(interaction.namespace, "user", None)
        target_user_id = target.id if target else None
    except Exception:
        target_user_id = None

    if not target_user_id:
        return []

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT cards.id, cards.name, cards.rarity, cards.custom_type
            FROM inventory
            JOIN cards ON cards.id = inventory.card_id
            WHERE inventory.user_id=$1
            ORDER BY cards.id
        """, target_user_id)

    choices = []

    for card in rows:
        label = plain_card_label(card)

        if current and current not in label.lower() and current not in str(card["id"]):
            continue

        choices.append(app_commands.Choice(name=label[:100], value=str(card["id"])))

        if len(choices) >= 25:
            break

    return choices

@bot.tree.command(name="trade", description="Trade one card with another user.")
@app_commands.describe(
    user="User you want to trade with",
    your_card="Card you are offering",
    their_card="Card you want from them"
)
@app_commands.autocomplete(your_card=user_cards_autocomplete, their_card=all_cards_autocomplete)
async def trade(interaction: discord.Interaction, user: discord.Member, your_card: str, their_card: str):
    await interaction.response.defer()

    if user.bot:
        return await interaction.followup.send("You cannot trade with bots.", ephemeral=True)

    if user.id == interaction.user.id:
        return await interaction.followup.send("You cannot trade with yourself.", ephemeral=True)

    your_card_data = await get_card_by_ref(your_card)
    their_card_data = await get_card_by_ref(their_card)

    if not your_card_data:
        return await interaction.followup.send("Your offered card was not found.", ephemeral=True)

    if not their_card_data:
        return await interaction.followup.send("The requested card was not found.", ephemeral=True)

    if your_card_data["id"] in active_trade_card_ids or their_card_data["id"] in active_trade_card_ids:
        return await interaction.followup.send("One of those cards is already in an active trade.", ephemeral=True)

    if not await user_owns_card(interaction.user.id, your_card_data["id"]):
        return await interaction.followup.send("You do not own the card you are trying to offer.", ephemeral=True)

    if not await user_owns_card(user.id, their_card_data["id"]):
        return await interaction.followup.send(f"{user.display_name} does not own the card you requested.", ephemeral=True)

    requester_trade_usage = await get_daily_limit_row(interaction.user.id, "trade")
    target_trade_usage = await get_daily_limit_row(user.id, "trade")

    if requester_trade_usage["count_value"] >= MAX_TRADES_PER_DAY:
        return await interaction.followup.send(
            f"You have reached your daily trade limit of **{MAX_TRADES_PER_DAY}** trades.",
            ephemeral=True
        )

    if target_trade_usage["count_value"] >= MAX_TRADES_PER_DAY:
        return await interaction.followup.send(
            f"{user.display_name} has reached their daily trade limit of **{MAX_TRADES_PER_DAY}** trades.",
            ephemeral=True
        )

    active_trade_card_ids.add(your_card_data["id"])
    active_trade_card_ids.add(their_card_data["id"])

    view = TradeView(interaction.user, user, your_card_data, their_card_data)

    await interaction.followup.send(embed=view.create_embed(), view=view)

@bot.tree.command(name="addcard", description="Staff only: add or reactivate a collectible card.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    name="Card name",
    rarity="Card rarity",
    image="Direct image URL",
    custom_type="Only needed for Custom cards"
)
@app_commands.choices(
    rarity=[
        app_commands.Choice(name="Common", value="Common"),
        app_commands.Choice(name="Rare", value="Rare"),
        app_commands.Choice(name="Epic", value="Epic"),
        app_commands.Choice(name="Legendary", value="Legendary"),
        app_commands.Choice(name="Custom", value="Custom"),
    ]
)
async def addcard(
    interaction: discord.Interaction,
    name: str,
    rarity: app_commands.Choice[str],
    image: str,
    custom_type: Optional[str] = None
):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    selected_custom_type = custom_type.strip() if custom_type else None

    if rarity.value == "Custom" and not selected_custom_type:
        selected_custom_type = "Collectible"

    if selected_custom_type and len(selected_custom_type) > 40:
        return await interaction.response.send_message("Custom type must be 40 characters or less.", ephemeral=True)

    if rarity.value != "Custom":
        selected_custom_type = None

    existing_card = await get_card_by_name(name)
    async with db_pool.acquire() as conn:
        if existing_card:
            await conn.execute(
                """
                UPDATE cards
                SET rarity=$1, image=$2, is_active = TRUE, custom_type=$3
                WHERE id=$4
                """,
                rarity.value,
                image,
                selected_custom_type,
                existing_card["id"]
            )
            return await interaction.response.send_message(
                f"Reactivated/updated **{name}** as a **{rarity.value}** card. **ID:** `{existing_card['id']}``"
            )
        new_id = await conn.fetchval(
            "INSERT INTO cards (name, rarity, image, is_active, custom_type) VALUES ($1,$2,$3, TRUE, $4) RETURNING id",
            name,
            rarity.value,
            image,
            selected_custom_type
        )
    await interaction.response.send_message(f"Added **{name}** as a **{rarity.value}** card. **ID:** `{new_id}``")

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
        app_commands.Choice(name="Custom", value="Custom"),
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
    selected_card = await choose_drop_card(cards, interaction.guild.id if interaction.guild else None)
    await send_staff_log(
        interaction.guild,
        "Manual Card Drop",
        f"**Card:** {selected_card['name']}\n**ID:** `{selected_card['id']}`\n**Rarity:** {selected_card['rarity']}\n**Custom Type:** {get_record_value(selected_card, 'custom_type') or 'None'}\n**Dropped by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(
        embed=create_card_embed(selected_card),
        view=ClaimView(selected_card)
    )

@bot.tree.command(name="removecard", description="Staff only: remove a card from future drops.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(card_name="Choose the card to remove")
@app_commands.autocomplete(card_name=all_active_cards_autocomplete)
async def removecard(interaction: discord.Interaction, card_name: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

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
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    title="Title text to sell",
    price="Price in Sancs"
)
async def addtitle(interaction: discord.Interaction, title: str, price: int):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    if price <= 0:
        return await interaction.response.send_message("Price must be greater than 0.", ephemeral=True)

    title_id = await add_title_to_shop(title, price)

    await interaction.response.send_message(
        f"Added title **{title}** for **{format_coins(price)}**. **ID:** `{title_id}`"
    )

@bot.tree.command(name="removetitle", description="Staff only: remove a preset title from the shop.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(title="Title to remove")
@app_commands.autocomplete(title=shop_title_autocomplete)
async def removetitle(interaction: discord.Interaction, title: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    row = await get_shop_title_by_ref(title)

    if not row:
        return await interaction.response.send_message("Title not found.", ephemeral=True)

    success = await remove_title_from_shop(row["title"])

    if not success:
        return await interaction.response.send_message("Title not found.", ephemeral=True)

    await send_staff_log(
        interaction.guild,
        "Title Removed",
        f"**Title:** {row['title']}\n**Removed by:** {interaction.user.mention}",
        discord.Color.red()
    )

    await interaction.response.send_message(
        f"Removed `{row['title']}` from the title shop.",
        ephemeral=True
    )

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
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    name="Emoji display name",
    emoji="Emoji to sell",
    price="Price in Sancs"
)
async def addprofileemoji(interaction: discord.Interaction, name: str, emoji: str, price: int):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    if price <= 0:
        return await interaction.response.send_message("Price must be greater than 0.", ephemeral=True)

    emoji_id = await add_profile_emoji_to_shop(name, emoji, price)

    await interaction.response.send_message(
        f"Added profile emoji **{name}** {emoji} for **{format_coins(price)}**. **ID:** `{emoji_id}`"
    )

@bot.tree.command(name="removeprofileemoji", description="Staff only: remove a preset profile emoji from the shop.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(name="Profile emoji to remove")
@app_commands.autocomplete(name=profile_emoji_shop_autocomplete)
async def removeprofileemoji(interaction: discord.Interaction, name: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    row = await get_profile_emoji_by_ref(name)

    if not row:
        return await interaction.response.send_message("Profile emoji not found.", ephemeral=True)

    success = await remove_profile_emoji_from_shop(row["name"])

    if not success:
        return await interaction.response.send_message("Profile emoji not found.", ephemeral=True)

    await send_staff_log(
        interaction.guild,
        "Profile Emoji Removed",
        f"**Emoji:** {row['emoji']} `{row['name']}`\n**Removed by:** {interaction.user.mention}",
        discord.Color.red()
    )

    await interaction.response.send_message(
        f"Removed {row['emoji']} `{row['name']}` from the profile emoji shop.",
        ephemeral=True
    )

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
@app_commands.describe(role="General staff role")
async def setstaffrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only server administrators can set staff roles.", ephemeral=True)

    await set_staff_role_db(interaction.guild.id, role.id)

    await send_staff_log(
        interaction.guild,
        "Staff Role Updated",
        f"**Role:** {role.mention}\n**Updated by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(f"Staff role set to {role.mention}.", ephemeral=True)

@bot.tree.command(name="addropchannel", description="Staff only: add a channel for automatic card drops.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(channel="Channel where automatic drops can happen")
async def addropchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)
    await add_drop_channel_db(interaction.guild.id, channel.id)

    await send_staff_log(
        interaction.guild,
        "Drop Channel Added",
        f"**Channel:** {channel.mention}\n**Added by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(
        f"Added {channel.mention} as a drop channel."
    )

@bot.tree.command(name="removedropchannel", description="Staff only: remove a channel from automatic card drops.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(channel="Channel to remove from automatic drops")
async def removedropchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)
    await remove_drop_channel_db(interaction.guild.id, channel.id)

    await send_staff_log(
        interaction.guild,
        "Drop Channel Removed",
        f"**Channel:** {channel.mention}\n**Removed by:** {interaction.user.mention}",
        discord.Color.red()
    )

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

    await send_staff_log(
        interaction.guild,
        "Snipers Given",
        f"**User:** {user.mention}\n**Item:** {amount}x {sniper_name}\n**Given by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

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

    await send_staff_log(
        interaction.guild,
        "Crates Given",
        f"**User:** {user.mention}\n**Item:** {amount}x {crate_name}\n**Given by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(
        f"Gave {user.mention} **{amount}x {crate_name}**."
    )

class MemberHelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Main Commands", value="main", description="Daily, weekly, inventory, shop"),
            discord.SelectOption(label="Cards & Collections", value="cards", description="Cards, sets, collections"),
            discord.SelectOption(label="Trading", value="trade", description="Trading cards with other users"),
            discord.SelectOption(label="Sniper Game", value="snipe", description="How snipes work"),
        ]

        super().__init__(
            placeholder="Choose a help section...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=create_member_help_embed(self.values[0]), view=self.view)

class MemberHelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(MemberHelpSelect())

def create_member_help_embed(section="main"):
    titles = {
        "main": "Main Help",
        "cards": "Cards & Collections Help",
        "trade": "Trading Help",
        "snipe": "Sniper Game Help",
    }

    embed = discord.Embed(
        title=titles.get(section, "Help Menu"),
        color=discord.Color.from_str("#9e659d")
    )

    if section == "main":
        embed.description = "Here’s everything you need to survive."
        embed.add_field(
            name="Main Commands",
            value=(
                "`/daily` - claim daily Sancs.\n"
                "`/weekly` - claim your weekly reward.\n"
                "`/inventory` - view Sancs, perks, crates, titles, and emojis.\n"
                "`/cardinventory` - view your cards by rarity.\n"
                "`/shop` - view the shop.\n"
                "`/buy` - buy shop items.\n"
                "`/leaderboard` - view the leaderboard."
            ),
            inline=False
        )

    elif section == "cards":
        embed.description = "Cards, collections, and completion rewards."
        embed.add_field(
            name="Cards",
            value=(
                "`/cards` - view obtainable cards.\n"
                "`/viewcard` - view a card.\n"
                "`/cardinventory` - view owned cards.\n"
                "`/sellcard` - sell a card."
            ),
            inline=False
        )
        embed.add_field(
            name="Collections",
            value=(
                "`/cardsets` - view available collections.\n"
                "`/viewset` - view a collection and your progress.\n"
                ""
            ),
            inline=False
        )

    elif section == "trade":
        embed.description = "Trade cards safely with other users."
        embed.add_field(
            name="Trading",
            value=(
                "`/trade` - request a card trade.\n"
                "Both users must own the cards being traded.\n"
                "Trades use Accept/Decline buttons."
            ),
            inline=False
        )

    elif section == "snipe":
        embed.description = "The sniper game is a hide-and-seek mute game."
        embed.add_field(
            name="How Snipes Work",
            value=(
                "Buy a sniper from the shop, then use `/snipe` on another user.\n"
                "The target hides in a bush.\n"
                "The sniper chooses a bush.\n"
                "If the sniper finds them, the target is muted for the set time.\n"
                "If the sniper misses, the target escapes."
            ),
            inline=False
        )

    return embed

@bot.tree.command(name="help", description="View bot help.")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_member_help_embed("main"), view=MemberHelpView(), ephemeral=True)

class StaffHelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Staff Commands", value="staff", description="General staff tools"),
            discord.SelectOption(label="Admin Setup", value="admin", description="Setup and configuration"),
            discord.SelectOption(label="Events & Collections", value="events", description="Event cards and card sets"),
            discord.SelectOption(label="Shop Management", value="shop", description="Titles, emojis, cards, shop"),
            discord.SelectOption(label="Settings", value="settings", description="Drop, rarity, crate, economy settings"),
        ]

        super().__init__(
            placeholder="Choose a staff help section...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=create_staff_help_embed(self.values[0]), view=self.view)

class StaffHelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(StaffHelpSelect())

def create_staff_help_embed(section="staff"):
    titles = {
        "staff": "Staff Help",
        "admin": "Admin Help",
        "events": "Events & Collections Help",
        "shop": "Shop Management Help",
        "settings": "Settings Help",
    }

    embed = discord.Embed(
        title=titles.get(section, "Staff Help"),
        color=discord.Color.from_str("#9e659d")
    )

    if section == "staff":
        embed.description = "General staff tools."
        embed.add_field(
            name="Cards & User Tools",
            value=(
                "`/dropcard` - manually drop a card.\n"
                "`/givecard` - give a card to a user.\n"
                "`/resetuser` - reset a user with confirmation.\n"
                "`/addcurrency` - give Sancs to a user.\n"
                "`/removecurrency` - remove Sancs from a user."
            ),
            inline=False
        )

    elif section == "admin":
        embed.description = "Setup and admin configuration."
        embed.add_field(
            name="Setup",
            value=(
                "`/setadminrole` - set the admin role.\n`/setmodrole` - set the mod role.\n`/setstaffrole` - set the staff role.\n"
                "`/setstafflog` - set the staff log channel.\n"
                "`/adddropchannel` - add a drop channel.\n"
                "`/removedropchannel` - remove a drop channel.\n"
                "`/settings` - view bot setup/status."
            ),
            inline=False
        )

    elif section == "events":
        embed.description = "Event cards, collections, and rewards."
        embed.add_field(
            name="Event Cards",
            value=(
                "`/seteventcard` - mark a card as an event card.\n"
                "`/removeeventcard` - remove a card from the event-card pool.\n"
                "`/eventsetup` - manage event settings."
            ),
            inline=False
        )
        embed.add_field(
            name="Collections",
            value=(
                "`/collectionsetup` - view collection setup.\n`/setticketchannel` - set the collection reward ticket channel.\n"
                "`/setcompletionemoji` - set the collection complete emoji.\n"
                "`/createset` - create a collection set.\n"
                "`/addcardtoset` - add a card to a set.\n"
                "`/removecardfromset` - remove a card from a set.\n"
                "`/viewset` - view a set.\n"
                "`/cardsets` - view all sets.\n"
                "`/checksets` - check completed sets."
            ),
            inline=False
        )

    elif section == "shop":
        embed.description = "Shop and reward management."
        embed.add_field(
            name="Cards",
            value=(
                "`/addcard` - add a card.\n"
                "`/removecard` - remove a card from future drops.\n"
                "`/cards` - view obtainable cards."
            ),
            inline=False
        )
        embed.add_field(
            name="Titles & Emojis",
            value=(
                "`/addtitle` - add a shop title.\n"
                "`/removetitle` - remove a shop title.\n"
                "`/addprofileemoji` - add a profile emoji.\n"
                "`/removeprofileemoji` - remove a profile emoji.\n"
                "`/unequiptitle` - remove your equipped title.\n"
                "`/unequipemoji` - remove your equipped emoji."
            ),
            inline=False
        )

    elif section == "settings":
        embed.description = "Bot settings and tuning."
        embed.add_field(
            name="Settings",
            value=(
                "`/settings` - view and edit admin settings.\n"
                "`/settingsedit` - quickly edit common settings.\n"
                "`/raritychances` - view rarity weights.\n"
                "`/setraritychance` - edit rarity weights."
            ),
            inline=False
        )

    return embed

@bot.tree.command(name="staffhelp", description="Staff only: view staff help.")
@app_commands.default_permissions(manage_messages=True)
async def staffhelp(interaction: discord.Interaction):
    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    await interaction.response.send_message(embed=create_staff_help_embed("staff"), view=StaffHelpView(), ephemeral=True)

@bot.tree.command(name="setstafflogchannel", description="Admin only: set the staff log channel.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(channel="Channel where staff logs should be sent")
async def setstafflogchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can set the staff log channel.", ephemeral=True)

    await set_staff_log_channel_db(interaction.guild.id, channel.id)

    embed = discord.Embed(
        title="Staff Log Channel Set",
        description=f"Staff logs will now be sent to {channel.mention}.",
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

    await send_staff_log(
        interaction.guild,
        "Staff Log Connected",
        f"Staff log channel set by {interaction.user.mention}.",
        discord.Color.from_str("#9e659d")
    )

@bot.tree.command(name="resetuser", description="Admin only: reset one user's bot data.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(user="User whose bot data should be reset")
async def resetuser(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can reset user data.", ephemeral=True)

    if user.bot:
        return await interaction.response.send_message("You cannot reset bot users.", ephemeral=True)

    embed = discord.Embed(
        title="Confirm User Reset",
        description=(
            f"Are you sure you want to reset {user.mention}'s bot data?\n\n"
            "**This will remove:**\n"
            f"{BULLET_EMOJI} Balance\n"
            f"{BULLET_EMOJI} Cards\n"
            f"{BULLET_EMOJI} Crates\n"
            f"{BULLET_EMOJI} Snipers\n"
            f"{BULLET_EMOJI} Equipped title / emoji\n"
            f"{BULLET_EMOJI} Owned titles / emojis\n"
            f"{BULLET_EMOJI} Cooldowns and daily limits"
        ),
        color=discord.Color.red()
    )

    await interaction.response.send_message(
        embed=embed,
        view=ResetUserConfirmView(interaction.user, user),
        ephemeral=True
    )

@bot.tree.command(name="eventsetup", description="Admin only: open the event setup panel.")
@app_commands.default_permissions(administrator=True)
async def eventsetup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use event setup.", ephemeral=True)

    await interaction.response.send_message(
        embed=await create_eventsetup_home_embed(interaction.guild.id),
        view=EventSetupView(),
        ephemeral=True
    )

@bot.tree.command(name="seteventcard", description="Staff only: mark a card as a locked event card.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(card="Card to mark as event", event_name="Event name for this card")
@app_commands.autocomplete(card=active_card_autocomplete)
async def seteventcard(interaction: discord.Interaction, card: str, event_name: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    card_row = await get_card_by_ref(card)

    if not card_row:
        return await interaction.response.send_message("Card not found.", ephemeral=True)

    updated = await set_card_event_status(card_row["id"], True, event_name)

    await send_staff_log(
        interaction.guild,
        "Event Card Locked",
        f"**Card:** {updated['name']} (`{updated['id']}`)\n**Event:** {event_name}\n**Updated by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(
        f"Locked **{updated['name']}** as an event card for **{event_name}**.",
        ephemeral=True
    )

@bot.tree.command(name="removeeventcard", description="Staff only: remove event-card lock from a card.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(card="Card to unlock")
@app_commands.autocomplete(card=event_card_autocomplete)
async def removeeventcard(interaction: discord.Interaction, card: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)

    card_row = await get_card_by_ref(card)

    if not card_row:
        return await interaction.response.send_message("Card not found.", ephemeral=True)

    updated = await set_card_event_status(card_row["id"], False, None)

    await send_staff_log(
        interaction.guild,
        "Event Card Unlocked",
        f"**Card:** {updated['name']} (`{updated['id']}`)\n**Updated by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(
        f"Removed event lock from **{updated['name']}**.",
        ephemeral=True
    )

@bot.tree.command(name="setticketchannel", description="Staff only: set the ticket channel for collection rewards.")
@app_commands.default_permissions(administrator=True)
async def setticketchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)
    await set_collection_ticket_channel_db(interaction.guild.id, channel.id)
    await send_staff_log(interaction.guild, "Collection Ticket Channel Updated", f"**Channel:** {channel.mention}\n**Updated by:** {interaction.user.mention}", discord.Color.from_str("#9e659d"))
    await interaction.response.send_message(f"Collection reward ticket channel set to {channel.mention}.", ephemeral=True)

@bot.tree.command(name="setcompletionemoji", description="Staff only: set the emoji for completed collections.")
@app_commands.default_permissions(administrator=True)
async def setcompletionemoji(interaction: discord.Interaction, emoji: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)
    await set_collection_completion_emoji_db(interaction.guild.id, emoji)
    await send_staff_log(interaction.guild, "Collection Completion Emoji Updated", f"**Emoji:** {emoji}\n**Updated by:** {interaction.user.mention}", discord.Color.from_str("#9e659d"))
    await interaction.response.send_message(f"Collection completion emoji set to {emoji}.", ephemeral=True)

@bot.tree.command(name="createset", description="Admin only: create a card collection set.")
@app_commands.default_permissions(administrator=True)
async def createset(interaction: discord.Interaction, name: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    async with db_pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO card_sets (guild_id, name, reward_text, is_active)
                VALUES ($1, $2, $3, TRUE)
            """, interaction.guild.id, name, "Open a ticket to claim your reward.")
        except Exception:
            return await interaction.response.send_message("A set with that name already exists.", ephemeral=True)

    await send_staff_log(
        interaction.guild,
        "Card Set Created",
        f"**Set:** {name}\n**Created by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )
    await interaction.response.send_message(f"Created set **{name}**.", ephemeral=True)

@bot.tree.command(name="addcardtoset", description="Staff only: add a card to a collection set.")
@app_commands.default_permissions(administrator=True)
@app_commands.autocomplete(set_name=card_set_autocomplete, card=active_card_autocomplete)
async def addcardtoset(interaction: discord.Interaction, set_name: str, card: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)
    card_set = await get_card_set_by_ref(interaction.guild.id, set_name)
    if not card_set:
        return await interaction.response.send_message("Set not found.", ephemeral=True)
    card_row = await get_card_by_ref(card)
    if not card_row:
        return await interaction.response.send_message("Card not found.", ephemeral=True)
    async with db_pool.acquire() as conn:
        await conn.execute("INSERT INTO card_set_cards (set_id, card_id) VALUES ($1, $2) ON CONFLICT DO NOTHING", card_set["id"], card_row["id"])
    await send_staff_log(interaction.guild, "Card Added To Set", f"**Set:** {card_set['name']}\n**Card:** {card_row['name']} (`{card_row['id']}`)\n**Updated by:** {interaction.user.mention}", discord.Color.from_str("#9e659d"))
    await interaction.response.send_message(f"Added **{card_row['name']}** to **{card_set['name']}**.", ephemeral=True)

@bot.tree.command(name="removecardfromset", description="Staff only: remove a card from a collection set.")
@app_commands.default_permissions(administrator=True)
@app_commands.autocomplete(set_name=card_set_autocomplete, card=active_card_autocomplete)
async def removecardfromset(interaction: discord.Interaction, set_name: str, card: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    if not await is_staff_member(interaction):
        return await interaction.response.send_message("No permission.", ephemeral=True)
    card_set = await get_card_set_by_ref(interaction.guild.id, set_name)
    if not card_set:
        return await interaction.response.send_message("Set not found.", ephemeral=True)
    card_row = await get_card_by_ref(card)
    if not card_row:
        return await interaction.response.send_message("Card not found.", ephemeral=True)
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM card_set_cards WHERE set_id=$1 AND card_id=$2", card_set["id"], card_row["id"])
    await send_staff_log(interaction.guild, "Card Removed From Set", f"**Set:** {card_set['name']}\n**Card:** {card_row['name']} (`{card_row['id']}`)\n**Updated by:** {interaction.user.mention}", discord.Color.red())
    await interaction.response.send_message(f"Removed **{card_row['name']}** from **{card_set['name']}**.", ephemeral=True)

@bot.tree.command(name="viewset", description="View a collection set and your progress.")
@app_commands.autocomplete(set_name=card_set_autocomplete)
async def viewset(interaction: discord.Interaction, set_name: str):
    card_set = await get_card_set_by_ref(interaction.guild.id, set_name)

    if not card_set:
        return await interaction.response.send_message("Set not found.", ephemeral=True)

    cards = await get_cards_in_set(card_set["id"])
    complete, owned_count, total_count = await user_owns_all_cards_in_set(interaction.user.id, card_set["id"])

    if not cards:
        card_text = "No cards have been added to this set yet."
    else:
        lines = []
        for card in cards:
            lines.append(f"{BULLET_EMOJI} {card['name']}")
        card_text = "\n".join(lines)

    embed = discord.Embed(
        title=f"{card_set['name']} Collection",
        description=f"**Progress:** {owned_count}/{total_count}\n\n**Cards**\n{card_text}",
        color=discord.Color.from_str("#9e659d")
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cardsets", description="View available card collection sets.")
async def cardsets(interaction: discord.Interaction):
    async with db_pool.acquire() as conn:
        sets = await conn.fetch("SELECT * FROM card_sets WHERE guild_id=$1 AND is_active=TRUE ORDER BY name", interaction.guild.id)
    if not sets:
        return await interaction.response.send_message("No card sets are available right now.", ephemeral=True)
    lines = []
    for card_set in sets:
        complete, owned_count, total_count = await user_owns_all_cards_in_set(interaction.user.id, card_set["id"])
        status = "✅" if complete else "⬜"
        lines.append(f"{status} **{card_set['name']}** — {owned_count}/{total_count}")
    embed = discord.Embed(title="Card Collections", description="\n".join(lines), color=discord.Color.from_str("#9e659d"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unequiptitle", description="Remove your currently equipped title.")
async def unequiptitle(interaction: discord.Interaction):
    await clear_user_title(interaction.user.id)
    await interaction.response.send_message("Your title has been unequipped.", ephemeral=True)

@bot.tree.command(name="unequipemoji", description="Remove your currently equipped profile emoji.")
async def unequipemoji(interaction: discord.Interaction):
    await clear_user_custom_emoji(interaction.user.id)
    await interaction.response.send_message("Your profile emoji has been unequipped.", ephemeral=True)

SETTING_OPTIONS = {
    "drops": {
        "title": "Drops Settings",
        "items": {
            "auto_drop_minutes": {"label": "Drop Interval", "kind": "drop", "values": [5, 10, 15, 20, 30, 45, 60, 90, 120], "suffix": " minutes"},
            "auto_drop_chance": {"label": "Drop Chance", "kind": "drop", "values": [0, 5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100], "suffix": "%"},
            "claim_cooldown_seconds": {"label": "Claim Cooldown", "kind": "drop", "values": [0, 10, 15, 30, 45, 60, 90, 120, 300], "suffix": " seconds"},
        },
    },
    "rarity": {
        "title": "Rarity Settings",
        "items": {
            "common_chance": {"label": "Common", "kind": "rarity", "values": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], "suffix": ""},
            "rare_chance": {"label": "Rare", "kind": "rarity", "values": [0, 5, 10, 15, 20, 25, 30, 40, 50], "suffix": ""},
            "epic_chance": {"label": "Epic", "kind": "rarity", "values": [0, 1, 2, 3, 5, 8, 10, 15, 20, 25], "suffix": ""},
            "legendary_chance": {"label": "Legendary", "kind": "rarity", "values": [0, 1, 2, 3, 5, 8, 10, 15], "suffix": ""},
        },
    },
    "economy": {
        "title": "Economy Settings",
        "items": {
            "daily_min": {"label": "Daily Minimum", "kind": "economy", "values": [50, 100, 150, 200, 250, 500, 750, 1000], "suffix": " Sancs"},
            "daily_max": {"label": "Daily Maximum", "kind": "economy", "values": [250, 500, 750, 1000, 1500, 2000, 2500, 5000], "suffix": " Sancs"},
            "weekly_min": {"label": "Weekly Minimum", "kind": "economy", "values": [500, 1000, 1500, 2000, 2500, 5000], "suffix": " Sancs"},
            "weekly_max": {"label": "Weekly Maximum", "kind": "economy", "values": [1000, 2000, 3000, 5000, 7500, 10000], "suffix": " Sancs"},
        },
    },
    "events": {
        "title": "Event Settings",
        "items": {
            "event_card_chance": {"label": "Event Card Chance", "kind": "event", "values": [0, 1, 2, 5, 10, 15, 20, 25, 30, 40, 50], "suffix": "%"},
        },
    },
    "crates": {
        "title": "Crate Settings",
        "items": {
            "regular_crate_min": {"label": "Regular Crate Minimum", "kind": "crate", "values": [50, 100, 250, 500, 750, 1000], "suffix": " Sancs"},
            "regular_crate_max": {"label": "Regular Crate Maximum", "kind": "crate", "values": [250, 500, 750, 1000, 1500, 2000], "suffix": " Sancs"},
            "legendary_crate_min": {"label": "Legendary Crate Minimum", "kind": "crate", "values": [500, 750, 1000, 1500, 2000, 2500], "suffix": " Sancs"},
            "legendary_crate_max": {"label": "Legendary Crate Maximum", "kind": "crate", "values": [1500, 2000, 2500, 3000, 5000, 7500], "suffix": " Sancs"},
            "legendary_second_card_chance": {"label": "Legendary Bonus Card Chance", "kind": "crate", "values": [0, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100], "suffix": "%"},
        },
    },
}

async def get_settings_snapshot(guild_id):
    return {
        "drop": await get_drop_settings(guild_id),
        "rarity": await get_rarity_settings(guild_id),
        "economy": await get_economy_settings(guild_id),
        "crate": await get_crate_settings(guild_id),
        "event": await get_event_settings(guild_id),
        "collection": await get_collection_settings(guild_id),
    }

def get_setting_current_value(snapshot, key, kind):
    if kind == "drop":
        return snapshot["drop"].get(key)
    if kind == "rarity":
        return snapshot["rarity"].get(key)
    if kind == "economy":
        return snapshot["economy"].get(key)
    if kind == "crate":
        return snapshot["crate"].get(key)
    if kind == "event":
        return snapshot["event"].get(key)
    return None

async def apply_simple_setting(guild_id, key, kind, value):
    if kind == "drop":
        if key == "auto_drop_minutes":
            await set_auto_drop_minutes_db(guild_id, value)
        elif key == "auto_drop_chance":
            await set_auto_drop_chance_db(guild_id, value)
        elif key == "claim_cooldown_seconds":
            await set_claim_cooldown_db(guild_id, value)
    elif kind == "rarity":
        await set_rarity_setting_db(guild_id, key, value)
    elif kind == "economy":
        await set_economy_setting_db(guild_id, key, value)
    elif kind == "crate":
        await set_crate_setting_db(guild_id, key, value)
    elif kind == "event":
        if key == "event_card_chance":
            await set_event_card_chance_db(guild_id, value)

async def create_settings_embed(guild_id, section="status"):
    snapshot = await get_settings_snapshot(guild_id)
    titles = {
        "status": "Settings Status",
        "drops": "Drops Settings",
        "rarity": "Rarity Settings",
        "economy": "Economy Settings",
        "crates": "Crate Settings",
        "events": "Event Settings",
        "collections": "Collection Settings",
    }

    embed = discord.Embed(
        title=titles.get(section, "Settings"),
        color=discord.Color.from_str("#9e659d")
    )

    if section == "status":
        embed.description = "Use the dropdown to view each section."

        admin_role_id = await get_admin_role(guild_id)
        mod_role_id = await get_mod_role(guild_id)
        staff_role_id = await get_staff_role(guild_id)
        staff_log_channel_id = await get_staff_log_channel(guild_id)

        collection = snapshot["collection"]
        drop = snapshot["drop"]
        event = snapshot["event"]

        try:
            async with db_pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT channel_id FROM drop_channels WHERE guild_id=$1 ORDER BY channel_id",
                    guild_id
                )
                drop_channels = [row["channel_id"] for row in rows]
        except Exception:
            drop_channels = []

        if drop_channels:
            drop_channel_text = ", ".join(f"<#{channel_id}>" for channel_id in drop_channels[:8])
            if len(drop_channels) > 8:
                drop_channel_text += f" +{len(drop_channels) - 8} more"
        else:
            drop_channel_text = "Not set"

        ticket_channel_text = f"<#{collection['ticket_channel_id']}>" if collection.get("ticket_channel_id") else "Not set"
        staff_log_text = f"<#{staff_log_channel_id}>" if staff_log_channel_id else "Not set"

        embed.add_field(
            name="Roles",
            value=(
                f"**Admin:** {f'<@&{admin_role_id}>' if admin_role_id else 'Not set'}\n"
                f"**Mod:** {f'<@&{mod_role_id}>' if mod_role_id else 'Not set'}\n"
                f"**Staff:** {f'<@&{staff_role_id}>' if staff_role_id else 'Not set'}"
            ),
            inline=False
        )

        embed.add_field(
            name="Channels",
            value=(
                f"**Staff Log:** {staff_log_text}\n"
                f"**Ticket:** {ticket_channel_text}\n"
                f"**Drop Channels:** {drop_channel_text}"
            ),
            inline=False
        )

        embed.add_field(
            name="Toggles",
            value=(
                f"**Auto Drops:** {format_on_off(drop.get('auto_drop_enabled', True))}\n"
                f"**Event Launched:** {format_on_off(event.get('event_launched', False))}\n"
                f"**Event Drops:** {format_on_off(event.get('event_only_drops', False))}\n"
                f"**Event Boosts:** {format_on_off(event.get('event_boosts_enabled', False))}"
            ),
            inline=False
        )

    elif section in SETTING_OPTIONS:
        lines = []

        for key, meta in SETTING_OPTIONS[section]["items"].items():
            current = get_setting_current_value(snapshot, key, meta["kind"])
            lines.append(f"**{meta['label']}:** {current}{meta['suffix']}")

        embed.description = "\n".join(lines)

        if section == "rarity":
            embed.set_footer(text="Common, Rare, Epic, and Legendary should total 100.")
        else:
            embed.set_footer(text="Use the edit dropdown below to change these values.")

    elif section == "events":
        event = snapshot["event"]
        embed.description = (
            f"**Name:** {event.get('event_name', 'No Event')}\n"
            f"**Theme:** {event.get('event_theme', 'None')}\n"
            f"**Type:** {event.get('event_type', 'Seasonal')}\n"
            f"**Launched:** {format_on_off(event.get('event_launched', False))}\n"
            f"**Event Drops:** {format_on_off(event.get('event_only_drops', False))}\n"
            f"**Event Boosts:** {format_on_off(event.get('event_boosts_enabled', False))}\n"
            f"**Event Card Chance:** {event.get('event_card_chance', 10)}%"
        )
        embed.set_footer(text="Use /eventsetup for event name/theme/launch controls.")

    elif section == "collections":
        collection = snapshot["collection"]
        ticket = f"<#{collection['ticket_channel_id']}>" if collection.get("ticket_channel_id") else "Not set"
        embed.description = (
            f"**Ticket Channel:** {ticket}\n"
            f"**Completion Emoji:** {collection.get('completion_emoji') or '🎉'}"
        )

    return embed

class SettingsSectionSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Status", value="status"),
            discord.SelectOption(label="Drops", value="drops"),
            discord.SelectOption(label="Rarity", value="rarity"),
            discord.SelectOption(label="Economy", value="economy"),
            discord.SelectOption(label="Crates", value="crates"),
            discord.SelectOption(label="Events", value="events"),
            discord.SelectOption(label="Collections", value="collections"),
        ]
        super().__init__(
            placeholder="Choose a settings section...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        section = self.values[0]
        await interaction.response.edit_message(
            embed=await create_settings_embed(interaction.guild.id, section),
            view=SettingsPanelView(section)
        )

class SettingsFieldSelect(discord.ui.Select):
    def __init__(self, section):
        self.section = section
        options = [
            discord.SelectOption(label=meta["label"], value=key)
            for key, meta in SETTING_OPTIONS.get(section, {}).get("items", {}).items()
        ]
        super().__init__(
            placeholder="Choose what to edit...",
            min_values=1,
            max_values=1,
            options=options[:25]
        )

    async def callback(self, interaction: discord.Interaction):
        field = self.values[0]
        meta = SETTING_OPTIONS[self.section]["items"][field]
        snapshot = await get_settings_snapshot(interaction.guild.id)
        current = get_setting_current_value(snapshot, field, meta["kind"])

        embed = discord.Embed(
            title=f"Edit {meta['label']}",
            description=(
                f"**Current:** {current}{meta['suffix']}\n\n"
                "Choose a new value below, or press Back to return."
            ),
            color=discord.Color.from_str("#9e659d")
        )

        await interaction.response.edit_message(
            embed=embed,
            view=SettingsEditValueView(self.section, field)
        )

class SettingsValueSelect(discord.ui.Select):
    def __init__(self, section, field):
        self.section = section
        self.field = field
        meta = SETTING_OPTIONS[section]["items"][field]
        options = [
            discord.SelectOption(label=f"{value}{meta['suffix']}", value=str(value))
            for value in meta["values"]
        ]
        super().__init__(
            placeholder=f"Choose {meta['label']} value...",
            min_values=1,
            max_values=1,
            options=options[:25]
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators can edit settings.", ephemeral=True)

        value = int(self.values[0])
        meta = SETTING_OPTIONS[self.section]["items"][self.field]
        await apply_simple_setting(interaction.guild.id, self.field, meta["kind"], value)
        await send_staff_log(
            interaction.guild,
            "Setting Updated",
            f"**Setting:** {meta['label']}\n**New value:** {value}{meta['suffix']}\n**Updated by:** {interaction.user.mention}",
            discord.Color.from_str("#9e659d")
        )
        await interaction.response.edit_message(
            embed=await create_settings_embed(interaction.guild.id, self.section),
            view=SettingsPanelView(self.section)
        )

class SettingsBackButton(discord.ui.Button):
    def __init__(self, target_section):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.target_section = target_section

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=await create_settings_embed(interaction.guild.id, self.target_section),
            view=SettingsPanelView(self.target_section)
        )

class SettingsPanelView(discord.ui.View):
    def __init__(self, section="status"):
        super().__init__(timeout=300)
        self.section = section
        if section == "status":
            self.add_item(SettingsSectionSelect())
        else:
            self.add_item(SettingsBackButton("status"))
            if section in SETTING_OPTIONS:
                self.add_item(SettingsFieldSelect(section))

class SettingsEditValueView(discord.ui.View):
    def __init__(self, section, field):
        super().__init__(timeout=300)
        self.add_item(SettingsBackButton(section))
        self.add_item(SettingsValueSelect(section, field))

@bot.tree.command(name="settings", description="Admin only: view and edit bot settings.")
@app_commands.default_permissions(administrator=True)
async def settings(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use settings.", ephemeral=True)

    await interaction.response.send_message(embed=await create_settings_embed(interaction.guild.id, "status"), view=SettingsPanelView("status"), ephemeral=True)

@bot.tree.command(name="hideset", description="Admin only: hide a collection set from users.")
@app_commands.default_permissions(administrator=True)
@app_commands.autocomplete(set_name=card_set_autocomplete)
async def hideset(interaction: discord.Interaction, set_name: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    card_set = await get_card_set_by_ref(interaction.guild.id, set_name)

    if not card_set:
        return await interaction.response.send_message("Set not found.", ephemeral=True)

    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE card_sets SET is_active=FALSE WHERE guild_id=$1 AND id=$2",
            interaction.guild.id,
            card_set["id"]
        )

    await interaction.response.send_message(f"Hidden **{card_set['name']}**.", ephemeral=True)

@bot.tree.command(name="showset", description="Admin only: show a hidden collection set again.")
@app_commands.default_permissions(administrator=True)
async def showset(interaction: discord.Interaction, set_name: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE card_sets SET is_active=TRUE WHERE guild_id=$1 AND LOWER(name)=LOWER($2) RETURNING *",
            interaction.guild.id,
            set_name
        )

    if not row:
        return await interaction.response.send_message("Hidden set not found.", ephemeral=True)

    await interaction.response.send_message(f"Restored **{row['name']}**.", ephemeral=True)

class BurnCardConfirmView(discord.ui.View):
    def __init__(self, card_id, card_name, admin_id):
        super().__init__(timeout=60)
        self.card_id = int(card_id)
        self.card_name = card_name
        self.admin_id = admin_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.admin_id:
            await interaction.response.send_message("Only the admin who started this burn can confirm it.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Burn Card Forever", style=discord.ButtonStyle.danger)
    async def confirm_burn(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                for query in [
                    "DELETE FROM inventory WHERE card_id=$1",
                    "DELETE FROM card_set_cards WHERE card_id=$1",
                    "DELETE FROM active_trades WHERE your_card_id=$1 OR their_card_id=$1",
                ]:
                    try:
                        await conn.execute(query, self.card_id)
                    except Exception:
                        pass

                await conn.execute("DELETE FROM cards WHERE id=$1", self.card_id)

        await send_staff_log(
            interaction.guild,
            "Card Burned",
            f"**Card:** {self.card_name} (`{self.card_id}`)\n**Burned by:** {interaction.user.mention}\nThis removed the card from all inventories and bot data.",
            discord.Color.red()
        )

        embed = discord.Embed(
            title="🔥 Card Burned",
            description=f"**{self.card_name}** has been permanently burned from all bot data.",
            color=discord.Color.red()
        )

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_burn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Burn cancelled.", embed=None, view=None)

@bot.tree.command(name="burncard", description="Admin only: permanently delete a card from all bot data.")
@app_commands.default_permissions(administrator=True)
@app_commands.autocomplete(card=active_card_autocomplete)
async def burncard(interaction: discord.Interaction, card: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    card_row = await get_card_by_ref(card)

    if not card_row:
        return await interaction.response.send_message("Card not found.", ephemeral=True)

    embed = discord.Embed(
        title="⚠️ Confirm Card Burn",
        description=(
            f"You are about to permanently burn **{card_row['name']}** (`{card_row['id']}`).\n\n"
            "**This will remove it from:**\n"
            "• all user inventories\n"
            "• all sets\n"
            "• all future drops\n"
            "• bot card data\n\n"
            "This cannot be undone."
        ),
        color=discord.Color.red()
    )

    await interaction.response.send_message(
        embed=embed,
        view=BurnCardConfirmView(card_row["id"], card_row["name"], interaction.user.id),
        ephemeral=True
    )

@bot.tree.command(name="givecard", description="Admin only: give a card directly to a user.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(user="User receiving the card", card="Card to give")
@app_commands.autocomplete(card=active_card_autocomplete)
async def givecard(interaction: discord.Interaction, user: discord.Member, card: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only administrators can use this command.", ephemeral=True)

    card_row = await get_card_by_ref(card)

    if not card_row:
        return await interaction.response.send_message("Card not found.", ephemeral=True)

    await add_card_to_inventory(user.id, card_row["id"])
    await notify_completed_sets(interaction, user.id)

    await send_staff_log(
        interaction.guild,
        "Card Given",
        f"**User:** {user.mention}\n**Card:** {card_row['name']} (`{card_row['id']}`)\n**Given by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

    embed = discord.Embed(
        title="Card Given",
        description=f"Gave **{card_row['name']}** to {user.mention}.",
        color=discord.Color.from_str("#9e659d")
    )

    await interaction.followup.send(embed=embed, ephemeral=True) if interaction.response.is_done() else await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setadminrole", description="Admin only: set the bot admin role for this server.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(role="Bot admin role")
async def setadminrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only server administrators can set admin roles.", ephemeral=True)

    await set_admin_role_db(interaction.guild.id, role.id)

    await send_staff_log(
        interaction.guild,
        "Admin Role Updated",
        f"**Role:** {role.mention}\n**Updated by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(f"Admin role set to {role.mention}.", ephemeral=True)

@bot.tree.command(name="setmodrole", description="Admin only: set the moderator role for this server.")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(role="Moderator role")
async def setmodrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Only server administrators can set moderator roles.", ephemeral=True)

    await set_mod_role_db(interaction.guild.id, role.id)

    await send_staff_log(
        interaction.guild,
        "Mod Role Updated",
        f"**Role:** {role.mention}\n**Updated by:** {interaction.user.mention}",
        discord.Color.from_str("#9e659d")
    )

    await interaction.response.send_message(f"Mod role set to {role.mention}.", ephemeral=True)

# ---------------- RUN ----------------
bot.run(TOKEN)
