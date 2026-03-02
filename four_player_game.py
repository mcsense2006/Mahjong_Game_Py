import pygame
import sys
import os
import random

pygame.init()
pygame.mixer.init()

# Config
Largeur, Hauteur = 1500, 1000
gameOnType = pygame.font.SysFont('times new roman', 25)
actionFont = pygame.font.SysFont('times new roman', 20)
clock = pygame.time.Clock()
fenetre = pygame.display.set_mode((Largeur, Hauteur))
pygame.display.set_caption("Mahjong 4 Joueurs")
Player_start = random.randint(1, 4)

# Tiles setup
tiles_pool = [f"{v}{s}" for s in ["m","p","s"] for v in range(1,10) for _ in range(4)] + \
             [f"{v}z" for v in range(1,8) for _ in range(4)]
random.shuffle(tiles_pool)

tile_to_path = {f"{v}{s}": os.path.join("Tiles", {"m":"man", "p":"pin", "s":"sou"}[s], f"Tile-{v}{s}.png") 
                for s in ["m","p","s"] for v in range(1,10)}
tile_to_path.update({f"{v}z": os.path.join("Tiles", "honor", f"Tile-{v}z.png") for v in range(1,8)})

tile_unknown_h = pygame.image.load("Tiles/Tile-unknown.png").convert_alpha()
tile_unknown_v = pygame.transform.rotate(tile_unknown_h, 90)
tile_width_h, tile_height_h = tile_unknown_h.get_size()
tile_width_v, tile_height_v = tile_unknown_v.get_size()

# Wall slots generator
def create_wall_slots(start_x, start_y, tiles_per_side=17, rows=2, spacing=2, is_vertical=False):
    slots = []
    tile_w, tile_h = (tile_width_v, tile_height_v) if is_vertical else (tile_width_h, tile_height_h)
    for row in range(rows):
        for col in range(tiles_per_side):
            x = start_x + (col if not is_vertical else row) * (tile_w + spacing)
            y = start_y + (row if not is_vertical else col) * (tile_h + spacing) // 1.5
            slots.append({"rect": pygame.Rect(x, y, tile_w, tile_h), "has_tile": True, "revealed": False, "tile_code": None})
    return slots

down_slots  = create_wall_slots((Largeur - 17*tile_width_h -16*2)//2, Hauteur-210)
right_slots = create_wall_slots(Largeur-320, (Hauteur-17*tile_height_v-16*2)//1.1, is_vertical=True)
up_slots    = create_wall_slots((Largeur - 17*tile_width_h -16*2)//2, 150)
left_slots  = create_wall_slots(250, (Hauteur-17*tile_height_v-16*2)//1.1, is_vertical=True)
all_wall_slots = down_slots + up_slots + left_slots + right_slots

# Hands setup
hand1_rect = pygame.Rect(0, Hauteur-80, Largeur, tile_height_h+20); hand1_tiles = []
hand2_rect = pygame.Rect(Largeur-200, 150, tile_height_v+20, Hauteur-275); hand2_tiles = []
hand3_rect = pygame.Rect(0, 50, Largeur, tile_height_h+20); hand3_tiles = []
hand4_rect = pygame.Rect(150, 150, tile_height_v+20, Hauteur-275); hand4_tiles = []
discard_rect = pygame.Rect(Largeur//2-100, Hauteur//2-50, 200, 100); discard_tiles = []
action_box_active = action_tile_slot = None; action_box_rect = pygame.Rect(Largeur//2-150, Hauteur//2-75, 300, 150)

def update_hand_positions(hand_tiles, start_x, start_y, horizontal=True):
    w, h = (tile_width_h, tile_height_h) if horizontal else (tile_height_v, tile_width_v)
    for i, (img, _, code, rev) in enumerate(hand_tiles):
        x = start_x + i*(w+5) if horizontal else start_x
        y = start_y if horizontal else start_y + i*(h+5)
        hand_tiles[i] = (img, pygame.Rect(x,y,w,h), code, rev)

def draw_tile_to_hand(hand_tiles, pool, start_x, start_y, horizontal=True):
    if pool:
        code = pool.pop(0)
        img = pygame.image.load(tile_to_path[code]).convert_alpha()
        if not horizontal: img = pygame.transform.rotate(img, 90)
        hand_tiles.append((img, None, code, False))
        update_hand_positions(hand_tiles, start_x, start_y, horizontal)

def reveal_tile_in_slot(slot):
    global tiles_pool
    if tiles_pool:
        code = tiles_pool.pop(0)
        slot["tile_code"] = code
        slot["revealed"] = True

def deal_initial_hands():
    wall_order = {1: (down_slots, right_slots, up_slots, left_slots),
                  2: (right_slots, up_slots, left_slots, down_slots),
                  3: (up_slots, left_slots, down_slots, right_slots),
                  4: (left_slots, down_slots, right_slots, up_slots)}[Player_start]
    
    walls = [s for wall in wall_order for s in wall]
    hands = [hand1_tiles, hand3_tiles, hand2_tiles, hand4_tiles]
    
    for i in range(52):
        slot = walls[i]
        code = tiles_pool.pop(0)
        slot["tile_code"], slot["has_tile"] = code, False
        hand = hands[i%4]
        rot = 90 if i%4 > 1 else 0
        img = pygame.image.load(tile_to_path[code]).convert_alpha()
        if rot: img = pygame.transform.rotate(img, rot)
        hand.append((img, None, code, False))
    
    update_hand_positions(hand1_tiles, 20, hand1_rect.y+10, True)
    update_hand_positions(hand2_tiles, hand2_rect.x+10, hand2_rect.y+10, False)
    update_hand_positions(hand3_tiles, 20, hand3_rect.y+10, True)
    update_hand_positions(hand4_tiles, hand4_rect.x+10, hand4_rect.y+10, False)

def draw_wall_slot(fenetre, slot):
    if not slot["has_tile"]: return
    if slot["revealed"] and slot["tile_code"]:
        img = pygame.image.load(tile_to_path[slot["tile_code"]]).convert_alpha()
        rot = 90 if slot in left_slots else -90 if slot in right_slots else 0
        fenetre.blit(pygame.transform.rotate(img, rot), slot["rect"].topleft)
        pygame.draw.rect(fenetre, (255,255,0), slot["rect"], 3)
    else:
        img = tile_unknown_v if slot in (left_slots+right_slots) else tile_unknown_h
        fenetre.blit(img, slot["rect"].topleft)

def draw_hand(fenetre, hand_tiles, rect, hidden=False):
    pygame.draw.rect(fenetre, (40,80,60), rect, border_radius=5)
    pygame.draw.rect(fenetre, (0,0,0), rect, 2, border_radius=5)
    back = tile_unknown_v if rect in (hand2_rect, hand4_rect) else tile_unknown_h
    for img, r, code, rev in hand_tiles:
        if r: fenetre.blit(back if hidden else img, r.topleft)

def draw_seat_winds():
    winds = {1: ["East","South","West","North"], 2:["South","West","North","East"],
             3:["West","North","East","South"], 4:["North","East","South","West"]}
    pos = [(Largeur//2, 3*Hauteur//4), (3*Largeur//4, Hauteur//2), (Largeur//2, Hauteur//4), (Largeur//4, Hauteur//2)]
    for i, (wind, (x,y)) in enumerate(zip(winds[Player_start], pos)):
        t = gameOnType.render(wind, True, (0,0,0))
        fenetre.blit(t, (x - t.get_width()//2, y - t.get_height()//2))

def draw_action_box(mouse_pos):
    if not action_box_active: return False, False
    pygame.draw.rect(fenetre, (100,100,100), action_box_rect, border_radius=10)
    pygame.draw.rect(fenetre, (0,0,0), action_box_rect, 3, border_radius=10)
    fenetre.blit(actionFont.render("What to do with tile?", True, (255,255,255)), (action_box_rect.x+10, action_box_rect.y+5))
    
    add_r = pygame.Rect(action_box_rect.x+20, action_box_rect.y+30, 260, 30)
    reveal_r = pygame.Rect(action_box_rect.x+20, action_box_rect.y+70, 260, 30)
    for r, color, text in [(add_r, (60,120,60), "Add tile to hand"), (reveal_r, (120,60,60), "Reveal Tile")]:
        pygame.draw.rect(fenetre, color, r, border_radius=5)
        pygame.draw.rect(fenetre, (0,0,0), r, 2, border_radius=5)
        fenetre.blit(actionFont.render(text, True, (255,255,255)), (r.x+10, r.y+5))
    return add_r.collidepoint(mouse_pos), reveal_r.collidepoint(mouse_pos)

# Init game
deal_initial_hands()

# Main loop
while True:
    fenetre.fill((60,120,100))
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if action_box_active:
                add_clicked, reveal_clicked = draw_action_box(mouse_pos)
                if add_clicked: 
                    action_tile_slot["has_tile"] = False
                    draw_tile_to_hand(hand1_tiles, tiles_pool, 20, hand1_rect.y+10, True)
                    action_box_active = action_tile_slot = None
                elif reveal_clicked: 
                    reveal_tile_in_slot(action_tile_slot)
                    action_box_active = action_tile_slot = None
            else:
                for slot in all_wall_slots:
                    if slot["has_tile"] and slot["rect"].collidepoint(mouse_pos):
                        action_box_active = action_tile_slot = slot; break
                for i,(img,r,_,_) in enumerate(hand1_tiles):
                    if r and r.collidepoint(mouse_pos):
                        hand1_tiles.pop(i); update_hand_positions(hand1_tiles, 20, hand1_rect.y+10, True)
                        discard_tiles.append((img, pygame.Rect(Largeur//2-50+len(discard_tiles)*15, Hauteur//2-25, tile_width_h, tile_height_h)))
                        break
    
    draw_seat_winds()
    draw_hand(fenetre, hand1_tiles, hand1_rect)
    draw_hand(fenetre, hand2_tiles, hand2_rect, True)
    draw_hand(fenetre, hand3_tiles, hand3_rect, True)
    draw_hand(fenetre, hand4_tiles, hand4_rect, True)
    
    pygame.draw.rect(fenetre, (80,80,80), discard_rect, border_radius=5)
    for img, r in discard_tiles: fenetre.blit(img, r.topleft)
    
    for slot in all_wall_slots: draw_wall_slot(fenetre, slot)
    draw_action_box(mouse_pos)
    
    pygame.display.flip(); clock.tick(60)