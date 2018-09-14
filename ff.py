# -- coding: utf-8 --
import sys
import random
import chardet
import subprocess
import os
import re
import json
import multiprocessing as mp
from pathlib import Path
from pprint import pprint
from win32api import GetShortPathName

'''
filter_w = int(0.50 * video_w)
filter_h = int(0.08 * video_h)
filter_y = int(0.03 * video_h)
filter_x = int(video_w - filter_w)
'''

def create_dir(dr_path):
    dr_path = dr_path.strip()
    dr_path = dr_path.rstrip('\\')
    isExists = os.path.exists(dr_path)
    if not isExists:
        os.makedirs(dr_path)
    return


def videojson(video_name, dir_type):

    strCmd = 'ffprobe -v quiet -print_format json -show_format -show_streams -i ' + video_name
    subp = subprocess.Popen(strCmd, stdout=subprocess.PIPE)
    json_subp = json.loads(subp.stdout.read())

    try:
        video_duration = (json_subp['streams'][0]['duration'])
    except KeyError as err:
        video_duration = (json_subp['format']['duration'])

    video_w = (json_subp['streams'][0]['width'])
    video_h = (json_subp['streams'][0]['height'])
    
    print (video_w, video_h)
    if dir_type == '右上':
        # if video_w > video_h:
        filter_w = int(0.30 * video_w)
        filter_h = int(0.15 * video_h)
        filter_y = int(0.08 * video_h)
        filter_x = int(video_w - filter_w)
    elif dir_type == '右下':
        filter_w = int(0.31 * video_w)
        filter_h = int(0.08 * video_h)
        filter_y = int(0.85 * video_h)
        filter_x = int(video_w - filter_w)
    elif dir_type == '左上':
        filter_w = int(0.25 * video_w)
        filter_h = int(0.08 * video_h)
        filter_y = int(0.08 * video_h)
        filter_x = int(0.03 * video_w)
    elif dir_type == '左下':
        filter_w = int(0.24 * video_w)
        filter_h = int(0.10 * video_h)
        filter_y = int(0.78 * video_h)
        filter_x = int(0.05 * video_w)
        # print (filter_x, filter_y, filter_w, filter_h)
    return (filter_x, filter_y, filter_w, filter_h, video_duration)


def process_name(video_name):

    frist_name = os.path.basename(video_name)
    frist_name = os.path.splitext(frist_name)
    frist_name = frist_name[0]
    return frist_name


def process_video(video_name, video_ok_path, dir_type):

    print (video_name)

    # 创建保存目录
    # video_ok_path = os.path.dirname(video_name)

    create_dir(video_ok_path)
    frist_name = process_name(video_name)

    video_save_name = os.path.dirname(video_name)
    video_save_name_short = GetShortPathName(video_save_name)
    video_name = GetShortPathName(video_name)

    random_video_name = str(random.random())[2:]
    video_save_name = video_save_name_short + '\\' + random_video_name + '.mp4'
    video_rename_change = video_ok_path + '\\' + frist_name + '.mp4'
    

    filter_x, filter_y, filter_w, filter_h, video_duration = videojson(
        video_name, dir_type)

    # print (video_save_name, video_rename_change)
    # 去掉前 4  后 3 秒
    video_duration_start = 4
    video_duration_end = round(float(video_duration)) - 3

    strCmd = 'ffmpeg -i {} -metadata comment='' -ss {} -to {} -vf delogo=x={}:y={}:w={}:h={}:t=2:band=30 -c:a copy {}'.format(
        video_name, video_duration_start, video_duration_end, filter_x, filter_y, filter_w, filter_h, video_save_name)
    subp = subprocess.Popen(strCmd, stdout=subprocess.PIPE)
    subp.wait()
    change_rename = os.rename(video_save_name, video_rename_change)
    delete_source = os.remove(video_name)


def DrsTart():
    p = mp.Pool()
    current_path = os.path.split(os.path.realpath(__file__))[0]
    first_path = open('裁剪目录.txt', encoding='utf-8').readlines()
    dir_name = ['左上', '右上', '右下','左下']
    # 遍历 裁减目录
    for _first_path in first_path:
        _first_path = _first_path.strip()

        for _dir_name in dir_name:
            _dir_name_type = _dir_name
            _dir_name = (current_path + '\\' + _first_path + '\\' + _dir_name)
            video_ok_path = (current_path + '\\' + _first_path)

            try:
                _dir_files = os.listdir(_dir_name)
            except Exception as err:
                continue

            _dir_full_name = list(
                map(lambda paths: _dir_name + '\\' + paths, _dir_files))
            for video_name in _dir_full_name:
                process_video(video_name, video_ok_path, _dir_name_type)
                #p.apply_async(process_video, args=(video_name, video_ok_path, _dir_name_type))
    #p.close()
    #p.join()

if __name__ == '__main__':
    DrsTart()