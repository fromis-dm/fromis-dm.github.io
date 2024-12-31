import csv
import os
import subprocess
import shutil

DATE_ID = 'date'
TIME_ID = 'time'
TEXT_ID = 'text'
YOUR_TEXT_ID = 'your_text'
IMAGE_ID = 'image'
VIDEO_ID = 'video'
AUDIO_ID = 'audio'

headers = [DATE_ID, TIME_ID, TEXT_ID, YOUR_TEXT_ID, IMAGE_ID, VIDEO_ID, AUDIO_ID]

skip_duplicate = True
skip_images = True

copy_image = False
copy_video = False

source_folder = ''
output_folder = ''

def convert_image(root, image):
    in_path = f'{root}/{image}'
    out_path = f'{output_folder}/{image}'

    if copy_image:
        make_copy(in_path, out_path)
        return

    if skip_duplicate and os.path.exists(out_path):
        return

    cmd = f'magick {in_path} -resize 1920x1080 -quality 80 {out_path}'
    subprocess.call(cmd, shell=True)
    print('Process image', in_path)
    pass

def process_video(root, video, is_video):
    in_path = f'{root}/{video}'
    out_thumb = f'{output_folder}/{video.removesuffix('.mp4')}-thumb.jpg'
    out_video = f'{output_folder}/{video}'

    if skip_duplicate and os.path.exists(out_video):
        print('skip', out_video)
        return

    if copy_video:
        make_copy(in_path, out_video)
    else:
        encode_video(in_path, out_video)
    print(f'Process ${'VIDEO' if is_video else 'AUDIO'}', in_path)

    # make the thumbnail
    if is_video:
        # cmd = ['ffmpeg', '-y', '-i', out_video, '-vf', 'scale=480:480:force_original_aspect_ratio=decrease', '-vframes', '1', out_path]
        cmd = ['ffmpeg', '-y', '-i', out_video, '-q:v', '15', '-vframes', '1', out_thumb]
        result = subprocess.run(cmd, capture_output=True, text=True)



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



def encode_video(in_path, out_path):
    # cmd = ['ffmpeg', '-y', '-i', in_path, '-vf', 'scale=1080:-2', '-vcodec', 'libx265', '-crf', '26', out_path]
    cmd = ['ffmpeg', '-y', '-i', in_path, '-vcodec', 'libx265', '-crf', '26', out_path]
    # if not os.path.exists(out_path):
    result = subprocess.run(cmd, capture_output=True, text=True)
    print('Encode video', result)
        # 'ffmpeg -i input.avi  scale=720:-1 -c:a copy output.mkv'

def resize_gif(in_path, out_path):
    cmd = ['ffmpeg', '-y', '-i', in_path, '-vf', 'fps=15,scale=480:-2', out_path]
    # if not os.path.exists(out_path):
    # ffmpeg -i input.gif -vf "scale=320:-1" output.gif
    result = subprocess.run(cmd, capture_output=True, text=True)
    print('Resize gif', result)
        # 'ffmpeg -i input.avi  scale=720:-1 -c:a copy output.mkv'

def make_copy(in_path, out_path):
    if not os.path.exists(out_path):
        shutil.copy(in_path, out_path)
        print('copy')
    else:
        print('skip')


def run_folder(new_source, new_output):
    global source_folder
    global output_folder

    source_folder = new_source
    output_folder = new_output

    if not os.path.exists(source_folder):
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(source_folder):
        for f in files:
            in_path = f'{root}/{f}'

            if f.endswith('.jpg') or f.endswith('.png'):
                if not skip_images:
                    print(in_path)
                    convert_image(root, f)
            elif f.endswith('.mp4'):
                print(in_path)
                process_video(root, f, True)
            elif f.endswith('.gif'):
                if not skip_images:
                    print(in_path)
                    out_path = f'{output_folder}/{f}'
                    # shutil.copy(in_path, out_path)
                    print('Resize gif', in_path)
                    # make_copy(in_path, out_path)
                    resize_gif(in_path, out_path)
            else:
                print('SKIP unknown file ', in_path)


if __name__ == '__main__':
    # members = ['saerom', 'hayoung', 'jiwon', 'jisun', 'seoyeon', 'chaeyoung', 'nagyung', 'jiheon']
    # for member_name in members:
    #     source_folder = f'raw/{member_name}/posts'
    #     output_folder = f'docs/media/{member_name}/posts'
    #     run_folder(source_folder, output_folder)
    run_folder('raw-data', 'docs/assets/videos')
    # run_folder('raw/moments-media', 'docs/assets/videos')