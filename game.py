import pygame
import random
import math

pygame.init()

#setup
WIDTH, HEIGHT = 1000, 700
MIN_WIDTH, MIN_HEIGHT = 800, 550

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), pygame.RESIZABLE
)
pygame.display.set_caption("NEON SURVIVOR")

clock = pygame.time.Clock()
FPS = 60

#colors
BG = (8, 10, 20)
GRID = (19, 24, 40)
WHITE = (240, 245, 255)
CYAN = (0, 240, 255)
RED = (255, 65, 95)
PURPLE = (170, 90, 255)
GREEN = (70, 255, 155)
MUTED = (130, 145, 170)

#fonts
font_small = pygame.font.SysFont("consolas", 16)
font = pygame.font.SysFont("consolas", 22)
font_big = pygame.font.SysFont("consolas", 48, bold=True)
font_title = pygame.font.SysFont("consolas", 64, bold=True)

#states
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

state = MENU

#player specs
PLAYER_RADIUS = 16
PLAYER_SPEED = 300
player = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
health = 100
max_health = 100

#objs
bullets = []
enemies = []
particles = []

score = 0
kills = 0
survival_time = 0
spawn_timer = 0
shoot_timer = 0
damage_flash = 0
best_score = 0


def draw_text(text, font_obj, color, x, y, center=True):
    image = font_obj.render(str(text), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))

    screen.blit(image, rect)


def draw_grid():
    screen.fill(BG)

    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))


def draw_panel(rect, color=(18, 22, 38), border=CYAN):
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, border, rect, 1, border_radius=12)


def create_particles(position, color, amount=8):
    for _ in range(amount):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(50, 200)

        velocity = pygame.Vector2(
            math.cos(angle) * speed,
            math.sin(angle) * speed
        )

        particles.append({
            "pos": pygame.Vector2(position),
            "vel": velocity,
            "life": random.uniform(0.2, 0.5),
            "max_life": 0.5,
            "color": color,
            "size": random.randint(2, 4)
        })


def reset_game():
    global player, health, score, kills
    global survival_time, spawn_timer, shoot_timer
    global bullets, enemies, particles, damage_flash

    player = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
    health = max_health
    score = 0
    kills = 0
    survival_time = 0
    spawn_timer = 0
    shoot_timer = 0
    damage_flash = 0

    bullets = []
    enemies = []
    particles = []


def spawn_enemy():
    side = random.randint(0, 3)

    if side == 0:
        position = pygame.Vector2(random.randint(0, WIDTH), -25)
    elif side == 1:
        position = pygame.Vector2(WIDTH + 25, random.randint(0, HEIGHT))
    elif side == 2:
        position = pygame.Vector2(random.randint(0, WIDTH), HEIGHT + 25)
    else:
        position = pygame.Vector2(-25, random.randint(0, HEIGHT))

    big = random.random() < 0.20

    enemies.append({
        "pos": position,
        "radius": 20 if big else 13,
        "speed": random.uniform(65, 95) if big else random.uniform(90, 135),
        "health": 3 if big else 1,
        "big": big
    })


def draw_player():
    mouse = pygame.Vector2(pygame.mouse.get_pos())
    direction = mouse - player

    if direction.length_squared() > 0:
        direction = direction.normalize()
    else:
        direction = pygame.Vector2(1, 0)

    barrel_end = player + direction * 27

    pygame.draw.line(
        screen, WHITE,
        (int(player.x), int(player.y)),
        (int(barrel_end.x), int(barrel_end.y)),
        5
    )

    pygame.draw.circle(screen, (0, 65, 80), player, 27)
    pygame.draw.circle(screen, CYAN, player, PLAYER_RADIUS)
    pygame.draw.circle(screen, WHITE, player, 6)


def draw_enemy(enemy):
    pos = enemy["pos"]
    radius = enemy["radius"]
    color = PURPLE if enemy["big"] else RED

    pygame.draw.circle(screen, (45, 20, 48), pos, radius + 7)
    pygame.draw.circle(screen, color, pos, radius)
    pygame.draw.circle(screen, WHITE, pos, 4)

    if enemy["big"]:
        pygame.draw.circle(screen, WHITE, pos, radius, 2)


def draw_hud():
    draw_panel(pygame.Rect(20, 20, 200, 85), border=CYAN)
    draw_text("SCORE", font_small, MUTED, 38, 34, False)
    draw_text(f"{score:06d}", font, WHITE, 38, 55, False)

    draw_panel(pygame.Rect(235, 20, 150, 85), border=PURPLE)
    draw_text("ELIMINATED", font_small, MUTED, 250, 34, False)
    draw_text(kills, font, WHITE, 250, 55, False)

    draw_panel(
        pygame.Rect(WIDTH - 190, 20, 170, 85),
        border=GREEN
    )

    draw_text("SURVIVED", font_small, MUTED, WIDTH - 175, 34, False)

    minutes = int(survival_time) // 60
    seconds = int(survival_time) % 60

    draw_text(
        f"{minutes:02d}:{seconds:02d}",
        font, WHITE, WIDTH - 175, 55, False
    )

    bar_x = 20
    bar_y = HEIGHT - 38
    bar_width = 250
    bar_height = 16

    draw_text("HEALTH", font_small, WHITE, bar_x, bar_y - 23, False)

    pygame.draw.rect(
        screen, (45, 48, 65),
        (bar_x, bar_y, bar_width, bar_height),
        border_radius=5
    )

    health_width = int(bar_width * max(0, health) / max_health)

    if health_width > 0:
        health_color = GREEN if health > 35 else RED

        pygame.draw.rect(
            screen, health_color,
            (bar_x, bar_y, health_width, bar_height),
            border_radius=5
        )

    draw_text(
        "WASD: MOVE | MOUSE: AIM | HOLD CLICK: SHOOT | ESC: PAUSE",
        font_small, MUTED, WIDTH // 2, HEIGHT - 18
    )


def draw_button(text, rect, color, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)

    fill = (32, 42, 60) if hovered else (18, 24, 40)
    border = WHITE if hovered else color

    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, border, rect, 2, border_radius=10)

    draw_text(text, font, WHITE, rect.centerx, rect.centery)


def update_particles(dt):
    for particle in particles[:]:
        particle["pos"] += particle["vel"] * dt
        particle["life"] -= dt

        if particle["life"] <= 0:
            particles.remove(particle)
            continue

        ratio = particle["life"] / particle["max_life"]
        radius = max(1, int(particle["size"] * ratio))

        pygame.draw.circle(
            screen,
            particle["color"],
            (int(particle["pos"].x), int(particle["pos"].y)),
            radius
        )


def start_game():
    global state
    reset_game()
    state = PLAYING


#main loop
running = True

while running:
    dt = min(clock.tick(FPS) / 1000, 0.033)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #window size changeable 
        if event.type == pygame.VIDEORESIZE:
            WIDTH = max(MIN_WIDTH, event.w)
            HEIGHT = max(MIN_HEIGHT, event.h)

            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT), pygame.RESIZABLE
            )

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == PLAYING:
                    state = PAUSED
                elif state == PAUSED:
                    state = PLAYING

            if event.key == pygame.K_RETURN:
                if state in (MENU, GAME_OVER):
                    start_game()
                elif state == PAUSED:
                    state = PLAYING

            if event.key == pygame.K_r and state == GAME_OVER:
                start_game()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == MENU:
                start_rect = pygame.Rect(
                    WIDTH // 2 - 110, 410, 220, 55
                )

                if start_rect.collidepoint(event.pos):
                    start_game()

            elif state == PAUSED:
                resume_rect = pygame.Rect(
                    WIDTH // 2 - 110, 365, 220, 55
                )
                menu_rect = pygame.Rect(
                    WIDTH // 2 - 110, 435, 220, 55
                )

                if resume_rect.collidepoint(event.pos):
                    state = PLAYING
                elif menu_rect.collidepoint(event.pos):
                    state = MENU

            elif state == GAME_OVER:
                retry_rect = pygame.Rect(
                    WIDTH // 2 - 110, 440, 220, 55
                )
                menu_rect = pygame.Rect(
                    WIDTH // 2 - 110, 510, 220, 55
                )

                if retry_rect.collidepoint(event.pos):
                    start_game()
                elif menu_rect.collidepoint(event.pos):
                    state = MENU

    draw_grid()

    if state == MENU:
        draw_text("NEON", font_title, CYAN, WIDTH // 2, HEIGHT * 0.26)
        draw_text("SURVIVOR", font_title, WHITE, WIDTH // 2, HEIGHT * 0.35)

        draw_text(
            "SURVIVE THE ARENA. ELIMINATE THE THREAT.",
            font_small, MUTED, WIDTH // 2, HEIGHT * 0.44
        )

        start_rect = pygame.Rect(
            WIDTH // 2 - 110, HEIGHT * 0.59, 220, 55
        )
        draw_button("START GAME", start_rect, CYAN, mouse_pos)

        draw_text(
            "WASD to move | Mouse to aim and shoot",
            font, WHITE, WIDTH // 2, HEIGHT * 0.74
        )

        draw_text(
            "Press ENTER to begin",
            font_small, MUTED, WIDTH // 2, HEIGHT * 0.80
        )

    elif state == PLAYING:
        survival_time += dt
        shoot_timer -= dt
        spawn_timer -= dt
        damage_flash = max(0, damage_flash - dt)

        #char movement
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            movement.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            movement.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            movement.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            movement.x += 1

        if movement.length_squared() > 0:
            movement = movement.normalize()
            player += movement * PLAYER_SPEED * dt

        player.x = max(
            PLAYER_RADIUS,
            min(WIDTH - PLAYER_RADIUS, player.x)
        )
        player.y = max(
            PLAYER_RADIUS,
            min(HEIGHT - PLAYER_RADIUS, player.y)
        )

        #shooting
        if pygame.mouse.get_pressed()[0] and shoot_timer <= 0:
            target = pygame.Vector2(mouse_pos)
            direction = target - player

            if direction.length_squared() > 0:
                direction = direction.normalize()

                bullets.append({
                    "pos": player + direction * 25,
                    "vel": direction * 650,
                    "life": 1.2
                })

                shoot_timer = 0.16

        #enemy spawn
        spawn_delay = max(0.25, 1.0 - survival_time * 0.008)

        if spawn_timer <= 0:
            spawn_enemy()
            spawn_timer = spawn_delay

        #bullet pos update
        for bullet in bullets[:]:
            bullet["pos"] += bullet["vel"] * dt
            bullet["life"] -= dt

            if (
                bullet["life"] <= 0
                or bullet["pos"].x < 0
                or bullet["pos"].x > WIDTH
                or bullet["pos"].y < 0
                or bullet["pos"].y > HEIGHT
            ):
                bullets.remove(bullet)
                continue

            pygame.draw.circle(screen, CYAN, bullet["pos"], 5)
            pygame.draw.circle(screen, WHITE, bullet["pos"], 2)

        #enemy pos update
        for enemy in enemies[:]:
            direction = player - enemy["pos"]

            if direction.length_squared() > 0:
                direction = direction.normalize()

            enemy["pos"] += direction * enemy["speed"] * (
                1 + survival_time * 0.002
            ) * dt

            #collisions
            for bullet in bullets[:]:
                distance = enemy["pos"].distance_to(bullet["pos"])

                if distance < enemy["radius"] + 5:
                    enemy["health"] -= 1
                    create_particles(bullet["pos"], CYAN, 3)
                    bullets.remove(bullet)

                    if enemy["health"] <= 0:
                        score += 30 if enemy["big"] else 10
                        kills += 1

                        create_particles(
                            enemy["pos"],
                            PURPLE if enemy["big"] else RED,
                            12
                        )

                        enemies.remove(enemy)

                    break

            if enemy not in enemies:
                continue

            #player collisions
            distance = player.distance_to(enemy["pos"])

            if distance < PLAYER_RADIUS + enemy["radius"]:
                health -= 30 * dt
                damage_flash = 0.1

            draw_enemy(enemy)

        update_particles(dt)
        draw_player()
        draw_hud()

        if damage_flash > 0:
            overlay = pygame.Surface(
                (WIDTH, HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((255, 0, 30, 35))
            screen.blit(overlay, (0, 0))

        if health <= 0:
            best_score = max(best_score, score)
            state = GAME_OVER

    elif state == PAUSED:
        draw_text(
            "PAUSED", font_title, CYAN,
            WIDTH // 2, HEIGHT * 0.32
        )
        draw_text(
            "Take a breather.", font, MUTED,
            WIDTH // 2, HEIGHT * 0.41
        )

        resume_rect = pygame.Rect(
            WIDTH // 2 - 110, HEIGHT * 0.52, 220, 55
        )
        menu_rect = pygame.Rect(
            WIDTH // 2 - 110, HEIGHT * 0.62, 220, 55
        )

        draw_button("RESUME", resume_rect, CYAN, mouse_pos)
        draw_button("MAIN MENU", menu_rect, PURPLE, mouse_pos)

        draw_text(
            "Press ESC or ENTER to resume",
            font_small, MUTED, WIDTH // 2, HEIGHT * 0.78
        )

    elif state == GAME_OVER:
        draw_text(
            "GAME OVER", font_title, RED,
            WIDTH // 2, HEIGHT * 0.28
        )

        draw_text(
            f"FINAL SCORE: {score}",
            font_big, WHITE, WIDTH // 2, HEIGHT * 0.41
        )

        draw_text(
            f"ENEMIES ELIMINATED: {kills}",
            font, MUTED, WIDTH // 2, HEIGHT * 0.49
        )

        minutes = int(survival_time) // 60
        seconds = int(survival_time) % 60

        draw_text(
            f"SURVIVAL TIME: {minutes:02d}:{seconds:02d}",
            font, MUTED, WIDTH // 2, HEIGHT * 0.54
        )

        draw_text(
            f"BEST SCORE THIS SESSION: {best_score}",
            font_small, GREEN, WIDTH // 2, HEIGHT * 0.59
        )

        retry_rect = pygame.Rect(
            WIDTH // 2 - 110, HEIGHT * 0.65, 220, 55
        )
        menu_rect = pygame.Rect(
            WIDTH // 2 - 110, HEIGHT * 0.76, 220, 55
        )

        draw_button("PLAY AGAIN", retry_rect, CYAN, mouse_pos)
        draw_button("MAIN MENU", menu_rect, PURPLE, mouse_pos)

        draw_text(
            "Press R or ENTER to play again",
            font_small, MUTED, WIDTH // 2, HEIGHT * 0.89
        )

    pygame.display.flip()

pygame.quit()