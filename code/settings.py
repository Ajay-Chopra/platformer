SCREEN_WIDTH = 1200
TILE_SIZE = 64
VERTICAL_TILE_NUMBER = 11
SCREEN_HEIGHT = VERTICAL_TILE_NUMBER * TILE_SIZE

# Overworld setings
NODE_DATA = {
    "0": {
       "node_pos":(10,300), 
       "content": "this is level 0", 
       "unlock": "1"
    },
    "1": {
        "node_pos":(200,120), 
        "content": "this is level 1", 
        "unlock": "2"
    },
    "2": {
        "node_pos":(380,510), 
        "content": "this is level 2", 
        "unlock": "3"
    },
    "3": {
        "node_pos":(510,250), 
        "content": "this is level 3", 
        "unlock": "4"
    },
    "4": {
        "node_pos":(780,110), 
        "content": "this is level 4", 
        "unlock": "5"
    },
    "5": {
        "node_pos":(950,300), 
        "content": "this is level 5", 
        "unlock": "5"
    }
}
SELECTOR_SIZE = TILE_SIZE / 4
NODE_OFFSET = 100
LINE_COLOR = "#a04f45"

# UI settings
HEALTH_BAR_POS = (50, 50)
HEALTH_BAR_RECT_POS = (84, 79)
MAX_HEALTH_RECT_WIDTH = 152
HEALTH_RECT_HEIGHT = 4
GOLD_COIN_IMAGE_POS = (45, 120)
GOLD_COIN_TEXT_POS = (85, 130)
SILVER_COIN_IMAGE_POS = (47, 170)
SILVER_COIN_TEXT_POS = (87, 180)

# Title settings
TITLE_CENTER_POS = (SCREEN_WIDTH / 2, 100)
TITLE_COLOR = "#402F1D"
MENU_BOX_HEIGHT = 300
MENU_BOX_WIDTH = 300
MENU_BOX_CENTER_POS = (SCREEN_WIDTH / 2, 350)
MENU_OPTION_START_HEIGHT = 200
MENU_OPTION_HEIGHT_DELTA = 50

# Projectile settings
SWORD_VELOCITY = 10