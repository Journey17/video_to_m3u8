import subprocess
import os

def convert_to_m3u8(input_file, output_file_prefix):
    # 使用FFmpeg将输入的MP4文件转换为M3U8格式
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-f', 'hls',
        '-hls_time', '3',  # 设置每个切片的时长为3秒
        '-hls_list_size', '0',  # 不限制M3U8文件中包含的切片列表的最大数量
        '-hls_segment_filename', f'{output_file_prefix}_%02d.ts',  # 设置TS文件的命名方式
        output_file_prefix + '.m3u8'
    ]
    subprocess.run(cmd)

def main():
    input_folder = './mp4folder'  # 替换为你的输入文件夹路径
    output_folder = './m3u8folder'  # 替换为你的输出文件夹路径

    # 确保输出文件夹存在，如果不存在就创建它
    os.makedirs(output_folder, exist_ok=True)

    # 获取输入文件夹中的所有MP4文件
    input_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]

    # 遍历每个MP4文件并转换为M3U8格式
    for input_file in input_files:
        input_path = os.path.join(input_folder, input_file)
        output_file_prefix = os.path.join(output_folder, os.path.splitext(input_file)[0])
        convert_to_m3u8(input_path, output_file_prefix)

if __name__ == "__main__":
    main()
