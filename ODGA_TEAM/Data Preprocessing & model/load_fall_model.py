import serial
import numpy as np
import pandas as pd
from scipy.signal import medfilt
import scipy as sp
from tensorflow.keras.models import load_model
import tensorflow

ser = serial.Serial('/dev/ttyACM0', 9600)



model = load_model('./fall_cnn_model_5.h5')


def median(signal_x, signal_y, signal_z):
    array_x = np.array(signal_x)
    array_y = np.array(signal_y)
    array_z = np.array(signal_z)

    med_x = sp.signal.medfilt(array_x, kernel_size = 3)
    med_y = sp.signal.medfilt(array_y, kernel_size = 3)
    med_z = sp.signal.medfilt(array_z, kernel_size = 3)
    
    return med_x, med_y, med_z

def MakeVector(med_x, med_y, med_z):
    vec_run = ((med_x ** 2) + (med_y ** 2) + (med_z ** 2)) ** (1/2)
    
    return vec_run
    
def LoadModel(vector):
    predict = model.predict_classes(vector)
    print(predict)
    if predict == [0]:
        result = 'R'
    else:
        result = 'F'
    return result


axis_x = []
axis_y = []
axis_z = []
ser = serial.Serial('/dev/ttyACM0', 9600)

with ser:
    while True:
        if ser.readline():

            res = ser.readline()
            res = str(res)[:-5].replace("b'","")
            res = res.split(',')
            
            try: 
                res = list(map(int, res))    
            except:
                print('Fail Change Type')
        

            if len(res) == 3:
                axis_x.append(res[0])
                axis_y.append(res[1])
                axis_z.append(res[2])
            

            if len(axis_x) ==  218:            
                df = pd.DataFrame({'x' : axis_x, 'y' : axis_y, 'z' : axis_z})
                axis_x = []
                axis_y = []
                axis_z = []
                med_df = list(median(df.x, df.y, df.z))
                vec_xyz = MakeVector(med_df[0], med_df[1], med_df[2])
                vec_xyz = np.array(vec_xyz)
                vec_xyz = vec_xyz.reshape(1,218,1)
                ser.write(bytes(LoadModel(vec_xyz),'utf-8'))

