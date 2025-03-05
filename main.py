import os
import requests
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH

# Replace with your API ID, API Hash, and Bot Token
API_ID = "21705536"
API_HASH = "c5bb241f6e3ecf33fe68a444e288de2d"
BOT_TOKEN = "7567433221:AAHrGstAQZY9lE-E5Pk4ceLNqWtfwbIKzVE"

# Input data
keys = [
    "a3ff00254489970a439bf7a8192c8207:74827d99e9d3994425e15bbcc0dd1ffa",
    "52e395c04a3d587bd7839bc372ad136f:ec1bd0939dc47b6d872f4c010249ef0b",
    "8d602a0e5a46f6502572396449f39dc9:df4c54d800032371c264cdf5bec807e7"
]
pssh = "AAAAXHBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAADwSEI1gKg5aRvZQJXI5ZEnznckSEFLjlcBKPVh714Obw3KtE28SEKP/ACVEiZcKQ5v3qBksggdI49yVmwY="

# Initialize Widevine CDM
device = Device.load("device_private_key")  # Replace with your device private key
cdm = Cdm.from_device(device)

# Parse PSSH
pssh_obj = PSSH(pssh)

# Function to download and decrypt video
def download_and_decrypt_video(mpd_url, output_file):
    try:
        # Get license (replace with actual license server URL)
        license_url = "https://india-drm.sdmc.tv/getlicense?token=eyJzZWNyZXRfaWQiOiJPMU0zVVMzRERNOUwyOUcxNVNDTlVMSjE2MjdDTkE1UyIsImRybV9zeXN0ZW0iOiJXSURFVklORSIsInVpZCI6IjkyOTkzMjAwMzkzMjY0NDE4NDQxIiwiY2lkIjoiZTA2ZmJkMjRjZDljMTM2YzVmMGVjMDRhYmFmM2FlYzYiLCJ0aW1lc3RhbXAiOjE3NDEyMDg0NzUsImhhc2giOiI3cjJNMncxWUthb01VM0grY3ZDVDhGN0dWbmVZa21zaFFJc2t3R2FndXVrPSIsInBvbGljeSI6Ik94a3FrYW8vb1diMEdwd2NVZUttQ0hyeXROK2FGaDJDbjM2NjlUWUtqeUNNdlJLRmdhUzEwRnNwUTdaSTdPNlJGbmt4cjB5bzhuNEExcXh5cHFMUHVJa1FCdmxDTnlrWHV1Q05RaFZnaWtpSlVvZ21pSUpMN2pOdzRjTllwR1hZOHo3RzVXWG5BR01GYTJtN1k5N1U1Y1N1aExoMnpLcGhqK1JSNitlT0tKdz0ifQ=="  # Replace with the actual license server URL
        challenge = cdm.get_license_challenge(pssh_obj)
        response = requests.post(license_url, data=challenge)
        license = cdm.parse_license(response.content)

        # Decrypt keys
        decrypted_keys = {}
        for key in keys:
            key_id, key_value = key.split(":")
            decrypted_key = cdm.decrypt(key_id, key_value)
            decrypted_keys[key_id] = decrypted_key

        # Generate a key file for decryption
        key_file = "keys.txt"
        with open(key_file, "w") as f:
            for key_id, key_value in decrypted_keys.items():
                f.write(f"{key_id}:{key_value}\n")

        # Download and decrypt the video using ffmpeg
        ffmpeg_command = f'ffmpeg -i "{mpd_url}" -c copy -encryption_key_file "{key_file}" "{output_file}"'
        subprocess.run(ffmpeg_command, shell=True, check=True)

        # Clean up the key file
        os.remove(key_file)
        return True
    except Exception as e:
        print(f"Error downloading and decrypting video: {e}")
        return False

# Initialize Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command handler
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(
        "Welcome! Send me the MPD URL of the video you want to download."
    )

# Handle MPD URL from user
@app.on_message(filters.text & ~filters.command)
async def handle_url(client: Client, message: Message):
    url = message.text
    if not url.endswith(".mpd"):
        await message.reply_text("Please send a valid MPD URL.")
        return

    # Inform the user that the download is starting
    await message.reply_text("Downloading and decrypting video... Please wait.")

    # Download and decrypt the video
    output_file = "downloaded_video.mp4"
    if download_and_decrypt_video(url, output_file):
        # Send the downloaded video to the user
        await message.reply_video(video=output_file, caption="Here's your video!")
        # Clean up the downloaded file
        os.remove(output_file)
    else:
        await message.reply_text("Failed to download and decrypt the video. Please check the URL and try again.")

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
