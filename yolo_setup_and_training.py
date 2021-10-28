import os
from colorama import Fore, Style
import yaml
import sys
import shutil
import stat
import random
from input_validation_for_yolov5 import inp_val

path_to_data, list_of_contents, train_data_folder, image_path, label_path, image_files,label_files,classes_file_name,classes_content_copy = inp_val()

os.remove(os.path.join(train_data_folder,'classes.txt'))
answer = input('validation completed successfully! Would you like to prepare data for training?(y/n) ')
if answer.lower() == 'yes' or answer.lower() == 'y':   
    classes_content_copy = [i.replace('\n','') for i in classes_content_copy]
    print(classes_content_copy)
    # sys.exit()
    
    new_folder = ['train', 'val']
    print(classes_content_copy)
    # sys.exit()
    
    epochs = 1
    batch_size = 4
    weights_size = 'm'
    validation_percentage = 20
    
    
    val_samples = int(len(list_of_contents[2][2]) / int(100/validation_percentage))
    for folder in new_folder:
        if folder == 'train':
            os.mkdir(os.path.join(image_path, folder))
            random.Random(4).shuffle(image_files)
            for file in image_files[val_samples:]:
                os.replace(os.path.join(image_path, file), os.path.join(image_path, folder, file))
            os.mkdir(os.path.join(label_path, folder))
            random.Random(4).shuffle(label_files)
            for file in label_files[val_samples:]:
                os.replace(os.path.join(label_path, file), os.path.join(label_path, folder, file))
        if folder == 'val':
            os.mkdir(os.path.join(image_path, folder))
            for file in image_files[0:val_samples]:
                os.replace(os.path.join(image_path, file), os.path.join(image_path, folder, file))
            os.mkdir(os.path.join(label_path, folder))
            for file in label_files[0:val_samples]:
                os.replace(os.path.join(label_path, file), os.path.join(label_path, folder, file))
    
    os.chdir(path_to_data)
    
    list_of_folders = list(os.walk(path_to_data))
    print(list_of_folders[0][1])
    # sys.exit()
    
    def remove_readonly(func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    if 'yolov5' in list_of_folders[0][1]:
        print('deleting folder......')
        # os.system("rmdir /s "+ path+"\yolov5")
        shutil.rmtree(os.path.join(path_to_data,'yolov5'), onerror=remove_readonly)
        os.system('git clone https://github.com/ultralytics/yolov5.git')
    else:
        os.system('git clone https://github.com/ultralytics/yolov5.git')
    # # sys.exit()
    with open(os.path.join(path_to_data,'yolov5\data\custom_data.yaml'),'w') as config: 
        dict_file1 = {'train':image_path.replace('\\', '/')+'/train/','val':image_path.replace('\\', '/')+'/val/','nc':len(classes_content_copy),'names':classes_content_copy,'epochs':epochs,'batch_size':batch_size,'weights':weights_size}
        yaml.dump(dict_file1, config,default_flow_style=True,sort_keys=False)
    answer = input('Dataset and config file are ready for training! Would you like to train the model?(y/n) ' )
    if answer.lower() == 'yes' or answer.lower() == 'y':   
        os.chdir(os.path.join(path_to_data,'yolov5'))
        with open(r"data\custom_data.yaml", "r") as stream:
            config = yaml.safe_load(stream)
            ep = config['epochs']
            bat = config['batch_size']
            wt = config['weights']
            print('------',ep,bat,wt)
        os.system("python train.py --img 640 --batch "+str(bat)+" --epochs "+str(ep)+" --data data\custom_data.yaml"+" --cfg yolov5"+wt+".yaml"+" --weights "+"yolov5"+wt+".pt --cache")
        # os.system("python train.py --img 640 --batch 4 --epochs 3 --data data\custom_file.yaml --cfg yolov5s.yaml --weights yolov5s.pt --cache")
        try:
            os.system("python export.py --weights yolov5" + wt + ".pt --img 640 --batch 1 ")
            print('yolov5 onnx model exported successfully! Thank you!')
        except Exception as e:
            print(e)
        os.chdir(path_to_data)
else:
    pass


    
    # model_dict = {'s': 'Small', 'm': 'Medium', 'l': 'Large', 'x': 'Extra-Large'}
    # while True:
    #     yolo_weights = input('Enter yolov5 weights, choose from : yolov5(s/m/l/x): ').lower()
    #     if yolo_weights == 's' or yolo_weights == 'm' or yolo_weights == 'l' or yolo_weights == 'x':
    #         print('You have chosen ' + f"{Fore.BLUE}" + model_dict[
    #             yolo_weights] + f"{Style.RESET_ALL}" + ' yolov5 model for training')
    #         break
    #     else:
    #         print(Fore.RED + 'wrong datatype or invalid model type selected! Try again.')
    # while True:
    #     number_of_epochs = input('Enter the number of epochs: ')
    #     if number_of_epochs.isdigit() and 0 < int(number_of_epochs):
    #         print('You have chosen ' + f"{Fore.BLUE}" + number_of_epochs + f"{Style.RESET_ALL}" + ' epochs for training')
    #         number_of_epochs = int(number_of_epochs)
    #         break
    #     else:
    #         print(Fore.RED + 'wrong datatype or an invalid number selected! Try again.' + Style.RESET_ALL)
    # while True:
    #     batch_size_for_training = input('Enter the batch size for training: ')
    #     if batch_size_for_training.isdigit() and 0 < int(batch_size_for_training):
    #         print(
    #             'You have chosen ' + f"{Fore.BLUE}" + batch_size_for_training + f"{Style.RESET_ALL}" + ' batch size for training')
    #         batch_size_for_training = int(batch_size_for_training)
    #         break
    #     else:
    #         print(Fore.RED + 'wrong datatype or invalid number selected! Try again.' + Style.RESET_ALL)
