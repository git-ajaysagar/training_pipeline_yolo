# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 01:50:48 2021

@author: Ajay Sagar
"""

def inp_val():
    #importing libraries
    import os
    import tarfile
    import random
    import json
    import sys
    import yaml
    import re
    import imghdr
    from colorama import Fore, Style
    
    with open(os.path.join(os.getcwd(),'yolo_training_config.json'),'r') as main_conf:
        conf = json.load(main_conf)
        
    link_to_dataset = conf['dataset']['url']
    input_dataset_type = link_to_dataset.split('/')[-1]
    print(input_dataset_type)
    # sys.exit()
    print(link_to_dataset)
    path_to_data = os.getcwd()
    print(path_to_data)
    # sys.exit()
    if link_to_dataset.startswith('http'):
        os.system('curl --output '+os.path.join(path_to_data+input_dataset_type)+' '+str(link_to_dataset))
        training_data = tarfile.open(os.path.join(path_to_data+input_dataset_type))
        training_data.extractall(path_to_data)
        print(path_to_data)
        # sys.exit()
        # os.remove(os.path.join(path_to_data,input_dataset_type))
  # else:
    #     training_data = tarfile.open(d['input'])
    #     training_data.extractall(path_to_data)    # path_to_yolov5 = os.path.join(path_to_data,'yolov5')
    #     #os.remove(os.path.join(path_to_data,'train_data.tar'))
    # print(input_dataset_type.split('.')[0])
    # sys.exit()
    list_of_contents = os.listdir((os.path.join(path_to_data,input_dataset_type.split('.')[0],'')))
    # print(list_of_contents)
    if len(list_of_contents)==0:
        print('Train data folder has no files!')
        sys.exit()
    # sys.exit()
    
    supported_image_formats = conf['data_type']['image_data_type']
    supported_label_formats = conf['data_type']['labels_data_type']

    unsupported_files = []
    #Checking formats of images and labels 
    for i in list_of_contents:
        if i.split('.')[-1] in supported_image_formats or i.split('.')[-1] in supported_label_formats:
            pass
        else:
            unsupported_files.append(i)
    if len(unsupported_files)==0:
        print('All the files present in training folder are in supported format. Now, image and label matching will begin')
    else:
        print(len(unsupported_files),'unsupported files are present in the training folder. Please fix the following files to continue:\n',unsupported_files)
        sys.exit()
    
    #checking images and their corresponding labels
    image_list = []
    label_list = []
    for i in list_of_contents:
        file_format = i.split('.')[-1]
        if file_format in supported_image_formats and i!='labels.txt':
            image_list.append(''.join(i.split('.')[0:-1]))
        if file_format in supported_label_formats and i!='labels.txt':
            label_list.append(''.join(i.split('.')[0:-1]))

    print('uncommon-------------',set(label_list)^set(image_list))
    mismatched_images = list(set(image_list)-set(label_list))
    mismatched_labels = list(set(label_list)-set(image_list))
    if len(mismatched_images) == 0:
        print('No mismatched images or labels found')
    if len(mismatched_images) != 0:
        print(len(mismatched_images),'mismacthed images found!Kindly fix following images before continuing:\n',mismatched_images)
        sys.exit()
    if len(mismatched_labels) != 0:
        print(len(mismatched_labels),'mismacthed labels found!Kindly fix following labels before continuing:\n',mismatched_labels)
        sys.exit()


    #checking file size of images and labels
    empty_files = []    
    for i in list_of_contents:
        file_size = os.path.getsize(os.path.join(path_to_data,input_dataset_type.split('.')[0],i))
        if file_size <5:
            empty_files.append(i)
        print(file_size,'bytes')
    if len(empty_files)==0:
        print('No empty files are found in training folder!')
    else:
        print(len(empty_files),'empty files are present in training folder. Please fix the following files before continuing:\n',empty_files)
        sys.exit()
        
    #checking label index and coords
    label_files = []
    total_label_index = set()
    for file in list_of_contents:
        if file.split('.')[-1] == 'txt' and file!='labels.txt':
            with open(os.path.join(path_to_data,input_dataset_type.split('.')[0],file),'r') as label_file:
                lines = label_file.readlines()
                non_int_index = set()
                non_float_coords = set()
                for l in lines:
                    label_data = l.replace('\n', '').split()                    
                    def check_int(int_data):
                        try:
                            int(int_data)
                            total_label_index.add(int(int_data))
                            # print('value is int')
                        except ValueError:
                            non_int_index.add(file)
                            return "Not int"
                        
                    def check_float(float_data):
                        try:
                            float(float_data)
                            # print('value is float')
                        except ValueError:
                            non_float_coords.add(file)
                            return "Not float"
                    check_int(label_data[0])
                    for coord in label_data[1:]:
                        check_float(coord)
    if len(non_int_index)==0:
        print('Label index are all good')
    else:
        print(len(non_int_index),'files have wrong index value type. Those files are:\n ',list(non_int_index))
    
    if len(non_float_coords)==0:
        print('Label coords are all good')
    else:
        print(len(non_float_coords),'files have wrong coords value type. Those files are:\n ',list(non_float_coords))
    # sys.exit()
    
    #checking number of labels in label files and labels.txt
    if 'labels.txt' in list_of_contents:
        with open(os.path.join(path_to_data,input_dataset_type.split('.')[0],'labels.txt'),'r') as lab:
            lab_content = lab.readlines()
            lab_content = [i.rstrip('\n') for i in lab_content]
            # sys.exit()
            if len(lab_content) == len(total_label_index):
                print("All the label files and 'labels.txt' have same number of fields!")
            else:
                print("Number of fields mismatch between label files and 'labels.txt'")
    else:
        print("labels file missing!Please add 'labels.txt' file.")

    #making config file    
    nc = len(lab_content)
    names = lab_content
    with open(os.path.join(path_to_data,'custom_file.yaml'),'w') as custom_f:
        custom_f.write('train: ../train_data/images/train/'+'\n'+'val: ../train_data/images/val/'+'\n'+str('nc:'+str(nc))+'\n'+str('names:'+str(names)))
    
    data_prep_prompt = input('All validations passed! Would you like to prepare the dataset for training? y/n: ')
    
    if data_prep_prompt.lower() =='y' or data_prep_prompt.lower() =='yes':
    #splitting data into train and val
        validation_percentage = input('Please enter validation percentage: ')
        image_files_list = []
        label_files_list = []
        new_folder = ['train', 'val']
        train_data_path = os.path.join(path_to_data,input_dataset_type.split('.')[0])
        training_data = os.listdir(train_data_path)
        for data in training_data:
            if data !='labels.txt':
                if imghdr.what(os.path.join(train_data_path,data)) is None:
                    label_files_list.append(data)
                else:
                    image_files_list.append(data)
        print(image_files_list)
        print(label_files_list)
        images_path = os.path.join(train_data_path,'images')
        labels_path = os.path.join(train_data_path,'labels')
        os.mkdir(images_path)
        os.mkdir(labels_path)
        
        val_samples = int(len(image_files_list) / int(100/int(validation_percentage)))
        for folder in new_folder:
            if folder == 'train':
                os.mkdir(os.path.join(images_path, folder))
                random.Random(4).shuffle(image_files_list)
                for file in image_files_list[val_samples:]:
                    os.replace(os.path.join(train_data_path, file), os.path.join(images_path, folder, file))
                os.mkdir(os.path.join(labels_path, folder))
                random.Random(4).shuffle(label_files_list)
                for file in label_files_list[val_samples:]:
                    os.replace(os.path.join(train_data_path, file), os.path.join(labels_path, folder, file))
            if folder == 'val':
                os.mkdir(os.path.join(images_path, folder))
                for file in image_files_list[0:val_samples]:
                    os.replace(os.path.join(train_data_path, file), os.path.join(images_path, folder, file))
                os.mkdir(os.path.join(labels_path, folder))
                for file in label_files_list[0:val_samples]:
                    os.replace(os.path.join(train_data_path, file), os.path.join(labels_path, folder, file))
        print('Data has been prepared successfully!')
    
    sys.exit()
    
#     if len(list_of_contents[1][1]) == 2 and list_of_contents[1][1][0]=='images' and list_of_contents[1][1][1] and list_of_contents[1][2][0] == 'classes.txt':
#         train_data_folder = list_of_contents[1][0]
#         print(train_data_folder)
#         # sys.exit()
#         classes_file_name = list_of_contents[1][2][0]
#         # config_file_name = list_of_contents[1][2][0]
#         print('--------------',classes_file_name)
    
#         image_path = list_of_contents[2][0]
#         label_path = list_of_contents[3][0]
#         # print('----',image_path,'------',label_path)
    
#         image_files = list_of_contents[2][2]
#         label_files = list_of_contents[3][2]
#         label_files_copy = label_files.copy()
        
#         # sys.exit()
#         format_list = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']
#         mismatched = 0
#         matched = 0
#         total = 0
#         mismatched_list = None
#         print('------------',format_list)
#         if len(image_files) == len(label_files):
#             image_mismatch = []
#             total = len(image_files)
#             labels_list = [''.join(j.split('.')[:-1]) for j in label_files]
#             classes_file = os.path.join(train_data_folder,classes_file_name)
#             classes_index_in_labels = []
#             with open(classes_file,'r') as cl:
#                 # config_content = yaml.safe_load(cl)
#                 classes_content = cl.readlines()
#                 classes_content_copy = classes_content.copy()
#                 # classes_content_copy = [i.replace('\n','') for i in classes_content]
#                 for i in ['dog\n', 'person\n', 'cat\n', 'tv\n', 'car\n', 'meatballs\n', 'marinara sauce\n', 'tomato soup\n', 'chicken noodle soup\n', 'french onion soup\n', 'chicken breast\n', 'ribs\n', 'pulled pork\n', 'hamburger\n', 'cavity\n']:
#                     classes_content_copy.remove(i)
#                 print(classes_content)
#                 # sys.exit()
#                 for i in label_files:
#                     with open(os.path.join(label_path,i),'r') as lab:
#                         label_lines = lab.readlines()
#                         new_index_list = []
#                         for line in label_lines:
#                             index_value = line.split()[0]
#                             classes_index_in_labels.append(index_value)
#                             class_name = classes_content[int(index_value)]
#                             new_index = classes_content_copy.index(class_name)
#                             new_index_list.append(new_index)
#                             with open(os.path.join(label_path,i),'w') as la:
#                                     for line,ind in zip(label_lines,new_index_list):
#                                         print(ind,line.split()[0])
#                                         line = line.split()
#                                         line[0]=str(ind)
#                                         print(line)
#                                         la.write(' '.join(line)+'\n')
#             #     # sys.exit()
#             print(len(classes_content),len(set(classes_index_in_labels)))
#             if len(classes_content) >= len(set(classes_index_in_labels)):
#                 print('classes validation completed!')
#                 pass
#                 # sys.exit()
#             else:
#                 print(Fore.RED+'Total classes mentioned mismatched with listed number of classes!'+Style.RESET_ALL)
#             #     sys.exit()
#             classes_in_label_file = []
#             for i,l in zip(image_files,label_files):
#                 with open(os.path.join(label_path,l),'r') as label_text_file:
#                     texts = label_text_file.readlines()
#                     print('-----------',texts)
#                     for t in texts:
#                         t = t.replace('\n', '')
#                         entry_list = t.split()
#                         try:
#                             if int(entry_list[0]):
#                                 print(Fore.GREEN+'class indices are correct!'+Style.RESET_ALL)
#                                 classes_in_label_file.append(int(entry_list[0]))
#                         except ValueError as ve:
#                             print(Fore.RED+'Invalid datatype for class index found in'+Style.RESET_ALL,l)
    
#                         try:
#                             if 0<float(entry_list[1])<1 and 0<float(entry_list[2])<1 and 0<float(entry_list[3])<1 and 0<float(entry_list[4])<1:
#                                 print(Fore.GREEN+'Coordinates datatype check successful!'+Style.RESET_ALL)
#                                 pass
#                         except:
#                             print(Fore.RED+'Something seems wrong with coordinates in label file'+Style.RESET_ALL,l)
#                             sys.exit()
    
#                 var_i = i
#                 var_l = l
#                 i_format = var_i.split('.')[-1].lower()
#                 l_format = var_l.split('.')[-1].lower()
#                 if i_format in format_list:
#                     pass
#                 else:
#                     print(Fore.RED+'Either one or more images have unsupported format! Please fix to continue'+Style.RESET_ALL)
#                     print('Hint! : ', i)
#                     sys.exit()
#                 if l_format == 'txt':
#                     pass
#                 else:
#                     print(Fore.RED+'Either one or more labels have unsupported format! Please fix to continue'+Style.RESET_ALL)
#                     print('Hint! : ',l)
#                     sys.exit()
#                 im = ''.join(i.split('.')[:-1])
#                 if im in labels_list:
#                     label_files_copy.remove(im+'.txt')
#                 else:
#                     image_mismatch.append(i)
#             if len(label_files_copy) == 0:
#                 matched = total
#                 print('total: ',f'{Fore.BLUE}',total,f'{Style.RESET_ALL}','\n','matched: ',f'{Fore.BLUE}',matched,f'{Style.RESET_ALL}','\n','mismatched: ',f'{Fore.BLUE}',mismatched,f'{Style.RESET_ALL}')
#             else:
#                 mismatched = len(label_files_copy)
#                 mismatched_list = label_files_copy
#                 print('total: ',f'{Fore.BLUE}',total,f'{Style.RESET_ALL}','\n','matched: ',f'{Fore.BLUE}',total-mismatched,f'{Style.RESET_ALL}','\n','mismatched: {} images and {} labels'.format(f'{Fore.RED}',mismatched,f'{Style.RESET_ALL}',f'{Fore.RED}',mismatched,f'{Style.RESET_ALL}'),'\n','mismatch list: ',f'{Fore.RED}',image_mismatch,mismatched_list,f'{Style.RESET_ALL}')
#                 sys.exit()
#         else:
#             print(Fore.RED+"number of images and labels don't match"+Style.RESET_ALL)
#             # sys.exit()
#             # f"{Fore.BLUE}Hello World{Style.RESET_ALL}"
#         return path_to_data, list_of_contents, train_data_folder, image_path, label_path, image_files,label_files,classes_file_name,classes_content_copy
#     else:
#         print('Something seems wrong in training data folder!')
#         sys.exit()
# # 


print(inp_val())
