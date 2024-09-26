from html import escape
from psutil import virtual_memory, cpu_percent, disk_usage
from time import time
from asyncio import iscoroutinefunction

from bot import (
    DOWNLOAD_DIR,
    task_dict,
    task_dict_lock,
    botStartTime,
    config_dict,
    status_dict,
)
from .bot_utils import sync_to_async
from ..telegram_helper.bot_commands import BotCommands
from ..telegram_helper.filters import CustomFilters
from ..telegram_helper.button_build import ButtonMaker

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]

class MirrorStatus:
    STATUS_UPLOADING = "Upload"
    STATUS_DOWNLOADING = "Download"
    STATUS_CLONING = "Clone"
    STATUS_QUEUEDL = "QueueDl"
    STATUS_QUEUEUP = "QueueUp"
    STATUS_PAUSED = "Pause"
    STATUS_ARCHIVING = "Archive️"
    STATUS_EXTRACTING = "Extract"
    STATUS_SPLITTING = "Split"
    STATUS_CHECKING = "CheckUp"
    STATUS_SEEDING = "Seed"
    STATUS_SAMVID = "SamVid"
    STATUS_CONVERTING = "Convert"

STATUSES = {
    "ALL": "All",
    "DL": MirrorStatus.STATUS_DOWNLOADING,
    "UP": MirrorStatus.STATUS_UPLOADING,
    "QD": MirrorStatus.STATUS_QUEUEDL,
    "QU": MirrorStatus.STATUS_QUEUEUP,
    "AR": MirrorStatus.STATUS_ARCHIVING,
    "EX": MirrorStatus.STATUS_EXTRACTING,
    "SD": MirrorStatus.STATUS_SEEDING,
    "CM": MirrorStatus.STATUS_CONVERTING,
    "CL": MirrorStatus.STATUS_CLONING,
    "SP": MirrorStatus.STATUS_SPLITTING,
    "CK": MirrorStatus.STATUS_CHECKING,
    "SV": MirrorStatus.STATUS_SAMVID,
    "PA": MirrorStatus.STATUS_PAUSED,
}


async def get_task_by_gid(gid: str):
    async with task_dict_lock:
        for tk in task_dict.values():
            if hasattr(tk, "seeding"):
                await sync_to_async(tk.update)
            if tk.gid() == gid:
                return tk
        return None

def get_specific_tasks(status, user_id):
    if status == "All":
        if user_id:
            return [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        else:
            return list(task_dict.values())
    elif user_id:
        return [
            tk
            for tk in task_dict.values()
            if tk.listener.user_id == user_id
            and (
                (st := tk.status())
                and st == status
                or status == MirrorStatus.STATUS_DOWNLOADING
                and st not in STATUSES.values()
            )
        ]
    else:
        return [
            tk
            for tk in task_dict.values()
            if (st := tk.status())
            and st == status
            or status == MirrorStatus.STATUS_DOWNLOADING
            and st not in STATUSES.values()
        ]


async def get_all_tasks(req_status: str, user_id):
    async with task_dict_lock:
        return await sync_to_async(get_specific_tasks, req_status, user_id)


def get_readable_file_size(size_in_bytes):
    if not size_in_bytes:
        return "0B"

    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1

    return f"{size_in_bytes:.2f}{SIZE_UNITS[index]}"

def get_readable_time(seconds: int):
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    return result

def time_to_seconds(time_duration):
    hours, minutes, seconds = map(int, time_duration.split(":"))
    return hours * 3600 + minutes * 60 + seconds

def speed_string_to_bytes(size_text: str):
    size = 0
    size_text = size_text.lower()
    if "k" in size_text:
        size += float(size_text.split("k")[0]) * 1024
    elif "m" in size_text:
        size += float(size_text.split("m")[0]) * 1048576
    elif "g" in size_text:
        size += float(size_text.split("g")[0]) * 1073741824
    elif "t" in size_text:
        size += float(size_text.split("t")[0]) * 1099511627776
    elif "b" in size_text:
        size += float(size_text.split("b")[0])
    return size

def get_progress_bar_string(pct):
    pct = float(pct.strip("%"))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = "█" * cFull
    p_str += "░️" * (12 - cFull)
    return f"{p_str}"

async def get_readable_message(sid, is_user, page_no=1, status="All", page_step=1):
    msg = ""
    button = None

    tasks = await sync_to_async(get_specific_tasks, status, sid if is_user else None)

    STATUS_LIMIT = config_dict["STATUS_LIMIT"]
    tasks_no = len(tasks)
    pages = (max(tasks_no, 1) + STATUS_LIMIT - 1) // STATUS_LIMIT
    if page_no > pages:
        page_no = (page_no - 1) % pages + 1
        status_dict[sid]["page_no"] = page_no
    elif page_no < 1:
        page_no = pages - (abs(page_no) % pages)
        status_dict[sid]["page_no"] = page_no
    start_position = (page_no - 1) * STATUS_LIMIT

    for index, task in enumerate(
        tasks[start_position : STATUS_LIMIT + start_position], start=1
    ):
        tstatus = await sync_to_async(task.status) if status == "All" else status
        user_tag = task.listener.tag.replace("@", "").replace("_", " ")
        cancel_task = (f"<b>/{BotCommands.CancelTaskCommand}_{task.gid()}</b>")
        if config_dict['SAFE_MODE']:
          msg += f"<pre>{tstatus}: {task.safemode_msg}..</pre>"
        else:
          msg = (
            f"<pre><a href='{task.listener.message.link}'>{tstatus}</a>: "
            f"{escape(f'{task.name()}')}</pre>"
            )
        if tstatus not in [
            MirrorStatus.STATUS_SEEDING,
            MirrorStatus.STATUS_QUEUEUP,
            MirrorStatus.STATUS_QUEUEDL,
            MirrorStatus.STATUS_CONVERTING
        ]:
            progress = (
                await task.progress()
                if iscoroutinefunction(task.progress)
                else task.progress()
            )
            msg += (
                f"\n{get_progress_bar_string(progress)} » <b><i>{progress}</i></b>"
                f"\n<code>Size   :</code> {task.size()}"
                f"\n<code>Done   :</code> {task.processed_bytes()}"
                f"\n<code>Speed  :</code> {task.speed()}"
                f"\n<code>Engine :</code> {task.engine}"
                f"\n<code>ETA    :</code> {task.eta()}"
                f"\n<code>User   :</code> {user_tag}"
                f"\n<code>UserID :</code> {task.listener.message.from_user.id}"
            )
            if hasattr(task, "seeders_num"):
                try:
                    msg += (
                        f"\n<code>Seeders:</code> {task.seeders_num()}"
                        f"\n<code>Leechers:</code> {task.leechers_num()}"
                    )
                except:
                    pass
        elif tstatus == MirrorStatus.STATUS_SEEDING:
            msg += (
                f"\n<code>Size   :</code> {task.size()}"
                f"\n<code>Speed  :</code> {task.seed_speed()}"
                f"\n<code>Uploaded:</code> {task.uploaded_bytes()}"
                f"\n<code>Ratio  :</code> {task.ratio()}"
                f"\n<code>Time   :</code> {task.seeding_time()}"
            )
        else:
            msg += (
                f"\n<code>Size   :</code> {task.size()}"
            )
        msg += f"\n<blockquote>{cancel_task}</blockquote>\n\n"

    if len(msg) == 0:
        if status == "All":
            return None, None
        else:
            msg = f"No Active {status} Tasks!\n\n"
    buttons = ButtonMaker()
    if is_user:
        buttons.data_button("ʙᴏᴛ\nʀᴇꜰʀᴇꜱʜ", f"status {sid} ref", position="header")
    if not is_user:
        buttons.data_button("ʙᴏᴛ\nɪɴꜰᴏ", f"status {sid} ov", position="header")
    if len(tasks) > STATUS_LIMIT:
        msg += f"<b>Page:</b> {page_no}/{pages} | <b>Tasks:</b> {tasks_no} | <b>Step:</b> {page_step}\n"
        buttons.data_button("⫷", f"status {sid} pre", position="header")
        buttons.data_button("⫸", f"status {sid} nex", position="header")
        if tasks_no > 30:
            for i in [1, 2, 4, 6, 8, 10, 15]:
                buttons.data_button(i, f"status {sid} ps {i}", position="footer")
    if status != "All" or tasks_no > 20:
        for label, status_value in list(STATUSES.items())[:9]:
            if status_value != status:
                buttons.data_button(label, f"status {sid} st {status_value}")
    button = buttons.build_menu(8)
    msg += (
        "\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"<b>CPU</b>: {cpu_percent()}% | "
        f"<b>FREE</b>: {get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)}\n"
        f"<b>RAM</b>: {virtual_memory().percent}% | "
        f"<b>UPTM</b>: {get_readable_time(time() - botStartTime)}"
    )
    return msg, button
    
