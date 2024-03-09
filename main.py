import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (255, 0, 0)  # Swapped with RED
RED = (0, 0, 255)   # Swapped with BLUE

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, color):
        super().__init__()
        self.image = pygame.Surface((50, 100))  # Taller rectangle
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = HEIGHT - self.rect.height  # Adjust the starting position
        self.speed = 5
        self.jump_power = 30
        self.is_jumping = False
        self.gravity = 2
        self.jump_velocity = 0
        self.health = 100
        self.stamina = 100
        self.kick_damage = 15
        self.punch_damage = 10
        self.kick_cooldown = 60  # Cooldown in frames between kicks
        self.kick_timer = 0  # Timer to track the cooldown
        self.punch_cooldown = 30  # Cooldown in frames between punches
        self.punch_timer = 0  # Timer to track the cooldown


    def update(self):
        keys = pygame.key.get_pressed()

        # Jumping logic
        if keys[pygame.K_SPACE] and not self.is_jumping and self.stamina > 0:
            self.is_jumping = True
            self.jump_velocity = self.jump_power  # Set jump velocity to jump power
            self.stamina -= 10  # Reduce stamina when jumping

        if self.is_jumping:
            self.rect.y -= self.jump_velocity
            self.jump_velocity -= self.gravity

            if self.rect.y >= HEIGHT - self.rect.height:
                self.is_jumping = False
                self.rect.y = HEIGHT - self.rect.height
                self.jump_velocity = 0

        # Horizontal movement
        if keys[pygame.K_a]:
            self.rect.x -= min(self.speed, self.speed * (self.stamina / 100))  # Reduce speed when stamina is low
        if keys[pygame.K_d]:
            self.rect.x += min(self.speed, self.speed * (self.stamina / 100))  # Reduce speed when stamina is low

        # Regenerate stamina over time
        if not keys[pygame.K_a] and not keys[pygame.K_d] and self.stamina < 100:
            self.stamina += 0.5

        # Collision check with NPC (if not jumping)
        if not self.is_jumping:
            collision_list = pygame.sprite.spritecollide(self, npc_group, False)
            for npc in collision_list:
                # Deal punch damage to the NPC
                npc.take_damage(self.punch_damage)

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and self.punch_timer == 0:  # Left mouse button
            self.punch()
            self.punch_timer = self.punch_cooldown

        if self.punch_timer > 0:
            self.punch_timer -= 1

    def kick(self):
        # Check for collision with NPC
        collision_list = pygame.sprite.spritecollide(self, npc_group, False)
        for npc in collision_list:
            # Deal kick damage to the NPC
            npc.take_damage(self.kick_damage)

    def punch(self):
        # Check for collision with NPC
        collision_list = pygame.sprite.spritecollide(self, npc_group, False)
        for npc in collision_list:
            # Deal punch damage to the NPC
            npc.take_damage(self.punch_damage)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()  # Remove the player when health is zero or negative

# NPC class
class NPC(pygame.sprite.Sprite):
    def __init__(self, x, color):
        super().__init__()
        self.image = pygame.Surface((50, 100))  # Taller rectangle
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = HEIGHT - self.rect.height  # Adjust the starting position
        self.speed = 1
        self.health = 100
        self.attack_damage = 10
        self.retreat_distance = 150  # Distance at which NPC will consider retreating
        self.attack_range = 60  # Distance at which NPC will consider attacking
        self.stand_still_chance = 0.02  # Chance of standing still
        self.attack_cooldown = 60  # Cooldown in frames between attacks
        self.attack_timer = 0  # Timer to track the cooldown


    def update(self):
        # Simple NPC decision-making logic
        player_center = player.rect.x + player.rect.width / 2
        npc_center = self.rect.x + self.rect.width / 2

        # Decide whether to attack, retreat, or stand still
        decision = random.uniform(0, 1)
        if decision < self.stand_still_chance:
            # Stand still
            pass
        elif abs(player_center - npc_center) < self.attack_range and self.attack_timer == 0:
            # Attack the player if close enough and not on cooldown
            if player_center < npc_center:
                self.rect.x -= self.speed
            elif player_center > npc_center:
                self.rect.x += self.speed
            player.take_damage(self.attack_damage)  # Reduce damage for a more balanced game
            self.attack_timer = self.attack_cooldown
        elif abs(player_center - npc_center) < self.retreat_distance:
            # Retreat from the player, avoiding the game boundaries
            if self.rect.x - self.speed > 0 and player_center < npc_center:
                self.rect.x -= self.speed
            elif self.rect.x + self.rect.width + self.speed < WIDTH and player_center > npc_center:
                self.rect.x += self.speed

        if self.attack_timer > 0:
            self.attack_timer -= 1
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()  # Remove the NPC when health is zero or negative


# Initialize game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Street Fighter")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
npc_group = pygame.sprite.Group()

# Create the player and NPC objects
player = Player(50, RED)
npc = NPC(WIDTH - 100, BLUE)

# Add objects to groups
all_sprites.add(player, npc)
player_group.add(player)
npc_group.add(npc)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    screen.fill((0, 0, 0))

    # Draw background, characters, and other elements
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - 50, WIDTH, 50))  # Ground
    all_sprites.draw(screen)

    # Display health and stamina bars
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, player.health * 2, 20))  # Player health bar
    pygame.draw.rect(screen, (0, 255, 0), (10, 40, player.stamina * 2, 20))  # Player stamina bar
    pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 210, 10, npc.health * 2, 20))  # NPC health bar

    pygame.display.flip()
    clock.tick(FPS)

# Quit the game
pygame.quit()
sys.exit()
