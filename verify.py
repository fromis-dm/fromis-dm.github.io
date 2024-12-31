import csv
import json
import os
import re
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import yt_dlp
import requests
import tzdata
import filedate

from yt_dlp.extractor.weverse import WeverseIE


DATE_ID = 'date'
TIME_ID = 'time'
TEXT_ID = 'text'
YOUR_TEXT_ID = 'your_text'
IMAGE_ID = 'image'
VIDEO_ID = 'video'
AUDIO_ID = 'audio'

headers = [DATE_ID, TIME_ID, TEXT_ID, YOUR_TEXT_ID, IMAGE_ID, VIDEO_ID, AUDIO_ID]

params = {
    # 'verbose': True,
    'quiet': True,
    'cookiesfrombrowser': ('firefox',),
}

uniq_files = set()

def edit_creation_date(file_path, new_date):
    # print(file_path, new_date)
    # file = filedate.File(file_path)
    # file.created = new_date
    # file.modified = new_date
    # file.accessed = new_date
    pass

def get_video_url(video_id, msg_id, room_id):
    req = f'/dm/v1.0/video/{video_id}/playInfo?messageId={msg_id}&roomId={room_id}'
    response = write_single(req, 'raw/test', False)

    if response:
        y = response['playInfo'].replace('\n', '').replace('\t', '')
        for z in y.split('source'):
            if '.mp4' in z:
                url = z.removeprefix('":"').removesuffix('","')
                return url
    return None
            # download_file(url, 'raw/test/out.mp4')

def make_extractor():
    ydl = yt_dlp.YoutubeDL(params)

    ext = WeverseIE()
    ext.set_downloader(ydl)
    ext.initialize()
    # ext._initialize_pre_login()
    # ext._real_initialize()
    # ext._ready = True
    return ext

def run_extr(extr, req, out_data=None, grab_data=True):
    # print(req)

    while True:
        try:
            json_data = extr._call_api(req, '')
            # print(json_data)
            break
        except Exception as e:
            print(e)
            breakpoint()
            time.sleep(5.0)

    if out_data is not None:
        if grab_data:
            post_data = json_data['data']
            out_data += post_data
            print(f'Found data {len(post_data)} Data: {len(out_data)}')
        else:
            out_data.append(json_data)
            print(len(out_data))

    return json_data


def write_single(req, filename, skip_exists=True):
    file_path = f'{filename}.json'
    if skip_exists and os.path.exists(file_path):
        return False

    extr = make_extractor()
    return run_extr(extr, req)
    # with open(file_path, 'w') as file:
    #     # Write the array as JSON
    #     json.dump(data, file)
    #     return True

def download_file(file_url, file_path, skip_exists, timeout):
    if skip_exists and os.path.exists(file_path):
        return False
    # if os.path.exists(file_path):
    #     response = requests.head(file_url, timeout=5)
    #     expected_size = int(response.headers['Content-Length'])
    #
    #     file_size = int(os.path.getsize(file_path))
    #     if file_size != expected_size:
    #         print(file_path, expected_size, file_size)
    #     time.sleep(0.1)
    #     # with open(file_path, 'rb') as file:
    #     #     file_bytes = file.read()  # Read the entire file as bytes
    #     #     print(file_bytes)
    #     return False

    # return
    retries = 0

    while True:  # Infinite loop to keep trying
        if retries > 5:
            print('FAILED TO DOWNLOAD FILE')
            print(file_url)
            breakpoint()
            return False
        try:
            # Send a GET request to the URL
            print(f"Downloading {file_path} {file_url}")
            response = requests.get(file_url, timeout=timeout)

            # Check if the request was successful
            if response.status_code == 200:
                # Open a file in binary write mode to save the image
                with open(file_path, "wb") as file:
                    file.write(response.content)
                    # print("Downloaded successfully!")
                return True  # Exit the loop if download is successful
            else:
                print(f"Failed to download image. Status code: {response.status_code}")
                time.sleep(10)
                retries += 1
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)
            retries += 1

def load_json(name):
    file_name = f'raw-data/{name}-clean.json'
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            return json_data
            # return list(reversed(json_data))
    return []

def load_tsv(name):
    file_name = f'raw-data/{name}.tsv'
    main_dict = dict()

    all_rows = []
    with open(file_name, encoding='utf-8') as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='\v')
        for line in rd:
            # print(line)
            row = dict()
            for i, elem in enumerate(line):
                # print(i, elem)
                if len(elem):
                    # print(f'Set {h} to {elem[i]}')
                    row[headers[i]] = elem  # print(row[TIME_ID])

            # if skip_your_msgs and YOUR_TEXT_ID in row:
            #     continue

            date_list = main_dict.setdefault(row[DATE_ID], [])
            date_list.append(row)
            all_rows.append(row)
            # print(line)
            # print(row)
    # print(all_rows)
    return all_rows


def get_json_text(json):
    for elem in json['body']:
        text = elem['value']
        if not text.startswith('<dm:'):
            return text
    return ''

def get_photo_url(body):
    pattern = r'imageUrl="(.*?)"'
    return re.search(pattern, body).group(1)

def get_video_id(body):
    pattern = r'videoId="(.*?)"'
    return re.search(pattern, body).group(1)

def get_room_id(member):
    room_ids = {
        'saerom': 321529,
        'hayoung': 297243,
        'jiwon': 464268,
        'jisun': 221087,
        'seoyeon': 229217,
        'chaeyoung': 329164,
        'nagyung': 233441,
        'jiheon': 414361
    }
    return room_ids[member]

def get_datetime(timestamp):
    time = int(timestamp) / 1000
    return datetime.fromtimestamp(time, tz=ZoneInfo("Asia/Seoul"))

def get_type(m):
    pattern = r'(<dm:(.*?)\s)'
    return re.search(pattern, m).group(1)

def get_all_media(member, json_data):
    media = {
        'video': [],
        'audio': [],
        'photo': []
    }

    total_msgs = 0

    for data in json_data:
        body = data['body']
        pattern = r'(<dm:.*?\/>)'
        msg_id = data['messageId']
        date = get_datetime(int(data['createDate']))
        formatted_date = date.strftime("%y%m%d-%H%M")

        total_msgs += 1

        for b in body:
            value = b['value']
            # print('VALUE', value)
            matches = re.findall(pattern, value)
            number_of_matches = len(matches)

            local_types = set()

            for m in matches:
                type = m.split(' ')[0].removeprefix('<dm:')
                if type == 'photo':
                    photo_url = get_photo_url(m)
                    my_pattern = r'/.*?/(.*?)/'
                    # print(photo_url)
                    photo_id = re.search(my_pattern, photo_url.removeprefix('https://')).group(1)
                    photo_id = ''.join(photo_id.split('.')[0:-1])
                    # photo_id = test2[-2] + '.' + test2[-1]

                    # print(photo_id, photo_url)

                    media[type].append((photo_url, photo_id, date))
                    if photo_id in uniq_files:
                        print(photo_id)
                        breakpoint()
                    uniq_files.add(photo_id)
                elif type == 'video' or type == 'audio':
                    id = get_video_id(m)
                    media[type].append((id, msg_id, date))
                    if id in uniq_files:
                        print(id)
                        breakpoint()
                    uniq_files.add(id)
                # else:
                #     print('WEIRD TYPE:', type, m)
                #     print('FULL', value)
                #     print('MATCH', m)

    # print(media)
    total_media = 0
    for k, v in media.items():
        # print('\t', k, len(v))
        total_media += len(v)
    # print('\t total media', total_media)
    # print('\t msgs', total_msgs)
    print(f'| {member} | {len(media['photo'])} | {len(media['audio'])} | {len(media['video'])} | {total_media} | {total_msgs}')


    return media

def download_media(media, member):
    room_id = get_room_id(member)

    root_folder = f'raw-data/{member}'
    if not os.path.exists(root_folder):
        os.mkdir(root_folder)

    images_by_time = dict()
    for media_type, items in media.items():
        # print('DOWNLOADING', media_type, len(items))
        if (media_type == 'video' or media_type == 'audio') and True:
            for video_id, msg_id, file_date in items:
                # print('Parsing video', video_id, msg_id)
                expected_file_path = f'{root_folder}/{video_id}.mp4'

                if expected_file_path in uniq_files:
                    print(expected_file_path)
                    breakpoint()
                uniq_files.add(expected_file_path)

                if os.path.exists(expected_file_path):
                    edit_creation_date(expected_file_path, file_date)
                    # print('\tSkip')
                    continue

                if video_id == '191A25538114D39BB6EA5508428F425CE66C':
                    req = f'/dm/v1.0/video/{video_id}/playInfo?messageId={msg_id}&roomId={room_id}'
                    response = write_single(req, 'raw/test', False)
                    print(response)

                video_url = get_video_url(video_id, msg_id, room_id)

                if download_file(video_url, expected_file_path, True, 300):
                    time.sleep(2)

        if media_type == 'photo' and True:
            for image_url, photo_id, file_date in items:
                ext = image_url.split('.')[-1]
                # print(image_url)
                filepath = f'{root_folder}/{photo_id}.{ext}'
                if os.path.exists(filepath):
                    edit_creation_date(filepath, file_date)
                    continue

                print('download ', filepath)
                if download_file(image_url, filepath, False, 120):
                    time.sleep(2)

    # for date, images in images_by_time.items():
    #     # if len(images) > 1:
    #     formatted_date = date.strftime("%y%m%d-%H%M")
    #     # print(formatted_date)
    #     use_suffix = len(images) > 1
    #     for i, image_url in enumerate(images):
    #         ext = image_url.rsplit('.')[-1]
    #         if use_suffix:
    #             filepath = f'{root_folder}/{formatted_date}-{i}.{ext}'
    #         else:
    #             filepath = f'{root_folder}/{formatted_date}.{ext}'
    #
    #         if filepath in uniq_files:
    #             print(filepath)
    #             breakpoint()
    #         uniq_files.add(filepath)
    #
    #         # if len(images) > 1:
    #         #     print('\t', filepath, image_url)
    #         if os.path.exists(filepath):
    #             continue
    #         if len(images) > 1:
    #             if download_file(image_url, filepath, False, 30):
    #                 time.sleep(2)

    #
    # body = data['body']
    # pattern = r'(<dm:.*?\/>)'
    # msg_id = data['messageId']
    # date = get_datetime(int(data['createDate']))
    # formatted_date = date.strftime("%y%m%d-%H%M")
    #
    # pending_images = []
    # pending_videos = []
    #
    # for b in body:
    #     value = b['value']
    #     matches = re.findall(pattern, value)
    #     number_of_matches = len(matches)
    #
    #     local_types = set()
    #
    #     for m in matches:
    #         type = m.split(' ')[0].removeprefix('<dm:')
    #         if type == 'photo':
    #             pending_images.append(get_photo_url(value))
    #
    #         if type == 'video':
    #             pending_videos.append(get_video_id(value))
    #
    #         if type == 'audio':
    #             pending_videos.append(get_video_id(value))
    #
    # if pending_images or pending_videos:
    #     print(pending_images, pending_videos)
    #     # for i, m in enumerate(matches):
    #     #     type = m.split(' ')[0].removeprefix('<dm:')
    #     #     if type == 'photo':
    #     #         print(data)
    #
    #         # if type == 'video':


def download_missing():
    pass

def main():
    members = ['saerom', 'hayoung', 'jiwon', 'jisun', 'seoyeon', 'chaeyoung', 'nagyung', 'jiheon']
    # members = ['saerom', 'hayoung', 'jiwon', 'jisun', 'chaeyoung', 'nagyung', 'jiheon']
    # members = ['jisun']
    for member in members:
        json_data = load_json(member)

        # count = 0
        # for data in json_data:
        #     body = data['body']
        #     for b in body:
        #         value = b['value']
        #         if 'dm:' in value:
        #             count += value.count('dm:photo')
        #             count += value.count('dm:video')
        #             count += value.count('dm:audio')
        # print(member, count)

        # print(member)
        media = get_all_media(member, json_data)
        # download_media(media, member)

        # tsv_data = list(reversed(load_tsv(member)))
        #
        # room_id = get_room_id(member)
        #
        # types = {
        #     'video': [],
        #     'audio': [],
        #     'photo': []
        # }
        # total = 0
        #
        # for data in json_data:
        #     body = data['body']
        #     pattern = r'(<dm:.*?\/>)'
        #     msg_id = data['messageId']
        #     date = get_datetime(int(data['createDate']))
        #     formatted_date = date.strftime("%y%m%d-%H%M")
        #
        #     for b in body:
        #         value = b['value']
        #         matches = re.findall(pattern, value)
        #         number_of_matches = len(matches)
        #
        #         total += number_of_matches
        #
        #         local_types = set()
        #
        #         for i, m in enumerate(matches):
        #             type = m.split(' ')[0].removeprefix('<dm:')
        #             if type in types:
        #                 types[type].append(m)  # print(type)
        #                 local_types.add(type)
        #
        #
        # total_media = 0
        # for t in ['photo', 'video', 'audio']:
        #     # for v in types[t]:
        #     if t in types:
        #         # print(t, len(types[t]))
        #         total_media += len(types[t])
        #
        # tsv_audio = []
        # tsv_video = []
        # tsv_image = []
        # for r in tsv_data:
        #     if VIDEO_ID in r:
        #         tsv_video.append(r[VIDEO_ID])
        #
        #     if AUDIO_ID in r:
        #         tsv_audio.append(r[AUDIO_ID])
        #
        #     if IMAGE_ID in r:
        #         tsv_image += r[IMAGE_ID].split(',')
        #
        # total_tsv = len(tsv_audio) + len(tsv_video) + len(tsv_image)
        # print(member, total_media, total_tsv, len(json_data), len(tsv_data))
        # print('\tvideos', len(types.get('video')), '/', len(tsv_video))
        # print('\taudio', len(types.get('audio')), '/', len(tsv_audio))
        # print('\tphoto', len(types.get('photo')), '/', len(tsv_image))
        # print('\ttotal', total_media, '/', total_tsv)

main()
