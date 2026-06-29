import pygame


DEFAULT_COLOR = "gray"

def group_drones_by_zone(history):
    grouped_history = []
    for turn in history:
        zone_dict = {}
        for drone_id, zone in turn.items():
            if zone not in zone_dict:
                zone_dict[zone] = []
            zone_dict[zone].append(drone_id)
        grouped_history.append(zone_dict)
    return grouped_history

def run_visualization(history, zones):
    turn = group_drones_by_zone(history)
    # print("grouped_history from visualizer: ", turn)
    pygame.init()

    WIDTH = 1020
    HEIGHT = 920

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    caption = pygame.display.set_caption("Flyin")

    # action
    screen.fill((30,30,30))
    # update it
    pygame.display.update()

    turn = 0

    MAX_X = max(zone.x for zone in zones.values())
    MAX_Y = max(zone.y for zone in zones.values())
    MARGIN = 80
    scale_x = (WIDTH - 2 * MARGIN) / max(MAX_X, 1)
    scale_y = (HEIGHT - 2 * MARGIN) / max(MAX_Y, 1)
    font = pygame.font.Font(None, 24)
    running = True
    RADIUS = 20
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if turn > 0:
                        turn -= 1
                if event.key == pygame.K_RIGHT:
                    turn += 1

        for zone in zones.values():
            px = int(zone.x * scale_x) + MARGIN
            py = int(zone.y * scale_y) + MARGIN

            pygame.draw.circle(screen, (0,0,0), (px, py), RADIUS + 3)
            try:
                pygame.draw.circle(screen, zone.color, (px, py), RADIUS)
            except:
                pygame.draw.circle(screen, DEFAULT_COLOR, (px, py), RADIUS)

            text = font.render(zone.id, True, (255, 255, 255))
            rect = text.get_rect()
            rect.midbottom = (px, py + RADIUS + 5)
            screen.blit(text, rect)

            pygame.display.update()
        
    pygame.quit()
