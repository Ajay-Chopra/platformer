import pygame

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

MAX_POTION_RECT_WIDTH = 152
POTION_RECT_HEIGHT = 10

# GOLD_COIN_IMAGE_POS = (45, 120)
# GOLD_COIN_TEXT_POS = (85, 130)
# SILVER_COIN_IMAGE_POS = (47, 170)
# SILVER_COIN_TEXT_POS = (87, 180)

BLUE_DIAMOND_IMAGE_POS = (300, 70)
BLUE_DIAMOND_TEXT_POS = (330, 70)
GREEN_DIAMOND_IMAGE_POS = (390, 70)
GREEN_DIAMOND_TEXT_POS = (420, 70)
RED_DIAMOND_IMAGE_POS = (480, 70)
RED_DIAMOND_TEXT_POS = (510, 70)
GOLD_COIN_IMAGE_POS = (570, 70)
GOLD_COIN_TEXT_POS = (600, 70)
SILVER_COIN_IMAGE_POS = (660, 70)
SILVER_COIN_TEXT_POS = (690, 70)
SKULL_IMAGE_POS = (730, 55)
SKULL_TEXT_POS = (760, 70)

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

# Enemy data
ENEMY_DATA = {
    "crabs": {
        "gameplay": {
            "damage_given": 20,
            "damage_taken": 20
        },
        "sprite_data": {
            "path": "../graphics/enemy/crabs",
            "animation_speed": 0.15,
            "min_speed": 3,
            "max_speed": 5
        }
    },
    "star": {
        "gameplay": {
            "damage_given": 20,
            "damage_taken": 20
        },
        "sprite_data": {
            "path": "../graphics/enemy/star",
            "animation_speed": 0.15,
            "min_speed": 3,
            "max_speed": 5
        }
    },
    "tooth": {
        "gameplay": {
            "damage_given": 20,
            "damage_taken": 20
        },
        "sprite_data": {
            "path": "../graphics/enemy/tooth",
            "animation_speed": 0.15,
            "min_speed": 3,
            "max_speed": 5
        }
    }
}

# shooter trap data
SHOOTER_TRAP_DATA = {
    "cannon": {
        "gameplay": {
            "damage_given": 50
        },
        "sprite_data": {
            "shoot_frame": 4,
            "path": "../graphics/enemy/cannon",
            "projectile_path": "../graphics/projectiles/cannon/ball.png",
            "projectile_speed": 20,
            "attack_cooldown_min_time": 4000,
            "attack_cooldown_max_time": 6000,
            "projectile_offset": pygame.math.Vector2(0, -90)
        }
    },
    "shell": {
        "gameplay": {
            "damage_given": 50
        },
        "sprite_data": {
            "shoot_frame": 2,
            "path": "../graphics/enemy/cannon",
            "projectile_path": "../graphics/projectiles/pearl/pearl.png",
            "projectile_speed": 20,
            "attack_cooldown_min_time": 4000,
            "attack_cooldown_max_time": 6000,
            "projectile_offset": pygame.math.Vector2(0, -90)
        }
    }
}

# collectable data
COLLECTABLE_ITEM_DATA = {
    "potions": {
        "red": {
            "path": "../graphics/collectables/potions/red",
            "base_increase_amount": 20 
        },
        "green": {
            "path": "../graphics/collectables/potions/green",
            "ui_path": "../graphics/collectables/potions/green/green_potion1.png",
            "image_pos": (50, 170),
            "timer_pos": (70, 180),
            "increase_amount": 20,
            "base_time_amount": 10000
        },
        "blue": {
            "path": "../graphics/collectables/potions/blue",
            "ui_path": "../graphics/collectables/potions/blue/blue_potion1.png",
            "image_pos": (55, 135),
            "timer_pos": (70, 140),
            "increase_amount": 20,
            "base_time_amount": 10000
        }
    },
    "diamonds": {
        "red": {
            "path": "../graphics/collectables/diamonds/red",
            "increase_amount": 20,
            "ui_path": "../graphics/ui/collectable_images/red_diamond1.png"
        },
        "green": {
            "path": "../graphics/collectables/diamonds/green",
            "multiplier": 2,
            "increase_amount": 5000,
            "ui_path": "../graphics/ui/collectable_images/green_diamond1.png"
        },
        "blue": {
            "path": "../graphics/collectables/diamonds/blue",
            "ui_path": "../graphics/ui/collectable_images/blue_diamond1.png",
            "increase_amount": 5000,
            "multiplier": 2
        }
    },
    "coins": {
        "gold": {
            "path": "../graphics/collectables/coins/gold",
            "value": 10
        },
        "silver": {
            "path": "../graphics/collectables/coins/silver",
            "value": 5
        }
    },
    "skull": {
        "path": "../graphics/collectables/skull/skull",
        "ui_path": "../graphics/ui/collectable_images/skull_real1.png"
    }
}










