import csv
import os

DATE_ID = 'date'
TIME_ID = 'time'
TEXT_ID = 'text'
YOUR_TEXT_ID = 'your_text'
IMAGE_ID = 'image'
VIDEO_ID = 'video'
AUDIO_ID = 'audio'

skip_your_msgs = True

headers = [DATE_ID, TIME_ID, TEXT_ID, YOUR_TEXT_ID, IMAGE_ID, VIDEO_ID, AUDIO_ID]

def check_row(row):
    if VIDEO_ID in row:
        return check_file(row[VIDEO_ID])

    if AUDIO_ID in row:
        return check_file(row[AUDIO_ID])

    return None

def check_file(f):
    if not os.path.exists(f'{relative_media_path}/{f}'):
        print(f'Media missing {f}')
        return f'*Media missing {f}*'

    return None

def get_parsed_text(row):
    time = row[TIME_ID]

    error = check_row(row)
    if error:
        return f'\n**{time}** {error}\n'

    if IMAGE_ID in row:
        image_arr = row[IMAGE_ID].removesuffix('_IMG').split(',')

        links_md = '<br>'.join([f'![]({media_path}/{t})' for t in image_arr])
        return \
f"""
**{time}**<br>
{links_md}{{ loading=lazy }}
"""

    # ![type:video]({member_name}/{row[VIDEO_ID]})

    mp4_name = ''

    if VIDEO_ID in row:
        mp4_name = row[VIDEO_ID]
        thumb_name = f"{mp4_name.removesuffix('.mp4')}-thumb.jpg"
        return \
f"""
**{time}**<br>
<video controls="controls" preload="none" poster="{media_path}/{thumb_name}">
<source src="{media_path}/{mp4_name}#t=1" type="video/mp4">
Your browser does not support the video tag.
</video>
"""

    if AUDIO_ID in row:
        return \
f"""
**{time}**<br>
<audio controls src="{media_path}/{row[AUDIO_ID]}" preload="none"></audio>
"""

    if TEXT_ID in row:
        return \
f"""
**{time}** {row[TEXT_ID].replace('\n', '<br>')}
"""

    if YOUR_TEXT_ID in row:
        return \
f"""
**{time}** {row[YOUR_TEXT_ID].replace('\n', '<br>')}
"""

    return ''

def main():
    out_file = \
f"""---
draft: true 
date: 2024-01-31 
categories:
  - Hello
  - World
---

# {member_name}
"""

    main_dict = dict()

    with open(tsv_name, encoding='utf-8') as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='\v')
        for line in rd:
            # print(line)
            row = dict()
            for i, elem in enumerate(line):
                # print(i, elem)
                if len(elem):
                    # print(f'Set {h} to {elem[i]}')
                    row[headers[i]] = elem
                # print(row[TIME_ID])

            if skip_your_msgs and YOUR_TEXT_ID in row:
                continue

            date_list = main_dict.setdefault(row[DATE_ID], [])
            date_list.append(row)
            print(row)


    for date, elems in main_dict.items():
        out_file += f'## {date}\n'
        for row in elems:
            parsed_text = get_parsed_text(row)
            out_file += parsed_text

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

    out_name = f'docs/posts/{member_name.lower()}.md'
    with open(out_name, mode='w', encoding='utf-8') as txt:
        txt.writelines(out_file)


if __name__ == '__main__':
    do_batch_run = False

    batch_run = ['Hayoung', 'Seoyeon', 'Jisun', 'Chaeyoung', 'Saerom']

    member_name = 'Hayoung'

    tsv_name = f'raw/{member_name}/dm-log.tsv'

    media_path = f'../media/{member_name.lower()}'

    relative_media_path = f'docs/media/{member_name.lower()}'

    if do_batch_run:
        for member_name in batch_run:

            tsv_name = f'raw/{member_name}/dm-log.tsv'

            media_path = f'../media/{member_name.lower()}'

            relative_media_path = f'docs/media/{member_name.lower()}'

            main()
    else:
        main()
