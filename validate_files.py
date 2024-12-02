import csv
import os

member_name = 'chaeyoung'

media_path = f'docs/media/{member_name}'

tsv_name = f'temp/{member_name}/dm-log.tsv'

DATE_ID = 'date'
TIME_ID = 'time'
TEXT_ID = 'text'
YOUR_TEXT_ID = 'your_text'
IMAGE_ID = 'image'
VIDEO_ID = 'video'
AUDIO_ID = 'audio'


headers = [DATE_ID, TIME_ID, TEXT_ID, YOUR_TEXT_ID, IMAGE_ID, VIDEO_ID, AUDIO_ID]


def validate(row, all_files):
    print('Validating ', row)
    time = row[TIME_ID]
    if IMAGE_ID in row:
        image_arr = row[IMAGE_ID].split(',')
        for n in image_arr:
            if not os.path.exists(f'{media_path}/{n}'):
                print('MISSING ', n)
            else:
                all_files.remove(n)
        return

    if VIDEO_ID in row:
        if not os.path.exists(f'{media_path}/{row[VIDEO_ID]}'):
            print('MISSING ', row[VIDEO_ID])
        else:
            all_files.remove(row[VIDEO_ID])
        return

    if AUDIO_ID in row:
        if not os.path.exists(f'{media_path}/{row[AUDIO_ID]}'):
            print('MISSING ', row[AUDIO_ID])
        else:
            all_files.remove(row[AUDIO_ID])
        return


def main():
    main_dict = dict()

    with open(tsv_name, encoding='utf-8') as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='\v')
        for line in rd:
            row = dict()
            for i, elem in enumerate(line):
                if len(elem):
                    row[headers[i]] = elem
            date_list = main_dict.setdefault(row[DATE_ID], [])
            date_list.append(row)

    all_files = set()

    for root, dirs, files in os.walk(media_path):
        for f in files:
            all_files.add(f)

    for date, elems in main_dict.items():
        for row in elems:
            validate(row, all_files)

    for f in all_files:
        print('UNKNOWN ', f)


if __name__ == '__main__':
    main()
