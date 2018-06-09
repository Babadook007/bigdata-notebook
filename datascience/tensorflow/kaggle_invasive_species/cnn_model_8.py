#nvidia-smi
#~/.keras/keras.json

#import keras
#print keras.__version__
#1.2.2
#https://faroit.github.io/keras-docs/1.2.2/


from keras.models import Sequential
from keras.layers.pooling import MaxPooling2D
from keras.layers.core import Dense
from keras.layers.core import Flatten
from keras.layers.core import Dropout
from keras.layers.convolutional import Conv2D
from keras.layers.pooling import MaxPooling2D
from keras.models import model_from_json
from keras.layers.normalization import BatchNormalization
from keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
#check 
#from tensorflow.python.client import device_lib
#print(device_lib.list_local_devices())

#load previous model
#json_file = open('cnn_model_3.json', 'r')
#loaded_model_json = json_file.read()
#json_file.close()
#classification = model_from_json(loaded_model_json)


def getModel():
	classification = Sequential()
	classification.add(Conv2D(16, 3,3, input_shape=(128, 128, 3), activation = 'relu'))
	classification.add(MaxPooling2D())
	classification.add(Conv2D(64, 3,3, activation = 'relu'))
	classification.add(MaxPooling2D())
	classification.add(Conv2D(128, 3,3, activation = 'relu'))
	classification.add(MaxPooling2D())
	classification.add(Conv2D(256, 3,3, activation = 'relu'))
	classification.add(MaxPooling2D())
	classification.add(Conv2D(512, 3,3, activation = 'relu'))
	classification.add(MaxPooling2D())
	classification.add(Dropout(0.25))
	classification.add(Flatten())
	classification.add(Dense(1024, activation = 'relu'))
	classification.add(BatchNormalization())
	classification.add(Dense(1, activation = 'sigmoid'))
	adam_optimizer = Adam(lr=0.0001, decay=1e-6)
	classification.compile(optimizer=adam_optimizer, loss='binary_crossentropy', metrics = ['accuracy'])
	return classification


model = getModel()
for layer in model.layers:
    print(str(layer.name)+" "+str(layer.input_shape)+" -> "+str(layer.output_shape))


def getData():
	all_data_gen = ImageDataGenerator(rotation_range=30, shear_range=0.2, zoom_range=0.2, horizontal_flip=True, vertical_flip=True, fill_mode='nearest', width_shift_range = 0.2,
            height_shift_range = 0.2)
	date_gen = all_data_gen.flow_from_directory('training_set_all', target_size=(128, 128), batch_size=25, class_mode='binary', shuffle=False)
	return data_gen


def trainModel(model, train, test, train_size, test_size):
	model.fit_generator(train, samples_per_epoch=train_size, validation_data=test, nb_epoch=20, nb_val_samples=test_size)

def kFoldCrossValidation(folds):
	data = getData()
	labels = data.classes
	skf = StratifiedKFold(labels, n_folds=folds, shuffle=True)

	for i, (train, val) in enumerate(skf):
		print("fold ", i)
		model = None
		model = getModel()
		trainModel(model, data[train], data[test], train.size, )


classification_json = classification.to_json()
with open("cnn_model_6.json", "w") as json_file:
    json_file.write(classification_json)

classification.save_weights("cnn_model_6.h5")
#80 val accuracy

valid_preds = classification.predict_generator(valid_gen, 150)
roc_auc_score(valid_gen.classes, valid_preds)
#0.48

#train on all training set
'''
train_all_data_gen = ImageDataGenerator(rotation_range=20, rescale=1./255, shear_range=0.4, zoom_range=0.1, horizontal_flip=True)
train_all_gen = train_data_gen.flow_from_directory('training_set_all', target_size=(128, 128), batch_size=25, class_mode='binary')
classification.fit_generator(train_all_gen, samples_per_epoch=2295, nb_epoch=20)

classification.save_weights("cnn_model_5_2.h5")
'''
#mv test/*.jpg test/unknown/
test_data_gen = ImageDataGenerator(rescale=1./255)
test_gen = test_data_gen.flow_from_directory('test', target_size=(128, 128), batch_size=25, class_mode='binary', shuffle=False)

prediction = classification.predict_generator(test_gen, 1531)


result = []
filenames = test_gen.filenames
for i in range(len(filenames)):
	result.append((int(filenames[i].split("/")[1].split(".")[0]), prediction[i][0]))

result.sort(key=lambda tup: tup[0])

with open("submission6.csv", "w") as output:
	output.write("name,invasive\n")
	for i in range(0, len(result)):
		output.write(str(result[i][0])+","+str(result[i][1])+"\n")

#92.7% score
