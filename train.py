from keras import models
from keras.applications import VGG16

if __name__=="__main__":
    print ("Loading VGG16 models...")
    model = VGG16(weights='imagenet', include_top=True)
    print (model.summary())
