import asyncio
import os
import signal
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler

TARGET_BOT_USERNAME = "eeveedecrypterbot"
APP_STORE_LINK = "https://apps.apple.com/app/id995999703"


SESSION_FILE = "user_session"  # encrypted session file

async def handle_message(client, message):
    """Handle incoming messages from the target bot."""
    if message.chat.username == TARGET_BOT_USERNAME and message.document:
        print(f"Document received: {message.document.file_name}")
        await message.download("Agario.ipa")
        print("File downloaded!")
        client._should_stop.set()

async def main():
    """Main function to send a message and wait for the response."""
    app = Client(SESSION_FILE)

    # Add the message handler
    app.add_handler(MessageHandler(handle_message, filters=filters.document))

    # Start the client
    await app.start()

    app._should_stop = asyncio.Event()

    # Send the App Store link to the bot
    print(f"Sending message to {TARGET_BOT_USERNAME}...")
    await app.send_message(f"@{TARGET_BOT_USERNAME}", APP_STORE_LINK)
    print("Message sent. Waiting for the response...")

    # Keep the client running to process messages
    try:
        await asyncio.wait_for(app._should_stop.wait(), timeout=10 * 60)
    except asyncio.TimeoutError:
        print("Timed out after 10 minutes. Killing the task.")
        os.kill(os.getpid(), signal.SIGINT)
    finally:
        await app.stop()
        print("Client stopped. Exiting.")

if __name__ == "__main__":
    asyncio.run(main())
