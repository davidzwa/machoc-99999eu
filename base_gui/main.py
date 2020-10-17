from typing import Any

import matplotlib
import numpy as np
import pygame
from pygame import Vector2
from pygame.locals import *

from base_gui.components.sidenav import SideNav
from base_gui.simulation.node import Node
from base_gui.simulation.wave import Wave
from base_gui.utils.reference_frame import translate_global_to_local, scale_tuple_pix2meter, PIXELS_PER_METER

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

fig = plt.figure(figsize=[3, 3])
ax = fig.add_subplot(111)
canvas = agg.FigureCanvasAgg(fig)


def plot(data):
    ax.plot(data)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    return pygame.image.fromstring(raw_data, size, "RGB")


pygame.init()
window = pygame.display.set_mode((800, 600), DOUBLEBUF | RESIZABLE)
screen = pygame.display.get_surface()
size = canvas.get_width_height()
pygame.display.flip()

a = np.array([1, 2, 3])
plot_surface = plot(a)


# screen.blit(plot_surface, (200, 0))


def menu_item_clicked(payload: Any):
    print('main menu button clicked', payload)


def mouse_in_frame(mouse_coord, rect):
    return mouse_coord[0] > rect.left \
           and mouse_coord[0] < rect.left + rect.width \
           and mouse_coord[1] > rect.top \
           and mouse_coord[1] < rect.top + rect.height


nav_rect_bounds = pygame.Rect(0, 0, 200, 800)
local_rect = pygame.Rect(200, 0, 600, 800)
side_menu = SideNav(screen, nav_rect_bounds, callback=menu_item_clicked)
button = side_menu.add_button(label="Simulate")
button2 = side_menu.add_button(label="Stop")
button3 = side_menu.add_button(label="Reset")

wave = Wave(screen, local_rect, (50, 50), 50, PIXELS_PER_METER)  # Static/doesnt scale like this

node_positions = ((2, 2), (2, 3), (3, 4), (2, 6))
sim_nodes = list()
for node_pos in node_positions:
    dot_node = Node(Vector2(node_pos), local_rect, screen, Color("red"))
    sim_nodes.append((dot_node))

crashed = False
while not crashed:
    ### CAPTURE
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            crashed = True

    ### PROCESS
    mouse_global_pixels = pygame.mouse.get_pos()
    if mouse_in_frame(mouse_global_pixels, local_rect):
        mouse_local_pixels = translate_global_to_local(mouse_global_pixels, local_rect)
        mouse_local_meters = scale_tuple_pix2meter(mouse_local_pixels)
        wave.adjust_origin_local(mouse_local_meters)  # Relative positioning

    ### RENDER
    screen.fill((245, 245, 245))
    wave.render()

    for sim_node in sim_nodes:
        sim_node.render()

    side_menu.render_nav_backlight()
    side_menu.render(events)
    # screen.blit(plot_surface, (200, 0))
    pygame.display.update()
