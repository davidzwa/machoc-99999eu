from typing import Any

import matplotlib
import numpy as np
import pygame
from pygame.locals import *

from base_gui.components.sidenav import SideNav
from base_gui.simulation.wave import Wave

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
screen.blit(plot_surface, (200, 0))


def menu_item_clicked(payload: Any):
    print('main menu button clicked', payload)


nav_rect_bounds = pygame.Rect(0, 0, 200, 800)
sim_rect_bounds = pygame.Rect(300, 100, 400, 400)
side_menu = SideNav(screen, nav_rect_bounds, callback=menu_item_clicked)
button = side_menu.add_button(label="Simulate")
button2 = side_menu.add_button(label="Stop")
button2 = side_menu.add_button(label="Reset")

wave = Wave(screen, sim_rect_bounds) # Static/doesnt scale like this

crashed = False
while not crashed:
    screen.fill((245, 245, 245))
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            crashed = True

    # mouse = pygame.mouse.get_pos()
    # print(mouse)
    side_menu.render(events)
    side_menu.render_nav_backlight()

    # screen.blit(plot_surface, (200, 0))
    wave.render(x=50, y=50)
    # button.listen(events)

    # button.draw()
    pygame.display.update()
