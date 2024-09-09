from speedtest import Speedtest, ConfigRetrievalError
from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import bot, LOGGER
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.status_utils import get_readable_file_size
from bot.helper.telegram_helper.message_utils import (
    send_message,
    delete_message,
    edit_message,
)


@new_task
async def speedtest(_, message):
    initial_msg = await send_message(message, "🚀 <i>Running a speed check...</i>")
    try:
        test = Speedtest()
    except ConfigRetrievalError:
        await edit_message(initial_msg, "⚠️ <b>Error:</b> <i>Unable to reach the server. Please retry later.</i>")
        return

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    image_url = result['share']

    speed_info = f"""
<b>🌐 Speed Test Summary</b>

📊 <b>Performance Metrics</b>
━━━━━━━━━━━━━━
<b>↗️ Upload Speed:</b> <code>{get_readable_file_size(result['upload'] / 8)}/s</code>
<b>↘️ Download Speed:</b> <code>{get_readable_file_size(result['download'] / 8)}/s</code>
<b>🕒 Ping:</b> <code>{result['ping']} ms</code>
<b>📅 Timestamp:</b> <code>{result['timestamp']}</code>
<b>⬆️ Data Sent:</b> <code>{get_readable_file_size(int(result['bytes_sent']))}</code>
<b>⬇️ Data Received:</b> <code>{get_readable_file_size(int(result['bytes_received']))}</code>

🖥️ <b>Server Details</b>
━━━━━━━━━━━━━━
<b>📍 Location:</b> <code>{result['server']['name']}, {result['server']['country']}</code>
<b>🏢 Sponsor:</b> <code>{result['server']['sponsor']}</code>
<b>⏱️ Latency:</b> <code>{result['server']['latency']} ms</code>

👤 <b>Client Information</b>
━━━━━━━━━━━━━━
<b>🌍 IP Address:</b> <code>{result['client']['ip']}</code>
<b>🌐 ISP:</b> <code>{result['client']['isp']} (Rating: {result['client']['isprating']})</code>
"""

    try:
        await send_message(message, speed_info, photo=image_url)
        await delete_message(initial_msg)
    except Exception as e:
        LOGGER.error(f"Error while sending speedtest data: {str(e)}")
        await edit_message(initial_msg, speed_info)


bot.add_handler(
    MessageHandler(
        speedtest,
        filters=command(BotCommands.SpeedCommand) & CustomFilters.authorized,
    )
)