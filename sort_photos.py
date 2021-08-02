# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 12:23:54 2018

@author: yenkov
"""

import exifread
import os
import datetime
import shutil
import filecmp


def copy_rename(file, new_name, dest_dir):
        shutil.copy(file, dest_dir)
        
        dest_file = os.path.join(dest_dir, file)
        new_dest_file = os.path.join(dest_dir, new_name)
        if os.path.isfile(new_dest_file):
            #print(file, filecmp.cmp(dest_file, new_dest_file))
            #os.unlink(new_dest_file)
            return
        os.rename(dest_file, new_dest_file)        

        
def read_rename_exif(file, name, dest_dir):
    dt_obj = datetime.datetime.strptime(name, '%Y:%m:%d %H:%M:%S')
    dt_string = dt_obj.strftime('%Y%m%d_%H%M%S')
    dir_name = dest_dir + '/' + dt_obj.strftime('%Y')
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    dir_name += '/photos'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)        
    dir_name += '/' + dt_obj.strftime('%m') + '_' + dt_obj.strftime('%B')
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    copy_rename(file, dt_string + '.jpg', dir_name)

    
def read_rename_vid(file, dest_dir):
    creation_sec = os.path.getmtime(file)
    dt_obj = datetime.datetime.fromtimestamp(creation_sec)   
    dt_string = dt_obj.strftime('%Y%m%d_%H%M%S')
    dir_name = dest_dir + '/' + dt_obj.strftime('%Y')
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    dir_name += '/videos'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)          
    _, ext = os.path.splitext(file)
    copy_rename(file, dt_string + ext, dir_name)        

    
def write_log(logfile, string):
    with open(logfile, 'a', encoding='utf-8') as f:
        f.write(string)

        
def main(source_dir, dest_dir, err_dir):
    camera_set = set()              
    exc_count = 0            
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                os.chdir(root)
                with open(file, 'rb') as fo:
                    tags = exifread.process_file(fo, details=False)
                    for key, _ in tags.items():
                        if 'Model' in key:
                            if tags[key].values not in camera_set:
                                camera_set.add(tags[key].values)
                            break                        
                    for key, _ in tags.items():
                        if 'DateTime' in key:
                            pic_time = tags[key].values
                            read_rename_exif(file, pic_time, dest_dir)
                            break
                    else:
                        exc_count += 1
                        if not os.path.exists(err_dir):
                            os.makedirs(err_dir)
                        shutil.copy(file, err_dir)                      
                        string = str(exc_count) + '\t' + str(root) \
                        + '/' + str(file) + '\nTAGS:\n' + str(tags) + '\n'
                        write_log(err_dir + '/err_log.txt', string + '\n')
            elif file.lower().endswith('.avi') or file.lower().endswith('.mov'):
                os.chdir(root)
                read_rename_vid(file, dest_dir)
    print('Exception count:', exc_count, '\nCameras:')
    for e in camera_set:
        print(e)        

        
if __name__ == '__main__': 
    source_dir = 'm:/tst_dir/Наши фото'
    dest_dir = 'm:/tst_dir/out'
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir, ignore_errors=True)
    err_dir = dest_dir + '/err_tags'  
    main(source_dir, dest_dir, err_dir)
