import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Aim Trainer")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)

# Fonts
font = pygame.font.SysFont('Comic Sans MS', 35)
title_font = pygame.font.SysFont('Comic Sans MS', 75)
game_over_font = pygame.font.SysFont('Comic Sans MS', 75)

# FPS and clock
FPS = 60
clock = pygame.time.Clock()

# Target properties
target_radius = 30  # Large targets
medium_target_radius = 20  # Medium targets
small_target_radius = 15  # Small targets
num_targets = 5
small_target_chance = 0.2
medium_target_chance = 0.4
target_speed_min = 2
target_speed_max = 5

# Effects list for destroyed targets
effects = []

# Score and lives
score = 0
lives = 10

# Target class
class Target:
    def __init__(self, x, y, color, radius, points, moving=False):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.points = points
        self.hit = False
        self.moving = moving
        self.dx = random.uniform(-target_speed_max, target_speed_max) if moving else 0
        self.dy = random.uniform(-target_speed_max, target_speed_max) if moving else 0

    def draw(self):
        if not self.hit:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self):
        if self.moving:
            self.x += self.dx
            self.y += self.dy

            # Bounce off walls
            if self.x - self.radius < 0 or self.x + self.radius > width:
                self.dx = -self.dx
            if self.y - self.radius < 0 or self.y + self.radius > height:
                self.dy = -self.dy

    def check_collision(self, mouse_pos):
        distance = math.sqrt((self.x - mouse_pos[0]) ** 2 + (self.y - mouse_pos[1]) ** 2)
        return distance <= self.radius

# Add visual effects for destroyed targets
def add_effect(x, y):
    effects.append({"x": x, "y": y, "radius": target_radius, "alpha": 255})

# Update effects
def update_effects():
    for effect in effects[:]:
        effect["radius"] += 5  # Expand the effect
        effect["alpha"] -= 15  # Fade out
        if effect["alpha"] <= 0:
            effects.remove(effect)
        else:
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.circle(
                surface, 
                (255, 255, 255, effect["alpha"]), 
                (effect["x"], effect["y"]), 
                effect["radius"]
            )
            screen.blit(surface, (0, 0))

# Function to display the score
def display_score(score, lives):
    score_text = font.render(f"Score: {score}", True, white)
    lives_text = font.render(f"Lives: {lives}", True, white)
    screen.blit(score_text, [10, 10])
    screen.blit(lives_text, [10, 50])

# Game Over screen
def game_over_screen():
    while True:
        screen.fill(black)
        game_over_text = game_over_font.render("GAME OVER", True, red)
        reason_text = font.render("You ran out of lives", True, white)
        retry_text = font.render("Press R to Retry or E to Exit", True, white)
        screen.blit(game_over_text, [width // 2 - game_over_text.get_width() // 2, height // 2 - 100])
        screen.blit(reason_text, [width // 2 - reason_text.get_width() // 2, height // 2 - 20])
        screen.blit(retry_text, [width // 2 - retry_text.get_width() // 2, height // 2 + 40])
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Retry
                    return "retry"
                if event.key == pygame.K_e:  # Exit
                    pygame.quit()
                    return None

# Starting screen
def starting_screen():
    while True:
        screen.fill(black)
        title_text = title_font.render("Aim Trainer", True, white)
        static_text = font.render("Press S for Static Mode", True, white)
        moving_text = font.render("Press M for Moving Mode", True, white)
        screen.blit(title_text, [width // 2 - title_text.get_width() // 2, height // 2 - 100])
        screen.blit(static_text, [width // 2 - static_text.get_width() // 2, height // 2])
        screen.blit(moving_text, [width // 2 - moving_text.get_width() // 2, height // 2 + 50])
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return False  # Static mode
                if event.key == pygame.K_m:
                    return True  # Moving mode

# Main game loop
def game_loop(moving_mode):
    global score, lives
    game_running = True

    while game_running:
        # Reset score and lives
        score = 0
        lives = 10

        # Generate targets
        targets = [
            Target(
                random.randint(target_radius, width - target_radius),
                random.randint(target_radius, height - target_radius),
                random.choice([red, green, blue, yellow]),
                target_radius,
                1,
                moving_mode,
            )
            for _ in range(num_targets)
        ]

        running = True
        while running:
            screen.fill(black)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for target in targets:
                        if target.check_collision(mouse_pos) and not target.hit:
                            target.hit = True
                            score += target.points
                            add_effect(target.x, target.y)
                            break  # Stop checking after the first hit target

                    else:  # If no target was hit
                        lives -= 1
                        if lives <= 0:
                            retry_choice = game_over_screen()
                            if retry_choice == "retry":
                                return  # Go back to starting screen
                            else:
                                game_running = False
                                running = False

            # Move targets if in moving mode
            for target in targets:
                target.move()

            # Draw and update targets
            for target in targets:
                target.draw()

            # Remove hit targets and spawn new ones
            targets = [target for target in targets if not target.hit]
            while len(targets) < num_targets:
                chance = random.random()
                if chance < small_target_chance:
                    targets.append(
                        Target(
                            random.randint(small_target_radius, width - small_target_radius),
                            random.randint(small_target_radius, height - small_target_radius),
                            random.choice([red, green, blue, yellow]),
                            small_target_radius,
                            3,
                            moving_mode,
                        )
                    )
                elif chance < small_target_chance + medium_target_chance:
                    targets.append(
                        Target(
                            random.randint(medium_target_radius, width - medium_target_radius),
                            random.randint(medium_target_radius, height - medium_target_radius),
                            random.choice([red, green, blue, yellow]),
                            medium_target_radius,
                            2,
                            moving_mode,
                        )
                    )
                else:
                    targets.append(
                        Target(
                            random.randint(target_radius, width - target_radius),
                            random.randint(target_radius, height - target_radius),
                            random.choice([red, green, blue, yellow]),
                            target_radius,
                            1,
                            moving_mode,
                        )
                    )

            # Update and draw effects
            update_effects()

            # Display score and lives
            display_score(score, lives)

            # Update the display
            pygame.display.update()
            clock.tick(FPS)

    pygame.quit()

# Run the game
while True:
    mode = starting_screen()
    if mode is None:  # Exit the game
        break
    game_loop(mode)
