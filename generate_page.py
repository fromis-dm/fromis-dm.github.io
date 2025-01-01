import csv
import json
import math
import os
import re
import textwrap
from datetime import datetime
from zoneinfo import ZoneInfo

def get_snippet_url(body):
    pattern = r'linkUrl="(.*?)"'
    return re.search(pattern, body).group(1)

def make_audio_md(audio_id):
    media_path = f'/assets/videos/{audio_id}.mp4'
    if not os.path.exists(f'docs/{media_path}'):
        print('MISSING ', media_path)

    return f'<audio controls src="{media_path}" preload="none"></audio>'

def make_video_md(video_id):
    media_path = f'/assets/videos/{video_id}.mp4'
    if not os.path.exists(f'docs/{media_path}'):
        print('MISSING ', media_path)

    thumb_path = f'/assets/videos/{video_id}-thumb.jpg'
    return \
f"""<figure class="msg-media" markdown="1">
<video controls="controls" preload="none" poster="{thumb_path}">
<source src="{media_path}" type="video/mp4">
Your browser does not support the video tag.
</video>
</figure>"""

def make_image_md(url, caption='', zoom_click=True, figure=True):
    if caption:
        caption = f'<figcaption>{caption}</figcaption>'

    zoom_md = 'onclick="openFullscreen(this)' if zoom_click else ''

    if figure:
        return textwrap.dedent(f"""\
                            <figure class="msg-media" markdown="1">
                            ![]({url+'?type=e1920'}){{ loading=lazy {zoom_md}"}}{caption}
                            </figure>""")
    else:
        return textwrap.dedent(f'![]({url+'?type=e1920'}){{ loading=lazy {zoom_md}"}}{caption}')

def get_datetime(data):
    time = int(data['createDate']) / 1000
    return datetime.fromtimestamp(time, tz=ZoneInfo("Asia/Seoul"))

def check_file(media_path, f):
    if not os.path.exists(f'{media_path}/{f}'):
        print(f'Media missing {f}')
        return f'*Media missing {f}*'

    return None

def load_json(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            return json_data
            # return list(reversed(json_data))
    else:
        print('failed to find', file_name)
    return []

def get_photo_url(body):
    pattern = r'imageUrl="(.*?)"'
    return re.search(pattern, body).group(1)

def get_video_id(body):
    pattern = r'videoId="(.*?)"'
    video_id = re.search(pattern, body).group(1)
    return video_id


def make_snippet_md(snippet_url):
    return f'<a href="{snippet_url}">{snippet_url}</a>'
    # return f'![{snippet_url}]({snippet_url})'


def wrap_links(text):
    # Regex pattern to match URLs
    url_pattern = r"(https?://[^\s]+)"

    # Replacement string to wrap the URL in an anchor tag
    replacement = r'<a href="\1">\1</a>'

    # Using re.sub to perform the replacement
    return re.sub(url_pattern, replacement, text)

def fix_body_text(text):
    pattern = r'(\d+)\.'
    replacement = r'\1\\.'
    text = re.sub(pattern, replacement, text)
    return text.replace('\n', '<br>').replace('#', '\\#')

def process_body(data):
    date = get_datetime(data)
    msg_date_str = date.strftime("%H:%M")

    body = data['body']
    out_md = []

    has_snippet = False
    for b in body:
        if 'dm:snippet' in b['value']:
            has_snippet = True
            break

    for b in body:
        value = fix_body_text(b['value'])
        pattern = r'(<dm:.*?\/>)'
        matches = re.findall(pattern, value)

        if has_snippet:
            value = wrap_links(value)

        if len(matches):
            for m in matches:
                type = m.split(' ')[0].removeprefix('<dm:')
                if type == 'photo':
                    photo_url = get_photo_url(m)
                    out_md.append(make_image_md(photo_url))
                if type == 'video':
                    video_id = get_video_id(m)
                    out_md.append(make_video_md(video_id))
                if type == 'audio':
                    audio_id = get_video_id(m)
                    out_md.append(make_audio_md(audio_id))
                if type == 'snippet':
                    print(m)
                #     snippet_url = get_snippet_url(m)
                #     out_md.append(make_snippet_md(snippet_url))
        else:
            out_md.append(value)

    if len(out_md) == 1:
        return \
f"""<div class="message" markdown="1">
<div class="message-date" markdown="1">
<small>{msg_date_str}</small>
</div>
<div markdown="1">
{out_md[0]}
</div>
</div>"""

    else:
        media_md = \
f"""<div class="message" markdown="1">
<div class="message-date" markdown="1">
<small>{msg_date_str}</small>
</div>
<div class="no-flex" markdown="1">
{''.join(out_md)}
</div>
</div>"""
        return media_md


def process_msg(data):
    date = get_datetime(data)
    # day_text = date.strftime("%y%m%d")
    msg_date_str = date.strftime("%H:%M")

    text = \
f"""{process_body(data)}"""

    return text

def process_day(day, msgs):
    day_text = day.strftime("%b %d %Y")

    all_msgs = []
    for m in msgs:
        all_msgs.append(process_msg(m))

    msgs = '\n'.join(all_msgs)


    out = \
f"""## {day_text}

{msgs}"""
    return out


def make_page(member_name, json_data, page_index):
    # all_msgs = []

    msgs_by_day = dict()

    first_day = None

    for data in json_data:
        date = get_datetime(data)
        day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        if not first_day:
            first_day = day

        # day = date.strftime("%y%m%d")
        msgs_by_day.setdefault(day, []).append(data)

    all_days = []
    days = sorted(msgs_by_day.keys())
    for d in days:
        all_days.append(process_day(d, msgs_by_day[d]))
    # print(days)

    # all_msgs.append(process_msg(data))

    # msgs = '\n'.join(all_msgs)

        # print(data)
        # print('num msgs', len(json_data))

    # main_dict = dict()
    #
    # for date, elems in main_dict.items():
    #     out_file += f'## {date}\n'
    #     for row in elems:
    #         parsed_text = get_parsed_text(row)
    #         out_file += parsed_text

    #             out_file += \
    # f"""
    # <div class="grid cards" markdown>
    # - **{time}**
    # {parsed_text}
    # </div>\n
    # """
    #             out_file += \
    # f"""
    # **{time}** {parsed_text}
    # """
    # print(time, text)
    out_file = \
f"""---
date: {first_day}
weight: {page_index}
---

# Page {page_index}

{'\n'.join(all_days)}
"""

    md_dir = f'docs/{member_name.lower()}'
    if not os.path.exists(md_dir):
        os.mkdir(md_dir)

    md_path = f'{md_dir}/{member_name.lower()}-{page_index}.md'
    with open(md_path, mode='w', encoding='utf-8') as txt:
        print('wrote to ', md_path)
        txt.writelines(out_file)

def process_json(member_name):
    tsv_name = f'raw/{member_name}/dm-log.tsv'
    json_name = f'raw-data/{member_name.lower()}-clean.json'
    json_data = list(reversed(load_json(json_name)))
    json_data = [d for d in json_data if d['userType'] == 'ARTIST']
    media_path = f'docs/media/{member_name.lower()}'

    msgs_by_day = dict()

    first_day = None

    for data in json_data:
        date = get_datetime(data)
        day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        if not first_day:
            first_day = day

        # day = date.strftime("%y%m%d")
        msgs_by_day.setdefault(day, []).append(data)

    num_msgs_per_page = 500

    all_days = []
    days = sorted(msgs_by_day.keys())
    page_data = []
    page_index = 1

    for i, d in enumerate(days):
        is_last_page = i == len(days) - 1
        page_data += msgs_by_day[d]

        if len(page_data) >= num_msgs_per_page or is_last_page:
            make_page(member_name, page_data, page_index)
            page_data = []
            page_index += 1


    # for i in range(0, len(json_data), num_msgs_per_page):
    #     data_slice = json_data[i:i+num_msgs_per_page]
    #     page_index = math.floor(i / num_msgs_per_page) + 1
    #     make_page(member_name, data_slice, page_index)

def main():
    members = ['Saerom', 'Hayoung', 'Jiwon', 'Jisun', 'Seoyeon', 'Chaeyoung', 'Nagyung', 'Jiheon']
    # members = ['Nagyung', 'Saerom', 'Jisun']
    # members = ['Jisun']

    for member_name in members:
        process_json(member_name)

if __name__ == '__main__':
    main()
