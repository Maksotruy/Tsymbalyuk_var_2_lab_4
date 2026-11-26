MIN_DISTANCE = 3
MAX_FIELD_SIZE = 40
MAX_GENERATION_ATTEMPTS = 100

MODES = {
    "1": "Класичний",
    "2": "Розширений"
}

DIFFICULTIES = {
    "1": "Легка",
    "2": "Середня",
    "3": "Важка"
}

LEVELS = {
    "Класичний": [
        (2, 0, (1, 2), None, 1, 15),
        (3, 0, (2, 3), None, 1, 15),
        (4, 0, (2, 3), None, 1, 15)
    ],

    "Розширений": [
        (4, 0, (1, 2), None, 1, 15),
        (6, 2, (1, 3), 5, 3, 20),
        (9, 4, (2, 3), 3, 5, 25)
    ]
}

DYNAMIC_SETTINGS = {
    "Легка": {
        "route_ratio": 0.50,
        "speed": (1, 1),
        "travel": (3, 5),
        "diagonal": False
    },

    "Середня": {
        "route_ratio": 0.65,
        "speed": (1, 1),
        "travel": (3, 5),
        "diagonal": False
    },

    "Важка": {
        "route_ratio": 0.80,
        "speed": (1, 2),
        "travel": (4, 7),
        "diagonal": True
    }
}

MOVING_SYMBOLS = {
    (1, 0): ">",
    (-1, 0): "<",
    (0, 1): "v",
    (0, -1): "^",
    (1, 1): "↘",
    (-1, -1): "↖",
    (1, -1): "↗",
    (-1, 1): "↙"
}