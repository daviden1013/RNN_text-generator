'''
Created on Jul 31, 2017

@author: david_000
'''

import numpy as np
import pyodbc
import operator
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.models import load_model

# load data
conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\david_000\AppData\Local\Programs\Python\Python35\Scripts\tutorial\reddit.accdb;' 
        )
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()

SQL = "SELECT title FROM LPT WHERE haha LIKE '%201701%'"
cursor.execute(SQL)

title = []
for row in cursor.fetchall():
    title.append(row[0])

cursor.close()
cnxn.close()
# subset
title = title[0:len(title)//3 * 2]
# join title strings
title_str = '\n'.join(title)
# make white list
white_list = "\n abcdefghijklmnopqrstuvwxyz,.:;?'������*-"
# convert title strings to lower case
title_str = title_str.lower()
# replace chars not in white list with '*'
title_str_reduced = ''.join([ch if ch in white_list else '*' for ch in title_str])
# get unique chars
chars = list(set(title_str_reduced))
# make char to int index mapping
char2int = {}
for i in range(len(chars)):
    char2int[chars[i]] = i   
# make int index to char mapping
int2char = {}
for i in range(len(chars)):
    int2char[i] = chars[i]   
# make char to one hot vector mapping
char2vec = {}
for ch, i in char2int.items():
    char2vec[ch] = np.eye(len(chars))[i]
# make data
seq_length = 100
x = []
y = []
for i in range(len(title_str_reduced) - seq_length):
    x.append([char2int[index] for index in title_str_reduced[i:i+seq_length]])
    y.append(char2vec[title_str_reduced[i+seq_length]])

x = np.reshape(x, (len(x), seq_length, 1))
x = x/float(len(chars))
y = np.reshape(y, (len(y), len(chars)))
# define model structure
model = Sequential()
model.add(LSTM(256, input_shape = (None, 1), return_sequences = True))
model.add(Dropout(0.2))
model.add(LSTM(256))
model.add(Dropout(0.2))
model.add(Dense(len(chars), activation = "softmax"))
model.compile(loss='categorical_crossentropy', optimizer='adam')
# define the checkpoint
filepath="LPT-{epoch:02d}-{loss:.4f}.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
callbacks_list = [checkpoint]
# fit the model
model.fit(x, y, epochs=40, batch_size=50, callbacks=callbacks_list)
'''

'''
#model = load_model("LPT-39-1.3290.h5")


'''
 Generate text
'''
# load best model
model = Sequential()
model.add(LSTM(256, input_shape = (None, 1), return_sequences = True))
model.add(Dropout(0.2))
model.add(LSTM(256))
model.add(Dropout(0.2))
model.add(Dense(len(chars), activation = "softmax"))
model.load_weights("LPT-00-2.8352.h5")
model.compile(loss='categorical_crossentropy', optimizer='adam')

# predict
out = 'lpt'
for i in range(10):
    pattern = [char2int[ch] for ch in out]
    pattern = np.reshape(pattern, (1, len(out), 1))
    pattern = pattern/float(len(chars))
    pre = model.predict(pattern).reshape(-1)
    index, value = max(enumerate(pre), key=operator.itemgetter(1))
    next = int2char[index]
    out += next

out


