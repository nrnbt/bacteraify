import os

COLORS = [
    '#FFFDD0',
    '#A52A2A',
    '#ADFF2F',
    '#FFC0CB',
    '#FF1493',
    '#9370DB',
    '#4B0082',
    '#8A2BE2',
    '#FFA500',
    '#FF0000',
    '#800020',
    '#FFFF00',
    '#0000FF',
    '#00008B',
    '#FFD700',
    '#FFD700',
    '#C0C0C0',
    '#A9A9A9',
    '#CD7F32',
    '#FA8072',
    '#FFFFFF',
    '#808080',
    '#A52A2A',
    '#90EE90',
    '#006400',
    '#FF4500',
    '#FF2400',
    '#FF007F',
    '#FF7F50',
    '#9B111E'
]

STRAINS = {
    0: "C. albicans",
    1: "C. glabrata",
    2: "K. aerogenes",
    3: "E. coli 1",
    4: "E. coli 2",
    5: "E. faecium",
    6: "E. faecalis 1",
    7: "E. faecalis 2",
    8: "E. cloacae",
    9: "K. pneumoniae 1",
    10: "K. pneumoniae 2",
    11: "P. mirabilis",
    12: "P. aeruginosa 1",
    13: "P. aeruginosa 2",
    14: "MSSA 1",
    15: "MSSA 3",
    16: "MRSA 1 (isogenic)",
    17: "MRSA 2",
    18: "MSSA 2",
    19: "S. enterica",
    20: "S. epidermidis",
    21: "S. lugdunensis",
    22: "S. marcescens",
    23: "S. pneumoniae 2",
    24: "S. pneumoniae 1",
    25: "S. sanguinis",
    26: "Group A Strep.",
    27: "Group B Strep.",
    28: "Group C Strep.",
    29: "Group G Strep.",
}

CNN_MODEL_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'cnn_model.h5')
SVM_MODEL_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'svm_model.pkl')
RNN_MODEL_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'rnn_model.h5')
UPLOAD_FILE_PATH = os.path.dirname(os.path.dirname(__file__))
