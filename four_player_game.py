import pygame
import sys
import os
import random
pygame.init()
pygame.mixer.init()

#Taille fenêtre
Largeur = 1500
Hauteur = 1000
#Texte
affichageFont = 'times new roman'
affichageSize = 15
gameOnType = pygame.font.SysFont(affichageFont, affichageSize + 10)
actionFont = pygame.font.SysFont(affichageFont, 20)

clock = pygame.time.Clock()

fenetre = pygame.display.set_mode((Largeur, Hauteur))
pygame.display.set_caption("Mahjong 4 Joueurs")

Player_start = random.randint(1, 4)

# pool tuiles
tiles_pool = []
for suit in ["m", "p", "s"]:
    for value in range(1, 10):
        for _ in range(4):
            tiles_pool.append(f"{value}{suit}")
for value in range(1, 8):
    for _ in range(4):
        tiles_pool.append(f"{value}z")
random.shuffle(tiles_pool)

tile_to_path = {}
for value in range(1, 10):
    tile_to_path[f"{value}m"] = os.path.join("Tiles", "man", f"Tile-{value}m.png")
    tile_to_path[f"{value}p"] = os.path.join("Tiles", "pin", f"Tile-{value}p.png")
    tile_to_path[f"{value}s"] = os.path.join("Tiles", "sou", f"Tile-{value}s.png")
for value in range(1, 8):
    tile_to_path[f"{value}z"] = os.path.join("Tiles", "honor", f"Tile-{value}z.png")

#Images
tile_unknown_horizontal = pygame.image.load(os.path.join("Tiles", "Tile-unknown.png")).convert_alpha()
tile_unknown_vertical = pygame.transform.rotate(tile_unknown_horizontal, 90)
tile_width_h = tile_unknown_horizontal.get_width()
tile_height_h = tile_unknown_horizontal.get_height()
tile_width_v = tile_unknown_vertical.get_height()
tile_height_v = tile_unknown_vertical.get_width()

#Murs
tiles_per_side = 17
rows_per_side = 2
spacing = 2

down_slots = []
player_1_start_x = (Largeur - tiles_per_side * tile_width_h - (tiles_per_side - 1) * spacing)//2
player_1_start_y = Hauteur - 210
for row in range(rows_per_side):
    for col in range(tiles_per_side):
        x = player_1_start_x + col * (tile_width_h + spacing)
        y = player_1_start_y + row * (tile_height_h + spacing)
        down_slots.append({"rect": pygame.Rect(x, y, tile_width_h, tile_height_h), "has_tile": True, "revealed": False, "tile_code": None})

right_slots = []
player_2_start_y = (Hauteur - tiles_per_side * tile_height_v - (tiles_per_side - 1) * spacing)//1.1
player_2_start_x = Largeur - 320
for row in range(rows_per_side):
    for col in range(tiles_per_side):
        x = player_2_start_x + row * (tile_width_v + spacing)
        y = player_2_start_y + col * (tile_height_v + spacing)//1.5
        right_slots.append({"rect": pygame.Rect(x, y, tile_width_v, tile_height_v), "has_tile": True, "revealed": False, "tile_code": None})

up_slots = []
player_3_start_x = player_1_start_x
player_3_start_y = 150
for row in range(rows_per_side):
    for col in range(tiles_per_side):
        x = player_3_start_x + col * (tile_width_h + spacing)
        y = player_3_start_y + row * (tile_height_h + spacing)
        up_slots.append({"rect": pygame.Rect(x, y, tile_width_h, tile_height_h), "has_tile": True, "revealed": False, "tile_code": None})

left_slots = []
player_4_start_y = player_2_start_y
player_4_start_x = 250
for row in range(rows_per_side):
    for col in range(tiles_per_side):
        x = player_4_start_x + row * (tile_width_v + spacing)
        y = player_4_start_y + col * (tile_height_v + spacing)//1.5
        left_slots.append({"rect": pygame.Rect(x, y, tile_width_v, tile_height_v), "has_tile": True, "revealed": False, "tile_code": None})

all_wall_slots = down_slots + up_slots + left_slots + right_slots

# Main et discard pour tous les joueurs
hand1_rect = pygame.Rect(0, Hauteur - 80, Largeur, tile_height_h + 20)
hand1_tiles = []

hand2_rect = pygame.Rect(Largeur - 200, 150, tile_height_v + 20, Hauteur-275)
hand2_tiles = []

hand3_rect = pygame.Rect(0, 50, Largeur, tile_height_h + 20)
hand3_tiles = []

hand4_rect = pygame.Rect(150, 150, tile_height_v + 20, Hauteur-275)
hand4_tiles = []

discard_rect = pygame.Rect(Largeur//2 - 100, Hauteur//2 - 50, 200, 100)
discard_tiles = []

#Boîte d'action
action_box_active = False
action_tile_slot = None
action_box_rect = pygame.Rect(Largeur//2 - 150, Hauteur//2 - 75, 300, 150)

def update_hand_positions(hand_tiles, start_x, start_y, is_horizontal=True, tile_width=tile_width_h, tile_height=tile_height_h):
    for i in range(len(hand_tiles)):
        img, _, code, revealed = hand_tiles[i]
        if is_horizontal:
            hand_x = start_x + i * (tile_width + 5)
            hand_y = start_y
        else:
            hand_x = start_x
            hand_y = start_y + i * (tile_height + 5)
        rect = pygame.Rect(hand_x, hand_y, tile_width, tile_height)
        hand_tiles[i] = (img, rect, code, revealed)

def draw_tile_to_hand(hand_tiles, tiles_pool, start_x, start_y, is_horizontal=True):
    if not tiles_pool: 
        return False
    tile_code = random.choice(tiles_pool)
    tiles_pool.remove(tile_code)
    img = pygame.image.load(tile_to_path[tile_code]).convert_alpha()
    if not is_horizontal:
        img = pygame.transform.rotate(img, 90)
    hand_tiles.append((img, None, tile_code, False))
    update_hand_positions(hand_tiles, start_x, start_y, is_horizontal)
    return True

def deal_initial_hands():
    global tiles_pool, hand1_tiles, hand2_tiles, hand3_tiles, hand4_tiles
    
    # Déterminer l'ordre clockwise à partir du mur Est selon Player_start
    wall_order = []
    if Player_start == 1:
        wall_order = down_slots + right_slots + up_slots + left_slots
    elif Player_start == 2:
        wall_order = right_slots + up_slots + left_slots + down_slots
    elif Player_start == 3:
        wall_order = up_slots + left_slots + down_slots + right_slots
    else:
        wall_order = left_slots + down_slots + right_slots + up_slots
    
    # Assigner les 52 premières tuiles du mur aux joueurs (13 par joueur)
    wall_idx = 0
    for _ in range(13):
        # Joueur 1 (bas)
        if wall_idx < len(wall_order):
            slot = wall_order[wall_idx]
            tile_code = tiles_pool.pop(0)  # Prendre du pool ET marquer le slot comme utilisé
            slot["tile_code"] = tile_code
            slot["has_tile"] = False  # Retirer du mur
            img1 = pygame.image.load(tile_to_path[tile_code]).convert_alpha()
            hand1_tiles.append((img1, None, tile_code, False))
            wall_idx += 1
        
        # Joueur 3 (haut) - alternance
        if wall_idx < len(wall_order):
            slot = wall_order[wall_idx]
            tile_code = tiles_pool.pop(0)
            slot["tile_code"] = tile_code
            slot["has_tile"] = False
            img3 = pygame.image.load(tile_to_path[tile_code]).convert_alpha()
            hand3_tiles.append((img3, None, tile_code, False))
            wall_idx += 1
        
        # Joueur 2 (droite)
        if wall_idx < len(wall_order):
            slot = wall_order[wall_idx]
            tile_code = tiles_pool.pop(0)
            slot["tile_code"] = tile_code
            slot["has_tile"] = False
            img2 = pygame.image.load(tile_to_path[tile_code]).convert_alpha()
            img2_rot = pygame.transform.rotate(img2, 90)
            hand2_tiles.append((img2_rot, None, tile_code, False))
            wall_idx += 1
        
        # Joueur 4 (gauche)
        if wall_idx < len(wall_order):
            slot = wall_order[wall_idx]
            tile_code = tiles_pool.pop(0)
            slot["tile_code"] = tile_code
            slot["has_tile"] = False
            img4 = pygame.image.load(tile_to_path[tile_code]).convert_alpha()
            img4_rot = pygame.transform.rotate(img4, 90)
            hand4_tiles.append((img4_rot, None, tile_code, False))
            wall_idx += 1
    
    # Positionner les mains
    update_hand_positions(hand1_tiles, 20, hand1_rect.y + 10, True)
    update_hand_positions(hand2_tiles, hand2_rect.x + 10, hand2_rect.y + 10, False, tile_height_v, tile_width_v)
    update_hand_positions(hand3_tiles, 20, hand3_rect.y + 10, True)
    update_hand_positions(hand4_tiles, hand4_rect.x + 10, hand4_rect.y + 10, False, tile_height_v, tile_width_v)

def reveal_tile_in_slot(slot):
    global tiles_pool
    if not tiles_pool: return
    tile_code = random.choice(tiles_pool)
    tiles_pool.remove(tile_code)
    slot["tile_code"] = tile_code
    slot["revealed"] = True

# Distribuer les mains au démarrage
deal_initial_hands()

# Boucle principale
while True:
    fenetre.fill((60, 120, 100))

    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if action_box_active:
                add_rect = pygame.Rect(action_box_rect.x + 20, action_box_rect.y + 30, 260, 30)
                reveal_rect = pygame.Rect(action_box_rect.x + 20, action_box_rect.y + 70, 260, 30)
                
                if add_rect.collidepoint(mouse_pos):
                    action_tile_slot["has_tile"] = False
                    draw_tile_to_hand(hand1_tiles, tiles_pool, 20, hand1_rect.y + 10, True)
                    action_box_active = False
                    action_tile_slot = None
                elif reveal_rect.collidepoint(mouse_pos):
                    reveal_tile_in_slot(action_tile_slot)
                    action_box_active = False
                    action_tile_slot = None
            else:
                for slot in all_wall_slots:
                    if slot["has_tile"] and slot["rect"].collidepoint(mouse_pos):
                        action_box_active = True
                        action_tile_slot = slot
                        break
                for i, (img, rect, code, revealed) in enumerate(hand1_tiles):
                    if rect and rect.collidepoint(mouse_pos):
                        hand1_tiles.pop(i)
                        update_hand_positions(hand1_tiles, 20, hand1_rect.y + 10, True)
                        discard_x = Largeur//2 - 50 + len(discard_tiles)*15
                        discard_tiles.append((img, pygame.Rect(discard_x, Hauteur//2-25, tile_width_h, tile_height_h)))
                        break

    # Seat winds
    if Player_start == 1:
        title = gameOnType.render("East", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 2 - title.get_width() // 2, 3 * Hauteur // 4 - title.get_height() // 2))
        title = gameOnType.render("South", True, (0, 0, 0))
        fenetre.blit(title, (3 * Largeur // 4 - title.get_width() // 2, Hauteur // 2 - title.get_height() // 2))
        title = gameOnType.render("West", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 2 - title.get_width() // 2, Hauteur // 4 - title.get_height() // 2))
        title = gameOnType.render("North", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 4 - title.get_width() // 2, Hauteur // 2 - title.get_height() // 2))
    elif Player_start == 2:
        title = gameOnType.render("South", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 2 - title.get_width() // 2, 3 * Hauteur // 4 - title.get_height() // 2))
        title = gameOnType.render("West", True, (0, 0, 0))
        fenetre.blit(title, (3 * Largeur // 4 - title.get_width() // 2, Hauteur // 2 - title.get_height() // 2))
        title = gameOnType.render("North", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 2 - title.get_width() // 2, Hauteur // 4 - title.get_height() // 2))
        title = gameOnType.render("East", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 4 - title.get_width() // 2, Hauteur // 2 - title.get_height() // 2))
    elif Player_start == 3:
        title = gameOnType.render("West", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 2 - title.get_width() // 2, 3 * Hauteur // 4 - title.get_height() // 2))
        title = gameOnType.render("North", True, (0, 0, 0))
        fenetre.blit(title, (3 * Largeur // 4 - title.get_width() // 2, Hauteur // 2 - title.get_height() // 2))
        title = gameOnType.render("East", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 2 - title.get_width() // 2, Hauteur // 4 - title.get_height() // 2))
        title = gameOnType.render("South", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 4 - title.get_width() // 2, Hauteur // 2 - title.get_height() // 2))
    else:
        title = gameOnType.render("North", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 2 - title.get_width() // 2, 3 * Hauteur // 4 - title.get_height() // 2))
        title = gameOnType.render("East", True, (0, 0, 0))
        fenetre.blit(title, (3 * Largeur // 4 - title.get_width() // 2, Hauteur // 2 - title.get_height() // 2))
        title = gameOnType.render("South", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 2 - title.get_width() // 2, Hauteur // 4 - title.get_height() // 2))
        title = gameOnType.render("West", True, (0, 0, 0))
        fenetre.blit(title, (Largeur // 4 - title.get_width() // 2, Hauteur // 2 - title.get_height() // 2))

    # main joueur 1 (bas) - visible
    pygame.draw.rect(fenetre, (40, 80, 60), hand1_rect, border_radius=5)
    pygame.draw.rect(fenetre, (0, 0, 0), hand1_rect, 2, border_radius=5)
    for img, rect, code, revealed in hand1_tiles:
        if rect:
            fenetre.blit(img, rect.topleft)

    # main joueur 2 (droite) - cachée
    pygame.draw.rect(fenetre, (40, 80, 60), hand2_rect, border_radius=5)
    pygame.draw.rect(fenetre, (0, 0, 0), hand2_rect, 2, border_radius=5)
    for img, rect, code, revealed in hand2_tiles:
        if rect:
            fenetre.blit(tile_unknown_vertical, rect.topleft)

    # main joueur 3 (haut) - cachée
    pygame.draw.rect(fenetre, (40, 80, 60), hand3_rect, border_radius=5)
    pygame.draw.rect(fenetre, (0, 0, 0), hand3_rect, 2, border_radius=5)
    for img, rect, code, revealed in hand3_tiles:
        if rect:
            fenetre.blit(tile_unknown_horizontal, rect.topleft)

    # main joueur 4 (gauche) - cachée
    pygame.draw.rect(fenetre, (40, 80, 60), hand4_rect, border_radius=5)
    pygame.draw.rect(fenetre, (0, 0, 0), hand4_rect, 2, border_radius=5)
    for img, rect, code, revealed in hand4_tiles:
        if rect:
            fenetre.blit(tile_unknown_vertical, rect.topleft)

    # défausse
    pygame.draw.rect(fenetre, (80, 80, 80), discard_rect, border_radius=5)
    for img, rect in discard_tiles:
        fenetre.blit(img, rect.topleft)

    # 4 murs + reveal (les tuiles distribuées ne s'affichent plus)
    for slot in down_slots:
        if slot["has_tile"]:
            if slot["revealed"] and slot["tile_code"]:
                img = pygame.image.load(tile_to_path[slot["tile_code"]]).convert_alpha()
                fenetre.blit(img, slot["rect"].topleft)
                pygame.draw.rect(fenetre, (255, 255, 0), slot["rect"], 3)
            else:
                fenetre.blit(tile_unknown_horizontal, slot["rect"].topleft)
    
    for slot in up_slots:
        if slot["has_tile"]:
            if slot["revealed"] and slot["tile_code"]:
                img = pygame.image.load(tile_to_path[slot["tile_code"]]).convert_alpha()
                fenetre.blit(img, slot["rect"].topleft)
                pygame.draw.rect(fenetre, (255, 255, 0), slot["rect"], 3)
            else:
                fenetre.blit(tile_unknown_horizontal, slot["rect"].topleft)
    
    for slot in left_slots:
        if slot["has_tile"]:
            if slot["revealed"] and slot["tile_code"]:
                img = pygame.image.load(tile_to_path[slot["tile_code"]]).convert_alpha()
                img_rot = pygame.transform.rotate(img, 90)
                fenetre.blit(img_rot, slot["rect"].topleft)
                pygame.draw.rect(fenetre, (255, 255, 0), slot["rect"], 3)
            else:
                fenetre.blit(tile_unknown_vertical, slot["rect"].topleft)
    
    for slot in right_slots:
        if slot["has_tile"]:
            if slot["revealed"] and slot["tile_code"]:
                img = pygame.image.load(tile_to_path[slot["tile_code"]]).convert_alpha()
                img_rot = pygame.transform.rotate(img, -90)
                fenetre.blit(img_rot, slot["rect"].topleft)
                pygame.draw.rect(fenetre, (255, 255, 0), slot["rect"], 3)
            else:
                fenetre.blit(tile_unknown_vertical, slot["rect"].topleft)

    #Boite d'action
    if action_box_active:
        pygame.draw.rect(fenetre, (100, 100, 100), action_box_rect, border_radius=10)
        pygame.draw.rect(fenetre, (0, 0, 0), action_box_rect, 3, border_radius=10)
        
        text = actionFont.render("What to do with tile?", True, (255, 255, 255))
        fenetre.blit(text, (action_box_rect.x + 10, action_box_rect.y + 5))
        
        add_rect = pygame.Rect(action_box_rect.x + 20, action_box_rect.y + 30, 260, 30)
        pygame.draw.rect(fenetre, (60, 120, 60), add_rect, border_radius=5)
        pygame.draw.rect(fenetre, (0, 0, 0), add_rect, 2, border_radius=5)
        add_text = actionFont.render("Add tile to hand", True, (255, 255, 255))
        fenetre.blit(add_text, (add_rect.x + 10, add_rect.y + 5))
        
        reveal_rect = pygame.Rect(action_box_rect.x + 20, action_box_rect.y + 70, 260, 30)
        pygame.draw.rect(fenetre, (120, 60, 60), reveal_rect, border_radius=5)
        pygame.draw.rect(fenetre, (0, 0, 0), reveal_rect, 2, border_radius=5)
        reveal_text = actionFont.render("Reveal Tile", True, (255, 255, 255))
        fenetre.blit(reveal_text, (reveal_rect.x + 10, reveal_rect.y + 5))

    pygame.display.flip()
    clock.tick(60)
