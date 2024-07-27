import os

directory_path_bit = 'faces/bit'
directory_path_car = 'faces/car'

def get_bit_names():
    file_names = os.listdir(directory_path_bit)
    print("Files in the directory:")
    res = []
    for file_name in file_names:
        print(file_name)
        res.append(file_name.split('.')[0])
    return res

def get_car_names():
    file_names = os.listdir(directory_path_car)
    print("Files in the directory:")
    res = []
    for file_name in file_names:
        print(file_name)
        res.append(file_name.split('.')[0])
    return res

face_bit_names = [
    'HAPPY-SMILE',
    'DUMB',
    'DOUBT',
    'LOOKAROUND-RIGHT',
    'LAUGH',
    'HUH',
    'WRONGED',
    'QUESTION',
    'ANGRY',
    'SPEECHLESS',
    'SLOBBER',
    'CRY',
    'SAD',
    'DEFAULT',
    'OGLE',
    'CLOSE-EYE',
    'UNHAPPY',
    'SMIRK',
    'AWKWARD-SMILE',
    'SMILE',
    'LOOKAROUND-MIDDLE',
    'SHOCK',
    'HAPPY',
    'SLEEP',
    'LOOKAROUND-LEFT',
    'SOB',
    'LIKE',
    'DOWNTIME']

face_car_names = ['STUPID-LAUGH',
    'DOUBT',
    'OOPS',
    'SOB',
    'INSIDIOUS',
    'SAN',
    'CRY',
    'SMILE',
    'SPEECHLESS',
    'LOOKAROUND',
    'SLEEP',
    'AFRAID',
    'SPOILED',
    'LAUGH',
    'DEFAULT',
    'SWEAT',
    'LOVE',
    'DAZE',
    'CUTE',
    'ANGRY']
