import pygame
import sys
import os
import random
import subprocess
import math
pygame.init()
pygame.mixer.init()

#Taille fenetre
Largeur = 800
Hauteur = 600

#Texte
affichageFont = 'times new roman'
affichageSize = 30
gameOnType = pygame.font.SysFont(affichageFont, affichageSize+10)

clock = pygame.time.Clock()

## ---création de la fenêtre de jeu---##
fenetre = pygame.display.set_mode((Largeur, Hauteur))
pygame.display.set_caption("Mahjong 3 Joueurs")

while True:
    fenetre.fill((60, 120, 100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
            
    pygame.display.flip()
    clock.tick(60)