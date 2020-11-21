# data
PALETTE = [255]

# loss
LOSS = "focal_dice"
GAMMA = 2.0  # focal loss gamma

OPTIMIZER = "sgd"

FREEZE = False
FREEZE_AT = 16

# hyperparameter
DROPOUT_RATE = 0.1
MOMENTUM = 0.9
LEARNING_RATE = 1e-2

IMAGE_SIZE = (216, 320, 1)  # (216, 320, 1) # (270, 400, 1) # (432, 640, 1)
BATCH_SIZE = 4
EPOCHS = 200
