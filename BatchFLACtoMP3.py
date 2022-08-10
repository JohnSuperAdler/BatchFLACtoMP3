##### Module

import numpy as np
import os
import time
import datetime
import shutil
import argparse

import mutagen
from pydub import AudioSegment
from mutagen import File, FileType
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


##### Parameter: argparse
##### Function

def happy_time(start, stop):
    process_time = round(stop - start)
    ss = process_time % 60
    mm = process_time // 60 % 60
    hh = process_time // 3600
    duration = "Process time == {}s == {}H {}m {}s".format(process_time,hh,mm,ss)
    return duration

### Count all
def count_files(path_src):
    count = 0
    for a, b, c in os.walk(path_src):
        for src_fn in c:
            count +=1
    print(f'Total {count} files in source directory.')
    print('Start conversion...')
    return count

### Conversion
def conversion(path_src, path_dst, count_1):
    conversion_count = 0
    count_2 = 0
    copy_count = 0
    for a, b, c in os.walk(path_src):
        for src_fn in c:
            count_2 += 1
            ### Filename and path
            src_fullpath = os.path.join(a, src_fn)
            dst_fn       = os.path.splitext(src_fn)[0] + '.mp3'
            dst_rela_dir = os.path.relpath(os.path.dirname(src_fullpath), path_src)
            dst_full_dir = os.path.join(path_dst, dst_rela_dir)
            dst_fullpath = os.path.join(dst_full_dir, dst_fn)
            if not os.path.exists(dst_full_dir):
                os.makedirs(dst_full_dir)
            ### Check src file type
            read_file = File(src_fullpath)
            file_type = type(read_file)
            
            ### File type manifold
            if file_type == mutagen.flac.FLAC:
                # TAG
                new_tag_di = {}
                for t in read_file.keys():
                    new_tag_di[t] = read_file[t][0]
                # Convert
                flac_audio = AudioSegment.from_file(src_fullpath, format='flac')
                flac_audio.export(dst_fullpath, format=file_format, bitrate=bitrate, tags=new_tag_di)
                # Art
                try:
                    art = read_file.pictures[0].data
                    audio = MP3(dst_fullpath, ID3=ID3)    
                    audio.tags.add(APIC(encoding=0, # 3 is for utf-8
                                        mime='image/png', # image/jpeg or image/png
                                        type=3, # 3 is for the cover image
                                        data=art))
                    audio.save()
                except:
                    pass
                conversion_count +=1
            elif file_type == mutagen.wave.WAVE:
                # Convert
                wav_audio = AudioSegment.from_file(src_fullpath, format='wav')
                wav_audio.export(dst_fullpath, format=file_format, bitrate=bitrate)
                # Write tags/art
                try:
                    for t in read_file.tags.keys():
                        audio = MP3(dst_fullpath, ID3=ID3)
                        audio.tags.add(read_file.tags[t])
                        audio.save()
                except:
                    pass
                conversion_count +=1
            #elif (file_type == mutagen.mp3.MP3) or (file_type == mutagen.mp4.MP4) or (file_type == mutagen.asf.ASF):
            elif file_type == mutagen.mp3.MP3:
                # Copy file
                shutil.copy(src_fullpath, dst_fullpath)
                copy_count += 1
            else:
                print(f'File type "{file_type}" not in deal list. Filename: "{src_fullpath}"')
                continue
            if (count_2 % 100) == 0:
                print(f'{count_2}/{count_1} files process done. {happy_time(loop_start, time.time())}')

    return conversion_count, copy_count

##### LOG

def write_log(path_src, path_dst, time_start_tag_2, time_end_tag_2, count_1, conversion_count, copy_count, dt_end):
    log  = ''
    log +=  '[PATH]\n'
    log += f'Source      : {path_src}\n'
    log += f'Destination : {path_dst}\n'
    log +=  '[TIME]\n'
    log += f'Start time : {time_start_tag_2}\n'
    log += f'End time   : {time_end_tag_2}\n'
    log +=  '[COUNT]\n'
    log += f'Total files          : {count_1}\n'
    log += f'Number of conversion : {conversion_count}\n'
    log += f'Number of copy       : {copy_count}\n'

    if not os.path.exists('output'):
        os.mkdir('output')

    log_fn = f'output/conversion_log_{dt_end.strftime("%y%m%d_%H%M%S")}.txt'
    if os.path.exists(log_fn): log_fn = log_fn.rsplit('.')[0] + '_X.txt'
    with open(log_fn, 'w') as file:
        file.write(log)

    print('Log generated.')


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser() 
    arg_parser.add_argument('src', type=str, help='path of source')
    arg_parser.add_argument('dst', type=str, help='path of destination')
    arg_parser.add_argument('-f', '--format' , type=str, default='mp3' , help='format of output files')
    arg_parser.add_argument('-b', '--bitrate', type=str, default='320K', help='bitrate of output files')
    path_src    = arg_parser.parse_args().src
    path_dst    = arg_parser.parse_args().dst
    file_format = arg_parser.parse_args().format
    bitrate     = arg_parser.parse_args().bitrate

    print(f'Source      file/directory: {path_src}')
    print(f'Destination file/directory: {path_dst}')
    print(f'Output file format : {file_format}')
    print(f'Output file bitrate: {bitrate}')

    time_start_tag_2 = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(f'Time start tag: {time_start_tag_2}')

    loop_start = time.time()
    count_1 = count_files(path_src)
    conversion_count, copy_count = conversion(path_src, path_dst, count_1)

    print(f'All {count_1} files process done. FINISHED')
    dt_end = datetime.datetime.now()
    time_end_tag_2 = dt_end.strftime('%Y/%m/%d %H:%M:%S')
    print(f'Time end tag: {time_end_tag_2}')

    write_log(path_src, path_dst, time_start_tag_2, time_end_tag_2, count_1, conversion_count, copy_count, dt_end)
