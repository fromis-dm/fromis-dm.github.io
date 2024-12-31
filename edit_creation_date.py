import re
from datetime import datetime

import filedate

def test():
    value = """<dm:photo imageUrl="https://phinf.wevpstatic.net/MjAyNDAzMjVfNDYg/MDAxNzExMzQ3ODA3MTM2.WGrkRaPoVl4fL722FzTcZ91354nuC5V9LXouKmS3cCsg.jIj1p4OcCCtrMUo32ufDygSlgYxtOTXY18drNl1xO2kg.JPEG/image.jpg" width="153" height="123" />"""
    pattern = r'(<dm:.*?\/>)'
    matches = re.findall(pattern, value)
    print('MATCHES')
    for m in matches:
        print('\t', m)
        type = m.split(' ')[0].removeprefix('<dm:')
        print(type)

def edit_creation_date(file_path):
    file = filedate.File(file_path)

    print(file.created)
    new_date = datetime(2024, 1, 1, 12, 0, 0)
    file.created = new_date
    file.modified = new_date
    file.accessed = new_date
    print(file.created)

def main():
    # edit_creation_date('z.jpg')
    # edit_creation_date('z.mp4')
    # edit_creation_date('z.png')
    # print(fix_body_text('"1. 달리치약 좋습니다\n2.파인프라 야무집니다\n3. 티타드 굿\n4. 치실 하세요\n5.ajona 독일제 ㅊㅊ"'))
    test()
    pass




def fix_body_text(text):
    pattern = r'(\d+)\.'
    replacement = r'\1\\.'
    text = re.sub(pattern, replacement, text)
    return text.replace('\n', '<br>').replace('#', '\\#')
main()