import os
import sys
import argparse

#---------------Расширения моделей--------------
const_caffemodel = '.caffemodel'
const_tfmodel = '.pb'
valid_data_types = [ 'FP16', 'FP32', 'half', 'float' ]
#-----------------------------------------------

#---------------Парсер аргументов---------------
def build_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mo_dir', type = str,
        dest = 'path_to_mo', help = 'Path to folder with model optimizer')
    parser.add_argument('-i', '--input_dir', type = str,
        dest = 'path_to_models', help = 'Path to folder with models')
    parser.add_argument('-d', '--data_type', type = str,
        dest = 'data_type', help = 'Data type for convert models')
    
    args = parser.parse_args()
    
    return args
#-----------------------------------------------

#--------Проверка корректности аргументов-------
def parse_arg(args):
    error = 0
    if ((args.path_to_mo == None) or (args.path_to_models == None) or
        (args.data_type == None)):
        raise ValueError('Expression expected : converter.py \
            --mo_dir <path to model oprimizer> \
            --input_dir <path to folder with models> \
            --data_type <data type for convert model>')
    
    mo = os.path.join(args.path_to_mo, 'mo.py')
    
    if (not(os.path.isfile(mo))):
        raise ValueError('Wrong path to folder with model optimizer')
    
    if (not(os.path.isdir(args.path_to_models))):
        raise ValueError('Wrong path to folder with models')
        
    if (args.data_type not in valid_data_types):
        raise ValueError('Wrong data type')

    return [args.path_to_mo, args.path_to_models, args.data_type]
#--------------------------------------------

#----Функция конвертации caffe моделей-------
def caffe_converter(path_to_mo, path_to_models, data_type):
    count = 0
    
    mo = os.path.join(path_to_mo, 'mo.py')
    
    for root, dirs, files in os.walk(path_to_models):
        for file in files:
            if file.endswith(const_caffemodel):
                model = os.path.join(root, file)
                output = os.path.join(root, 'ir', data_type)
                
                command = '{0} --input_model {1} --output_dir {2} \
                --data_type {3}'.format(mo, model, output, data_type)
                
                os.system(command)
                
                count += 1

    return count
#--------------------------------------------

#----Функция конвертации tf моделей----------
def tf_converter(path_to_mo, path_to_models, data_type):
    count = 0
    
    support_config = os.path.join(path_to_mo, 'extensions',
        'front', 'tf', 'ssd_v2_support.json')
    mo = os.path.join(path_to_mo, 'mo_tf.py')
    
    for root, dirs, files in os.walk(path_to_models):
        for file in files:
            if ((file != 'saved_model.pb') and 
                (file.endswith(const_tfmodel))):
                model = os.path.join(root, file)
                pipeline_config = os.path.join(root, 'pipeline.config')
                output = os.path.join(root, 'ir', data_type)
                
                command = '{0} --input_model {1} --output_dir {2} \
                --data_type {3} --tensorflow_use_custom_operations_config \
                {4} --tensorflow_object_detection_api_pipeline_config \
                {5}'.format(mo, model, output, data_type, 
                support_config, pipeline_config)
                
                os.system(command)
                
                count += 1
    
    return count
#--------------------------------------------

#---------Функция конвертации моделей--------
def models_converter(path_to_mo, path_to_models, data_type):
    count = 0
    
    count += caffe_converter(path_to_mo, path_to_models, data_type)
    count += tf_converter(path_to_mo, path_to_models, data_type)
    
    if (count == 0):
        raise ValueError('No models in folder')
    
    return 0
#-------------------------------------------

#-------------------Main--------------------
if __name__ == '__main__':
    try:
        [path_to_mo, path_to_models, data_type] = parse_arg(build_argparse())
        models_converter(path_to_mo, path_to_models, data_type)
    except Exception as Exp:
        print('ERROR! : {0}'.format(str(Exp)))
        sys.exit()
    print('Convert completed!')
#-------------------------------------------