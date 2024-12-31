import json
import os
from collections import deque
from enum import member
from charset_normalizer import detect


def load_json(file_name):
    if os.path.exists(file_name):
        # with open(file_name, 'r', encoding='utf-8') as file:
        with open(file_name, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            return json_data
            # return list(reversed(json_data))
    return []

def main():
    members = ['saerom', 'hayoung', 'jiwon', 'jisun', 'seoyeon', 'chaeyoung', 'nagyung', 'jiheon']
    # members = ['jisun']
    for m in members:
        messages = dict()
        print(m)

        data = load_json(f'raw-data/{m}.json')
        data = [d for d in data if d['userType'] == 'ARTIST']
        latest_data = load_json(f'raw-data/{m}-latest.json')
        for d in data:
            if d['userType'] == 'ARTIST':
                date = d['createDate']
                if date in messages:
                    print(d)
                    breakpoint()
                else:
                    messages[d['createDate']] = d

        for d in reversed(latest_data['data']):
            if d['userType'] == 'ARTIST':
                # body = d['body']
                # for b in body:
                #     print(b)

                if d['createDate'] not in messages:
                    # print('\tAdding')
                    print(d)
                    # data.append(d)
                    data.insert(0, d)
                    # print(data)

        new_file = f'raw-data/{m}-clean.json'
        with open(new_file, 'w', encoding='utf-8') as file:
            json.dump(data, file)
                    # print(d)
                # messages[d['createDate']] = d
        # print(len(messages))
                # print(d['userType'])
                # print(d)
            # print(d['messageId'])
        # latest_data = load_json(f'raw-data/{m}-latest.json')

# with open(f'raw-data/jisun.json', 'rb') as file:
#     result = detect(file.read())
#     print(result)

main()