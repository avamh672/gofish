import os
from datetime import datetime
import functools
import sys

import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, LeakyReLU
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping

#A mask for which parameters you fixed (1) vs fit (0) when generating the training data. Must match the one in the emulator.
significantBeamParams = [0,1,1,0,1,0,0,1,0,0,0,0,0]
significantTargetParams = [1,0,1,1,1,0,0,1,0,1,1,0,1,0,1,1,1,0,0,0,1,1]

#Uncomment and run with this if you need to get the normalization parameters from the training data
"""
#Read results from files
f = open("beamInputs.csv",'r')
X = np.empty((90000,sum(significantBeamParams)+sum(significantTargetParams)))
lineCount = 0
newline = f.readline()
while newline:
  params = newline.strip("[ ]\n").split(',')
  params = [float(x) for x in params]
  for i in range(len(params)):
    if significantBeamParams[i] == 1:
      X[lineCount,sum(significantBeamParams[:i])] = params[i]
  lineCount += 1
  newline = f.readline()
f.close()


f = open("targetInputs.csv",'r')
lineCount = 0
newline = f.readline()
while newline:
  params = newline.strip("[ ]\n").split(',')
  params = [float(x) for x in params]
  for i in range(len(params)):
    if significantTargetParams[i] == 1:
      X[lineCount,sum(significantBeamParams)+sum(significantTargetParams[:i])] = params[i]
  lineCount += 1
  newline = f.readline()
f.close()

#f = open("mcChisq.csv",'r')
f = open("gosiaOutputs.csv",'r')
#Y = np.empty((90000,1))
Y = np.empty((90000,72))
lineCount = 0
newline = f.readline()
while newline:
  outputs = newline.strip("[ ]\n").split(',')
  #if len(outputs) != 73:
    #print(lineCount,newline)
  outputs = [float(x) for x in outputs]
  #Y[lineCount,:] = outputs[-1]
  Y[lineCount,:] = outputs[:-1]
  lineCount += 1
  newline = f.readline()
f.close()

#prepare data for NN by mean-centering

X_nn = X.copy()
X_min = X_nn.min(axis=0)
X_max = X_nn.max(axis=0)
#print(X_min,X_max)

X_nn = (X_nn - X_min)/(X_max - X_min)

Y_nn = Y.copy()

Y_min = Y_nn.min(axis=0)
Y_max = Y_nn.max(axis=0)

f = open("batchNormalizationParameters.csv",'w')
xminstring = ""
for xmin in X_min:
  xminstring += str(xmin) + ","
xminstring = xminstring[:-1] + "\n"
f.write(xminstring)
xmaxstring = ""
for xmax in X_max:
  xmaxstring += str(xmax) + ","
xmaxstring = xmaxstring[:-1] + "\n"
f.write(xmaxstring)
yminstring = ""
for ymin in Y_min:
  yminstring += str(ymin) + ","
yminstring = yminstring[:-1] + "\n"
f.write(yminstring)
ymaxstring = ""
for ymax in Y_max:
  ymaxstring += str(ymax) + ","
ymaxstring = ymaxstring[:-1] + "\n"
f.write(ymaxstring)
f.close()
"""



model = Sequential()           
model.add(Dense(100,input_dim=17,activation='relu',kernel_initializer='VarianceScaling', ))
model.add(BatchNormalization())
model.add(Dense(200,activation='relu',kernel_initializer='VarianceScaling'))
model.add(BatchNormalization())
model.add(Dense(100,activation='relu',kernel_initializer='VarianceScaling'))
model.add(BatchNormalization())
model.add(Dense(72,activation='relu',kernel_initializer='VarianceScaling'))

model.compile(loss='mean_squared_error',optimizer='nadam')
print(model.summary())

model.load_weights('grid_weights_best_43.h5')

f = open("batchNormalizationParameters.csv",'r')
X_min = [float(x) for x in f.readline().strip().split(",")]
X_max = [float(x) for x in f.readline().strip().split(",")]
Y_min = [float(x) for x in f.readline().strip().split(",")]
Y_max = [float(x) for x in f.readline().strip().split(",")]
f.close()

X_min = np.array(X_min)
X_max = np.array(X_max)
Y_min = np.array(Y_min)
Y_max = np.array(Y_max)


f = open("beamInputsToEmulator.csv",'r')
X = np.empty((5000,sum(significantBeamParams)+sum(significantTargetParams)))
lineCount = 0
newline = f.readline()
while newline:
  params = newline.strip("[ ]\n").split(',')
  params = [float(x) for x in params]
  for i in range(len(params)):
    if significantBeamParams[i] == 1:
      X[lineCount,sum(significantBeamParams[:i])] = params[i]
  lineCount += 1
  newline = f.readline()
f.close()

f = open("targetInputsToEmulator.csv",'r')
lineCount = 0
newline = f.readline()
while newline:
  params = newline.strip("[ ]\n").split(',')
  params = [float(x) for x in params]
  for i in range(len(params)):
    if significantTargetParams[i] == 1:
      X[lineCount,sum(significantBeamParams)+sum(significantTargetParams[:i])] = params[i]
  lineCount += 1
  newline = f.readline()
f.close()

X_nn = X.copy()
X_nn = (X_nn - X_min)/(X_max - X_min)

Y_nn = model(X_nn,training=False)
Y_emulator = Y_nn*(Y_max-Y_min) + Y_min

f = open("emulatorOutputs.csv",'w')
for rownum in range(Y_emulator.shape[0]):
  yemstring = ""
  for i in range(72):
    yemstring += str(float(Y_emulator[rownum,i])) + ","
  yemstring = yemstring[:-1] + "\n"
  f.write(yemstring)
f.close()
