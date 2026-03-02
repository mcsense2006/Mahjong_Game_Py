import pygame
import sys
import os
import random
import subprocess
import math
pygame.init()
pygame.mixer.init()

#Taille fenetre
Largeur = 1000
Hauteur = 800

#Texte
affichageFont = 'times new roman'
affichageSize = 30
gameOnType = pygame.font.SysFont(affichageFont, affichageSize+10)

clock = pygame.time.Clock()

#Création de la fenêtre de jeu
fenetre = pygame.display.set_mode((Largeur, Hauteur))
pygame.display.set_caption("Mahjong")

input_font = pygame.font.SysFont(affichageFont, 32)
four_player_box = pygame.Rect((Largeur // 2)-100,200,200,40)
three_player_box = pygame.Rect((Largeur // 2)-100,300,200,40)

while True:
    fenetre.fill((60, 120, 100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    #Position de la souris
    mouse_pos = pygame.mouse.get_pos()

    #Remplir en gris si la souris est dans le rect
    if four_player_box.collidepoint(mouse_pos):
        pygame.draw.rect(fenetre, (150, 150, 150), four_player_box)
    if three_player_box.collidepoint(mouse_pos):
        pygame.draw.rect(fenetre, (150, 150, 150), three_player_box)

    #Chois du mode de jeu
    title = gameOnType.render("Mode de jeu", True, (0, 0, 0))
    fenetre.blit(title, (Largeur // 2 - title.get_width() // 2, 100))
    fenetre.blit(input_font.render('4 Joueurs', True, (255, 255, 255)), (Largeur // 2 - input_font.size('4 Joueurs')[0] // 2, 200))
    fenetre.blit(input_font.render('3 Joueurs', True, (255, 255, 255)), (Largeur // 2 - input_font.size('3 Joueurs')[0] // 2, 300))

    pygame.draw.rect(fenetre, (0,0,0), four_player_box, 2)
    pygame.draw.rect(fenetre, (0,0,0), three_player_box, 2)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = event.pos

        if four_player_box.collidepoint(mouse_pos):
            #Lancer le jeu 4 joueurs
            subprocess.Popen([sys.executable, "four_player_game.py"])
            pygame.quit()
            sys.exit()

        if three_player_box.collidepoint(mouse_pos):
            #Lancer le jeu 3 joueurs
            subprocess.Popen([sys.executable, "three_player_game.py"])
            pygame.quit()
            sys.exit()
            
    pygame.display.flip()
    clock.tick(60)