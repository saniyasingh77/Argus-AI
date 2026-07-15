import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

# load dataset
X = np.load("X.npy")
y = np.load("y.npy")

# automatically detect number of classes
num_classes = len(set(y))

print("Number of classes:", num_classes)

# convert labels
y = to_categorical(y, num_classes=num_classes)

# create model
model = Sequential([
    Dense(128, activation="relu", input_shape=(66,)),
    Dense(64, activation="relu"),
    Dense(32, activation="relu"),
    Dense(num_classes, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# train model
model.fit(
    X,
    y,
    epochs=20
)

# save model
model.save("backend/activity_model.h5")

print("Model training complete")