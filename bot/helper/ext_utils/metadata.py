import json
from os import path as ospath, replace as osreplace
from bot import user_data
from asyncio import create_subprocess_exec
from .files_utils import get_base_name
from .bot_utils import cmd_exec, sync_to_async


async def edit_video_metadata(user_id, file_path):
    if not file_path.lower().endswith(('.mp4', '.mkv')):
        return

    user_dict = user_data.get(user_id, {})
    if user_dict.get("metadatatext", False):
        metadata_text = user_dict["metadatatext"]
    else:
        return

    file_name = ospath.basename(file_path)
    temp_ffile_name = ospath.basename(file_path)
    directory = ospath.dirname(file_path)
    temp_file = f"{file_name}.temp.mkv"
    temp_file_path = ospath.join(directory, temp_file)
    
    cmd = ['ffprobe', '-hide_banner', '-loglevel', 'error', '-print_format', 'json', '-show_streams', file_path]
    process = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"Error getting stream info: {stderr.decode().strip()}")
        return

    try:
        streams = json.loads(stdout)['streams']
    except:
        print(f"No streams found in the ffprobe output: {stdout.decode().strip()}")
        return

    cmd = [
        'xtra', '-y', '-i', file_path, '-c', 'copy',
        '-metadata:s:v:0', f'title={metadata_text}',
        '-metadata', f'title={metadata_text}',
        '-metadata', 'copyright=',
        '-metadata', 'description=',
        '-metadata', 'license=',
        '-metadata', 'LICENSE=',
        '-metadata', 'author=',
        '-metadata', 'summary=',
        '-metadata', 'comment=',
        '-metadata', 'artist=',
        '-metadata', 'album=',
        '-metadata', 'genre=',
        '-metadata', 'date=',
        '-metadata', 'creation_time=',
        '-metadata', 'language=',
        '-metadata', 'publisher=',
        '-metadata', 'encoder=',
        '-metadata', 'SUMMARY=',
        '-metadata', 'AUTHOR=',
        '-metadata', 'WEBSITE=',
        '-metadata', 'COMMENT=',
        '-metadata', 'ENCODER=',
        '-metadata', 'FILENAME=',
        '-metadata', 'MIMETYPE=',
        '-metadata', 'PURL=',
        '-metadata', 'ALBUM='
    ]

    audio_index = 0
    subtitle_index = 0
    first_video = False

    for stream in streams:
        stream_index = stream['index']
        stream_type = stream['codec_type']

        if stream_type == 'video':
            if not first_video:
                cmd.extend(['-map', f'0:{stream_index}'])
                first_video = True
            cmd.extend([f'-metadata:s:v:{stream_index}', f'title={metadata_text}'])
        elif stream_type == 'audio':
            cmd.extend(['-map', f'0:{stream_index}', f'-metadata:s:a:{audio_index}', f'title={metadata_text}'])
            audio_index += 1
        elif stream_type == 'subtitle':
            codec_name = stream.get('codec_name', 'unknown')
            if codec_name in ['webvtt', 'unknown']:
                print(f"Skipping unsupported subtitle metadata modification: {codec_name} for stream {stream_index}")
            else:
                cmd.extend(['-map', f'0:{stream_index}', f'-metadata:s:s:{subtitle_index}', f'title={metadata_text}'])
                subtitle_index += 1
        else:
            cmd.extend(['-map', f'0:{stream_index}'])

    cmd.append(temp_file_path)
    process = await create_subprocess_exec(*cmd, stderr=PIPE, stdout=PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        err = stderr.decode().strip()
        print(err)
        print(f"Error modifying metadata for file: {file_name}")
        return

    osreplace(temp_file_path, file_path)
    print(f"Metadata modified successfully for file: {file_name}")

async def add_attachment(user_id, file_path):
    if not file_path.lower().endswith(('.mp4', '.mkv')):
        return

    user_dict = user_data.get(user_id, {})
    if user_dict.get("attachmenturl", False):
        attachment_url = user_dict["attachmenturl"]
    else:
        return

    file_name = ospath.basename(file_path)
    temp_ffile_name = ospath.basename(file_path)
    directory = ospath.dirname(file_path)
    temp_file = f"{file_name}.temp.mkv"
    temp_file_path = ospath.join(directory, temp_file)

    attachment_ext = attachment_url.split('.')[-1].lower()
    if attachment_ext in ['jpg', 'jpeg']:
        mime_type = 'image/jpeg'
    elif attachment_ext == 'png':
        mime_type = 'image/png'
    else:
        mime_type = 'application/octet-stream'

    cmd = [
        'xtra', '-y', '-i', file_path,
        '-attach', attachment_url,
        '-metadata:s:t', f'mimetype={mime_type}',
        '-c', 'copy', '-map', '0', temp_file_path
    ]

    process = await create_subprocess_exec(*cmd, stderr=PIPE, stdout=PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        err = stderr.decode().strip()
        print(err)
        print(f"Error adding photo attachment to file: {file_name}")
        return

    osreplace(temp_file_path, file_path)
    print(f"Photo attachment added successfully to file: {file_name}")