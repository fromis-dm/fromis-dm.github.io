import csv
import os

member_name = 'hayoung'

media_path = f'raw/{member_name}'

tsv_name = f'raw/{member_name}/dm-log.tsv'

DATE_ID = 'date'
TIME_ID = 'time'
TEXT_ID = 'text'
YOUR_TEXT_ID = 'your_text'
IMAGE_ID = 'image'
VIDEO_ID = 'video'
AUDIO_ID = 'audio'

should_rename = False

headers = [DATE_ID, TIME_ID, TEXT_ID, YOUR_TEXT_ID, IMAGE_ID, VIDEO_ID, AUDIO_ID]


def validate(row, all_files, missing):
    # print('Validating ', row)
    time = row[TIME_ID]
    if IMAGE_ID in row:
        image_arr = row[IMAGE_ID].split(',')
        for n in image_arr:
            if not os.path.exists(f'{media_path}/{n}'):
                print('MISSING ', n)
                missing.append(n)
            else:
                all_files.remove(n)
        return

    if VIDEO_ID in row:
        if not os.path.exists(f'{media_path}/{row[VIDEO_ID]}'):
            print('MISSING ', row[VIDEO_ID])
            missing.append(row[VIDEO_ID])
        else:
            all_files.remove(row[VIDEO_ID])
        return

    if AUDIO_ID in row:
        if not os.path.exists(f'{media_path}/{row[AUDIO_ID]}'):
            print('MISSING ', row[AUDIO_ID])
            missing.append(row[AUDIO_ID])
        else:
            all_files.remove(row[AUDIO_ID])
        return

def get_time(x):
    if '__' in x:
        return int(x.split('__')[1].split('.')[0])
    return None

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
    missing = []

    for root, dirs, files in os.walk(media_path):
        for f in files:
            all_files.add(f)

    for date, elems in main_dict.items():
        for row in elems:
            validate(row, all_files, missing)

    missing_ids = [(get_time(x), x) for x in missing]
    print(missing_ids)
    for f in all_files:
        time = get_time(f)
        found_match = False
        if time:
            for m, name in missing_ids:
                if abs(time - m) == 1:
                    old_path = f'{media_path}/{f}'
                    new_path = f'{media_path}/{name}'
                    print('FOUND MATCH')
                    print('\tOLD ' + old_path)
                    print('\tNEW ' + new_path)

                    if should_rename:
                    # if input("Rename?") == 'yes':
                        os.rename(old_path, new_path)
                        found_match = True

                    continue

        if not found_match:
            print('UNKNOWN ', f)


if __name__ == '__main__':
    main()
