from pickle import FALSE
import pygame
import sys
import random
import os

# Initialize PyGame
pygame.init()

# Set up the game window
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Shooter Game")

# Set the frame rate
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Fonts
font = pygame.font.SysFont("Arial", 30)
large_font = pygame.font.SysFont("Arial", 60)

# Player settings
player_width = 120
player_height = 140
player_speed = 14
player_hp = 1  # Player health

# Bullet settings
bullet_width = 40
bullet_height = 80
bullet_speed = 20
bullets = []

# Enemy settings
enemy_width = 140
enemy_height = 140
enemy_speed = 2
enemies = []
enemy_bullets = []
enemy_bullet_width = 40
enemy_bullet_height = 80
enemy_bullet_speed = 15
enemy_min_fire_rate = 1000
enemy_max_fire_rate = 4000

# Enemy spawn
enemy_timer = 0
enemy_spawn_time = 2000

# Score settings
score = 0

# Load player, enemy, and bullet sprites
player_sprite = pygame.image.load('images/player_sprite.png')
enemy_sprite = pygame.image.load('images/enemy_sprite.png')
bullet_sprite = pygame.image.load('images/bullet_sprite.png')
enemy_bullet_sprite = pygame.image.load('images/enemy_bullet_sprite.png')

# Load the background image (you can replace 'images/background.png' with your image)
background_image = pygame.image.load('images/background.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))  # Resize it to fit the screen

# Resize sprites
player_sprite = pygame.transform.scale(player_sprite, (player_width, player_height))
enemy_sprite = pygame.transform.scale(enemy_sprite, (enemy_width, enemy_height))
bullet_sprite = pygame.transform.scale(bullet_sprite, (bullet_width, bullet_height))
enemy_bullet_sprite = pygame.transform.scale(enemy_bullet_sprite, (enemy_bullet_width, enemy_bullet_height))


# Collision detection function
def check_collision(rect1, rect2):
    return pygame.Rect(rect1).colliderect(pygame.Rect(rect2))

# Main game
def main_game():
    global player_hp, score, enemies, bullets, enemy_bullets, enemy_timer

    player_x = screen_width // 2 - player_width // 2
    player_y = screen_height - player_height - 10

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet_x = player_x + player_width // 2 - bullet_width // 2
                    bullet_y = player_y
                    bullets.append([bullet_x, bullet_y])

        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed

        # Update bullet positions
        for bullet in bullets:
            bullet[1] -= bullet_speed
        bullets = [bullet for bullet in bullets if bullet[1] > 0]

        # Update enemy positions and spawn new ones
        current_time = pygame.time.get_ticks()
        if current_time - enemy_timer > enemy_spawn_time:
            enemy_x = random.randint(0, screen_width - enemy_width)
            enemy_y = -enemy_height
            enemies.append({
                "x": enemy_x,
                "y": enemy_y,
                "hp": 1,
                "last_shot": current_time,
                "fire_rate": random.randint(enemy_min_fire_rate, enemy_max_fire_rate)
            })
            enemy_timer = current_time

        for enemy in enemies:
            enemy["y"] += enemy_speed

            # Enemy shooting
            if current_time - enemy["last_shot"] > enemy["fire_rate"]:
                enemy_bullet_x = enemy["x"] + enemy_width // 2 - enemy_bullet_width // 2
                enemy_bullet_y = enemy["y"] + enemy_height
                enemy_bullets.append([enemy_bullet_x, enemy_bullet_y])
                enemy["last_shot"] = current_time
                enemy["fire_rate"] = random.randint(enemy_min_fire_rate, enemy_max_fire_rate)

        # Update enemy bullets
        for enemy_bullet in enemy_bullets:
            enemy_bullet[1] += enemy_bullet_speed
        enemy_bullets = [bullet for bullet in enemy_bullets if bullet[1] < screen_height]

        # Check collisions with player bullets
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if check_collision((bullet[0], bullet[1], bullet_width, bullet_height),
                                   (enemy["x"], enemy["y"], enemy_width, enemy_height)):
                    bullets.remove(bullet)
                    enemy["hp"] -= 1
                    if enemy["hp"] <= 0:
                        enemies.remove(enemy)
                        score += 10
                    break

        # Check collisions with player
        for enemy_bullet in enemy_bullets[:]:
            if check_collision((enemy_bullet[0], enemy_bullet[1], enemy_bullet_width, enemy_bullet_height),
                               (player_x, player_y, player_width, player_height)):
                enemy_bullets.remove(enemy_bullet)
                player_hp -= 1
                if player_hp <= 0:
                    os.system('python3 end_menu.py')
                    quit()
                    break

        # Remove enemies that are off the screen
        enemies = [enemy for enemy in enemies if enemy["y"] < screen_height]

        # Draw background image
        screen.blit(background_image, (0, 0))

        # Draw the player
        screen.blit(player_sprite, (player_x, player_y))

        # Draw the bullets
        for bullet in bullets:
            screen.blit(bullet_sprite, (bullet[0], bullet[1]))

        # Draw the enemies
        for enemy in enemies:
            screen.blit(enemy_sprite, (enemy["x"], enemy["y"]))

        # Draw the enemy bullets
        for enemy_bullet in enemy_bullets:
            screen.blit(enemy_bullet_sprite, (enemy_bullet[0], enemy_bullet[1]))

        # Display the score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Display player HP
        hp_text = font.render(f"HP: {player_hp}", True, RED)
        screen.blit(hp_text, (10, 50))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)


# Start the game
main_game()
