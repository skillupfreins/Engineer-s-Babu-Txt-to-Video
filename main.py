import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess
import urllib.parse
import yt_dlp
import cloudscraper
import m3u8
import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

my_name = "𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚"

cookies_file_path = os.getenv("COOKIES_FILE_PATH", "youtube_cookies.txt")
# Sudo (Owner) ID
SUDO_USERS = [123456789]  # Replace with your Telegram ID

# Data storage for authorized users, channels, and groups
AUTHORIZED_USERS = set()
AUTHORIZED_CHANNELS = set()
AUTHORIZED_GROUPS = set()

# Load authorized data from file (if exists)
if os.path.exists("authorized_data.json"):
    with open("authorized_data.json", "r") as f:
        data = json.load(f)
        AUTHORIZED_USERS = set(data.get("users", []))
        AUTHORIZED_CHANNELS = set(data.get("channels", []))
        AUTHORIZED_GROUPS = set(data.get("groups", []))

# Save authorized data to file
def save_authorized_data():
    data = {
        "users": list(AUTHORIZED_USERS),
        "channels": list(AUTHORIZED_CHANNELS),
        "groups": list(AUTHORIZED_GROUPS)
    }
    with open("authorized_data.json", "w") as f:
        json.dump(data, f)

# Check if user is authorized
def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS or user_id in SUDO_USERS

# Check if channel is authorized
def is_authorized_channel(channel_id):
    return channel_id in AUTHORIZED_CHANNELS

# Check if group is authorized
def is_authorized_group(group_id):
    return group_id in AUTHORIZED_GROUPS

# Add user command
@bot.on_message(filters.command("adduser") & filters.user(SUDO_USERS))
async def add_user(client: Client, msg: Message):
    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
        AUTHORIZED_USERS.add(user_id)
        save_authorized_data()
        await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "success" sticker
        await msg.reply_text(f"User {user_id} has been added to the authorized list.")
    else:
        await msg.reply_text("Please reply to a user's message to add them.")

# Remove user command
@bot.on_message(filters.command("removeuser") & filters.user(SUDO_USERS))
async def remove_user(client: Client, msg: Message):
    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
        if user_id in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(user_id)
            save_authorized_data()
            await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "removed" sticker
            await msg.reply_text(f"User {user_id} has been removed from the authorized list.")
        else:
            await msg.reply_text("User is not in the authorized list.")
    else:
        await msg.reply_text("Please reply to a user's message to remove them.")

# Add channel command
@bot.on_message(filters.command("addchannel") & filters.user(SUDO_USERS))
async def add_channel(client: Client, msg: Message):
    try:
        channel_id = int(msg.text.split()[1])
        AUTHORIZED_CHANNELS.add(channel_id)
        save_authorized_data()
        await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "success" sticker
        await msg.reply_text(f"Channel {channel_id} has been added to the authorized list.")
    except:
        await msg.reply_text("Invalid channel ID.")

# Remove channel command
@bot.on_message(filters.command("removechannel") & filters.user(SUDO_USERS))
async def remove_channel(client: Client, msg: Message):
    try:
        channel_id = int(msg.text.split()[1])
        if channel_id in AUTHORIZED_CHANNELS:
            AUTHORIZED_CHANNELS.remove(channel_id)
            save_authorized_data()
            await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "removed" sticker
            await msg.reply_text(f"Channel {channel_id} has been removed from the authorized list.")
        else:
            await msg.reply_text("Channel is not in the authorized list.")
    except:
        await msg.reply_text("Invalid channel ID.")

# Add group command
@bot.on_message(filters.command("addgroup") & filters.user(SUDO_USERS))
async def add_group(client: Client, msg: Message):
    try:
        group_id = int(msg.text.split()[1])
        AUTHORIZED_GROUPS.add(group_id)
        save_authorized_data()
        await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "success" sticker
        await msg.reply_text(f"Group {group_id} has been added to the authorized list.")
    except:
        await msg.reply_text("Invalid group ID.")

# Remove group command
@bot.on_message(filters.command("removegroup") & filters.user(SUDO_USERS))
async def remove_group(client: Client, msg: Message):
    try:
        group_id = int(msg.text.split()[1])
        if group_id in AUTHORIZED_GROUPS:
            AUTHORIZED_GROUPS.remove(group_id)
            save_authorized_data()
            await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "removed" sticker
            await msg.reply_text(f"Group {group_id} has been removed from the authorized list.")
        else:
            await msg.reply_text("Group is not in the authorized list.")
    except:
        await msg.reply_text("Invalid group ID.")

# List users command
@bot.on_message(filters.command("userlist") & filters.user(SUDO_USERS))
async def list_users(client: Client, msg: Message):
    if AUTHORIZED_USERS:
        users_list = "\n".join([f"User ID: {user_id}" for user_id in AUTHORIZED_USERS])
        await msg.reply_text(f"Authorized Users:\n{users_list}")
    else:
        await msg.reply_text("No authorized users.")

# List channels command
@bot.on_message(filters.command("channellist") & filters.user(SUDO_USERS))
async def list_channels(client: Client, msg: Message):
    if AUTHORIZED_CHANNELS:
        channels_list = "\n".join([f"Channel ID: {channel_id}" for channel_id in AUTHORIZED_CHANNELS])
        await msg.reply_text(f"Authorized Channels:\n{channels_list}")
    else:
        await msg.reply_text("No authorized channels.")

# List groups command
@bot.on_message(filters.command("grouplist") & filters.user(SUDO_USERS))
async def list_groups(client: Client, msg: Message):
    if AUTHORIZED_GROUPS:
        groups_list = "\n".join([f"Group ID: {group_id}" for group_id in AUTHORIZED_GROUPS])
        await msg.reply_text(f"Authorized Groups:\n{groups_list}")
    else:
        await msg.reply_text("No authorized groups.")

# Help command
@bot.on_message(filters.command("help"))
async def help_command(client: Client, msg: Message):
    help_text = (
        "🌟 **Available Commands** 🌟\n\n"
        "/start - Start the bot\n"
        "/engineer or /upload - Download and upload files (Authorized only)\n"
        "/adduser - Add a user (Sudo only)\n"
        "/removeuser - Remove a user (Sudo only)\n"
        "/addchannel - Add a channel (Sudo only)\n"
        "/removechannel - Remove a channel (Sudo only)\n"
        "/addgroup - Add a group (Sudo only)\n"
        "/removegroup - Remove a group (Sudo only)\n"
        "/userlist - List authorized users (Sudo only)\n"
        "/channellist - List authorized channels (Sudo only)\n"
        "/grouplist - List authorized groups (Sudo only)\n"
        "/help - Show this help message"
    )
    await msg.reply_text(help_text)
# Define aiohttp routes
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("https://text-leech-bot-for-render.onrender.com/")

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def start_bot():
    await bot.start()
    print("Bot is up and running")

async def stop_bot():
    await bot.stop()

async def main():
    if WEBHOOK:
        # Start the web server
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        site = web.TCPSite(app_runner, "0.0.0.0", PORT)
        await site.start()
        print(f"Web server started on port {PORT}")

    # Start the bot
    await start_bot()

    # Keep the program running
    try:
        while True:
            await bot.polling()  # Run forever, or until interrupted
    except (KeyboardInterrupt, SystemExit):
        await stop_bot()
    

async def start_bot():
    await bot.start()
    print("Bot is up and running")

async def stop_bot():
    await bot.stop()

async def main():
    if WEBHOOK:
        # Start the web server
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        site = web.TCPSite(app_runner, "0.0.0.0", PORT)
        await site.start()
        print(f"Web server started on port {PORT}")

    # Start the bot
    await start_bot()

    # Keep the program running
    try:
        while True:
            await asyncio.sleep(3600)  # Run forever, or until interrupted
    except (KeyboardInterrupt, SystemExit):
        await stop_bot()
        
class Data:
    START = (
        "🌟 Welcome {0}! 🌟\n\n"
    )
# Define the start command handler
@bot.on_message(filters.command("start"))
async def start(client: Client, msg: Message):
    user = await client.get_me()
    mention = user.mention
    start_message = await client.send_message(
        msg.chat.id,
        Data.START.format(msg.from_user.mention)
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Initializing Uploader bot... 🤖\n\n"
        "Progress: [⬜⬜⬜⬜⬜⬜⬜⬜⬜] 0%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Loading features... ⏳\n\n"
        "Progress: [🟥🟥🟥⬜⬜⬜⬜⬜⬜] 25%\n\n"
    )
    
    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "This may take a moment, sit back and relax! 😊\n\n"
        "Progress: [🟧🟧🟧🟧🟧⬜⬜⬜⬜] 50%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Checking Bot Status... 🔍\n\n"
        "Progress: [🟨🟨🟨🟨🟨🟨🟨⬜⬜] 75%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Checking status Ok... Command Nhi Bataunga **Bot Made BY 𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚™👨🏻‍💻**🔍\n\n"
        "Progress:[🟩🟩🟩🟩🟩🟩🟩🟩🟩] 100%\n\n"
    )

@bot.on_message(filters.command(["stop"]) )
async def restart_handler(_, m):
    await m.reply_text("**STOPPED**🛑", True)
    os.execl(sys.executable, sys.executable, *sys.argv)


# Engineer/Upload command handler
@bot.on_message(filters.command(["engineer", "upload"]))
async def engineer_upload(client: Client, msg: Message):
    # Check authorization
    if not (is_authorized(msg.from_user.id) or is_authorized_channel(msg.chat.id) or is_authorized_group(msg.chat.id)):
        await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "denied" sticker
        await msg.reply_text("You are not authorized to use this command.")
        return

    editable = await msg.reply_text("🔹 Hi, I am a Powerful TXT Downloader Bot. Send me the TXT file and wait.")
    input: Message = await bot.listen(msg.chat.id)
    x = await input.download()
    await input.delete(True)

    file_name, ext = os.path.splitext(os.path.basename(x))
    credit = "𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚™"

    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = [i.split("://", 1) for i in content]
        os.remove(x)
    except Exception as e:
        await msg.reply_text(f"Invalid file input. Error: {e}")
        os.remove(x)
        return
   
    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download initial is **1**")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
    try:
        arg = int(raw_text)
    except:
        arg = 1

    if raw_text == "1":
        file_name_without_ext = os.path.splitext(file_name)[0]
        fancy_batch_name = f"𝐁𝐚𝐭𝐜𝐡 𝐍𝐚𝐦𝐞: 𝗤𝘂𝗮𝗹𝗶𝘁𝘆".replace("𝗤𝘂𝗮𝗹𝗶𝘁𝘆", file_name_without_ext)
        
        name_message = await bot.send_message(
            m.chat.id,
            f"📌 **Batch Name Pinned!** 📌\n"
            f"🎨 {fancy_batch_name}\n"
            f"✨ Stay organized with your pinned batches 🚀!"
        )
        await bot.pin_chat_message(m.chat.id, name_message.id)
        await asyncio.sleep(2)  # Wait for 2 seconds before proceeding

        
    await editable.edit("**Enter Your Batch Name or send d for grabing from text filename.**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == 'd':
        b_name = file_name
    else:
        b_name = raw_text0

    await editable.edit("**Enter resolution.\n Eg : 480 or 720**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "144x256"
        elif raw_text2 == "240":
            res = "240x426"
        elif raw_text2 == "360":
            res = "360x640"
        elif raw_text2 == "480":
            res = "480x854"
        elif raw_text2 == "720":
            res = "720x1280"
        elif raw_text2 == "1080":
            res = "1080x1920" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
    
    await editable.edit("**Enter Your Name or send 'de' for use default.\n Eg : 𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚™👨🏻‍💻**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    if raw_text3 == 'de':
        CR = credit
    else:
        CR = raw_text3
        
    await editable.edit("**Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋  or send 'Not' for use default**")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)
    if raw_text4 == 'not':
        MR = token
    else:
        MR = raw_text4
        
    await editable.edit("Now send the **Thumb url**\n**Eg :** ``\n\nor Send `no`")
    input6 = message = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb == "no"

    count =int(raw_text)    
    try:
        for i in range(arg-1, len(links)):

            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'
                

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif 'media-cdn.classplusapp.com/drm/' in url:
                url = f"https://www.masterapi.tech/get/cp/dl?url={url}"
                
            elif 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url or "media-cdn-alisg.classplusapp.com" in url or "videos.classplusapp" in url or "videos.classplusapp.com" in url or "media-cdn-a.classplusapp" in url or "media-cdn.classplusapp" in url or "alisg-cdn-a.classplusapp" in url:
             url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9r'}).json()['url']

            elif "apps-s3-jw-prod.utkarshapp.com" in url:
                if 'enc_plain_mp4' in url:
                    url = url.replace(url.split("/")[-1], res+'.mp4')
                    
                elif 'Key-Pair-Id' in url:
                    url = None
                    
                elif '.m3u8' in url:
                    q = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).split("/")[0]
                    x = url.split("/")[5]
                    x = url.replace(x, "")
                    url = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).replace(q+"/", x)

            elif '/master.mpd' in url:
             vid_id =  url.split("/")[-2]
             url =  f"https://madxapi-d0cbf6ac738c.herokuapp.com/{vid_id}/master.m3u8?token={raw_text4}"

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]} {my_name}'

            if "appx" in url:
                url = f"https://dragoapi.vercel.app/pdf/{url}"
            elif "appx-recordings-mcdn.akamai.net.in/drm/" in url:
                cmd = f'ffmpeg -i "{url}" -c copy -bsf:a aac_adtstoasc "{name}.mp4"'
            elif "arvind" in url:
                cmd = f'ffmpeg -i "{url}" -c copy -bsf:a aac_adtstoasc "{name}.mp4"'
                
            if '/do' in url:               
               pdf_id = url.split("/")[-1].split(".pdf")[0]
               print(pdf_id)
               url = f"https://kgs-v2.akamaized.net/kgs/do/pdfs/{pdf_id}.pdf"
               
            if 'sec-prod-mediacdn.pw.live' in url:
             vid_id = url.split("sec-prod-mediacdn.pw.live/")[1].split("/")[0]
             url = f"https://pwplayer-0e2dbbdc0989.herokuapp.com/player?url=https://d1d34p8vz63oiq.cloudfront.net/{vid_id}/master.mpd?token={raw_text4}"
   
            if 'bitgravity.com' in url:               
               parts = url.split('/')               
               part1 = parts[1]
               part2 = parts[2]
               part3 = parts[3] 
               part4 = parts[4]
               part5 = parts[5]
               part6 = parts[6]
               
               print(f"PART1: {part1}")
               print(f"PART2: {part2}")
               print(f"PART3: {part3}")
               print(f"PART4: {part4}")
               print(f"PART5: {part5}")
               print(f"PART6: {part6}")
               url = f"https://kgs-v2.akamaized.net/{part3}/{part4}/{part5}/{part6}"

            if '?list' in url:
               video_id = url.split("/embed/")[1].split("?")[0]
               print(video_id)
               url = f"https://www.youtube.com/embed/{video_id}"
                
            
            if 'workers.dev' in url:
             vid_id = url.split("cloudfront.net/")[1].split("/")[0]
             print(vid_id)
             url = f"https://madxapi-d0cbf6ac738c.herokuapp.com/{vid_id}/master.m3u8?token={raw_text4}"
                
            if 'psitoffers.store' in url:
             vid_id = url.split("vid=")[1].split("&")[0]
             print(f"vid_id = {vid_id}")
             url =  f"https://madxapi-d0cbf6ac738c.herokuapp.com/{vid_id}/master.m3u8?token={raw_text4}"

            if "edge.api.brightcove.com" in url:
                bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
                url = url.split("bcov_auth")[0]+bcov
                
            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
            
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'

            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:  
                
                cc = f'**🎞️ VID_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} {my_name} {res}.mkv\n\n📚 Batch Name: {b_name}\n\n📥 Extracted By : {CR}\n\n**━━━━━✦{my_name}✦━━━━━**'
                cc1 = f'**📁 PDF_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} {my_name}.pdf\n\n📚 Batch Name: {b_name}\n\n📥 Extracted By : {CR}\n\n**━━━━━✦{my_name}✦━━━━━**'
                    
                
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif ".pdf" in url:
                    try:
                        await asyncio.sleep(4)
        # Replace spaces with %20 in the URL
                        url = url.replace(" ", "%20")
 
        # Create a cloudscraper session
                        scraper = cloudscraper.create_scraper()

        # Send a GET request to download the PDF
                        response = scraper.get(url)

        # Check if the response status is OK
                        if response.status_code == 200:
            # Write the PDF content to a file
                            with open(f'{name}.pdf', 'wb') as file:
                                file.write(response.content)

            # Send the PDF document
                            await asyncio.sleep(4)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            count += 1

            # Remove the PDF file after sending
                            os.remove(f'{name}.pdf')
                        else:
                            await m.reply_text(f"Failed to download PDF: {response.status_code} {response.reason}")

                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif ".pdf" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue                       
                          
                else:
                    Show = f"📥 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 »\n\n📝 Title:- `{name}\n\n**🔗 𝐓𝐨𝐭𝐚𝐥 𝐔𝐑𝐋 »** ✨{len(links)}✨\n\n⌨ 𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {raw_text2}`\n\n**𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ 𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚"
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(
                    f"⌘ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐈𝐧𝐭𝐞𝐫𝐮𝐩𝐭𝐞𝐝 ❌ \n\n⌘ 𝐍𝐚𝐦𝐞 » {name}\n⌘ 𝐋𝐢𝐧𝐤 » `{url}`"
                )
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("**✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐃𝐨𝐧𝐞**")
