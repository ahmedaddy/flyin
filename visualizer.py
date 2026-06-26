import math

import pygame

from simulation import Simulation
from zone import ZoneType


def _zone_color(zone) -> tuple[int, int, int]:
    if zone.hub_type and zone.hub_type.value == "start_hub":
        return (72, 187, 120)
    if zone.hub_type and zone.hub_type.value == "end_hub":
        return (231, 76, 60)
    if zone.z_type == ZoneType.PRIORITY.value:
        return (155, 89, 182)
    if zone.z_type == ZoneType.RESTRICTED.value:
        return (230, 126, 34)
    if zone.z_type == ZoneType.BLOCKED.value:
        return (44, 62, 80)
    return (52, 152, 219)


def _build_layout(graph, width: int, height: int):
    padding = 80
    xs = [zone.x for zone in graph.zones.values()]
    ys = [zone.y for zone in graph.zones.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(1, max_x - min_x)
    span_y = max(1, max_y - min_y)
    scale_x = (width - padding * 2) / span_x
    scale_y = (height - padding * 2) / span_y
    scale = min(scale_x, scale_y)

    positions = {}
    for zone_id, zone in graph.zones.items():
        x = padding + (zone.x - min_x) * scale
        y = padding + (zone.y - min_y) * scale
        positions[zone_id] = (int(x), int(y))
    return positions


def _drone_position(snapshot, positions):
    start_pos = positions[snapshot.zone]
    if not snapshot.in_transit or not snapshot.transit_destination:
        return start_pos

    end_pos = positions[snapshot.transit_destination]
    return (
        int((start_pos[0] + end_pos[0]) / 2),
        int((start_pos[1] + end_pos[1]) / 2),
    )


def run_visualization(graph, nb_drones, start_hub_id, end_hub_id, speed=1.5):
    frames = list(
        Simulation.collect_frames(graph, nb_drones, start_hub_id, end_hub_id)
    )
    if not frames:
        raise ValueError("No simulation frames available.")

    pygame.init()
    pygame.display.set_caption("Drone Simulation")
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18)
    title_font = pygame.font.SysFont("arial", 26, bold=True)
    drone_font = pygame.font.SysFont("arial", 10, bold=True)
    positions = _build_layout(graph, width, height)

    current_frame = 0
    paused = False
    running = True
    fps = max(1, math.ceil(speed))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_RIGHT:
                    paused = True
                    current_frame = min(current_frame + 1, len(frames) - 1)
                elif event.key == pygame.K_LEFT:
                    paused = True
                    current_frame = max(current_frame - 1, 0)
                elif event.key == pygame.K_r:
                    paused = True
                    current_frame = 0
                elif event.key == pygame.K_e:
                    paused = True
                    current_frame = len(frames) - 1
                elif event.key in (
                    pygame.K_PLUS,
                    pygame.K_EQUALS,
                    pygame.K_KP_PLUS,
                ):
                    fps = min(fps + 1, 60)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    fps = max(fps - 1, 1)

        if not paused and current_frame < len(frames) - 1:
            current_frame += 1

        screen.fill((245, 247, 250))

        for zone_id, links in graph.connections.items():
            start_pos = positions[zone_id]
            for link in links:
                end_pos = positions[link.neighbor]
                pygame.draw.line(
                    screen, (180, 180, 180), start_pos, end_pos, 3
                )

        for zone_id, zone in graph.zones.items():
            position = positions[zone_id]
            color = _zone_color(zone)
            pygame.draw.circle(screen, color, position, 18)
            pygame.draw.circle(screen, (40, 40, 40), position, 18, 2)
            label = font.render(zone_id, True, (25, 25, 25))
            screen.blit(label, (position[0] + 22, position[1] - 10))

        frame = frames[current_frame]
        for index, snapshot in enumerate(frame.drone_snapshots):
            x, y = _drone_position(snapshot, positions)
            hue = (index * 63) % 255
            drone_color = (80 + hue // 4, 50 + hue // 5, 180 - hue // 6)
            pygame.draw.circle(screen, drone_color, (x, y), 8)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 8, 2)
            drone_label = drone_font.render(str(snapshot.id), True, (0, 0, 0))
            label_rect = drone_label.get_rect(center=(x, y))
            screen.blit(drone_label, label_rect)

        title = title_font.render(
            f"Turn {frame.turn} / {len(frames) - 1}", True, (30, 30, 30)
        )
        screen.blit(title, (30, 20))

        status = (
            "Space play/pause | Left/Right step | R reset | E end | "
            "+/- speed | Esc quit"
        )
        status_surface = font.render(status, True, (60, 60, 60))
        screen.blit(status_surface, (30, 55))

        speed_surface = font.render(
            f"Playback speed: {fps} FPS", True, (60, 60, 60)
        )
        screen.blit(speed_surface, (30, 80))

        action_text = (
            " ".join(frame.actions)
            if frame.actions
            else "No moves this turn"
        )
        if len(action_text) > 110:
            action_text = action_text[:107] + "..."
        action_surface = font.render(action_text, True, (60, 60, 60))
        screen.blit(action_surface, (30, height - 40))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
