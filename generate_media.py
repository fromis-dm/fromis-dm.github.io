import csv
import os
import subprocess
import shutil

import ffmpeg

member_name = 'hayoung'

source_folder = f'raw/{member_name}'
output_folder = f'docs/media/{member_name}'

def convert_image(root, image):
    in_path = f'{root}/{image}'
    out_path = f'{output_folder}/{image}'
    cmd = f'magick {in_path} -resize 1280x720 {out_path}'
    subprocess.call(cmd, shell=True)
    print('Process image', in_path)
    pass

def generate_thumbnail(root, video):
    in_path = f'{root}/{video}'
    out_path = f'{output_folder}/{video.removesuffix('.mp4')}-thumb.jpg'
    cmd = f"ffmpeg -ss 00:00:01.00 -i \"{in_path}\" -vf 'scale=320:320:force_original_aspect_ratio=decrease' -vframes 1 \"{out_path}\""
    # print(cmd)

    result = subprocess.run(['ffmpeg', '-y', '-i', in_path, '-vf', 'scale=480:480:force_original_aspect_ratio=decrease', '-vframes', '1', out_path], capture_output=True, text=True)

    out_video = f'{output_folder}/{video}'
    make_copy(in_path, out_video)
    print('Process video', in_path)



#     process = (
#         ffmpeg
#         .input(in_path)
#         .output('pipe':, format='rawvideo', pix_fmt='rgb24')
#         .run_async(pipe_stdout=True, pipe_stderr=True)
#     )
#
# ffmpeg.input()
#     ffmpeg.compile()
#     subprocess.call(cmd)
#     ffmpeg.run(cmd)

    # cmd = '/usr/local/bin/convert -size 30x40 xc:white -fill white -fill black -font Arial -pointsize 40 -gravity South -draw "text 0,0 \'P\'" /Users/fred/desktop/draw_text2.gif'
    # subprocess.call(cmd, shell=True)



def make_copy(in_path, out_path):
    if not os.path.exists(out_path):
        shutil.copy(in_path, out_path)


def main():
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(source_folder):

        for f in files:
            in_path = f'{root}/{f}'

            if f.endswith('.jpg'):
                convert_image(root, f)
            elif f.endswith('.mp4'):
                generate_thumbnail(root, f)
            elif f.endswith('.gif'):
                out_path = f'{output_folder}/{f}'
                # shutil.copy(in_path, out_path)
                print('Copy media', in_path)
                make_copy(in_path, out_path)
            else:
                print('SKIP unknown file ', in_path)

if __name__ == '__main__':
    main()
