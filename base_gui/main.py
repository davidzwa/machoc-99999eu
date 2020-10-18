from typing import Any

import numpy as np
import pygame
from pygame import Vector2

from base_gui.app_logging import LOGGER
from base_gui.constants import SCREEN_SIZE, NAV_WIDTH, SIM_SIZE, NUM_NODES
from base_gui.simulation.gui_sim import GuiSim
from base_gui.simulation.wave import Wave
from base_gui.utils.reference_frame import translate_global_to_local, scale_tuple_pix2meter, PIXELS_PER_METER


def menu_item_clicked(payload: Any):
    LOGGER.info('main menu button clicked')


def start_simulation(payload: Any):
    LOGGER.info('start clicked')


def mouse_in_frame(mouse_coord, rect):
    return mouse_coord[0] > rect.left \
           and mouse_coord[0] < rect.left + rect.width \
           and mouse_coord[1] > rect.top \
           and mouse_coord[1] < rect.top + rect.height

simulation_window_rect = pygame.Rect(NAV_WIDTH, 0, SIM_SIZE.x, SIM_SIZE.y)
simulation_origin = Vector2(int(SIM_SIZE.x / 2), int(SIM_SIZE.y / 2))

guiSim = GuiSim(SCREEN_SIZE, simulation_window_rect, simulation_origin)
guiSim.create_game()
guiSim.add_nav_menu()
guiSim.add_nav_button(label="Simulate", button_callback=start_simulation)
guiSim.add_nav_button(label="Stop", button_callback=None)
guiSim.add_nav_button(label="Reset", button_callback=None)

guiSim.generate_nodes_multivariate(NUM_NODES, 20)
wave = Wave(guiSim.screen, simulation_window_rect, simulation_origin, 50,
            PIXELS_PER_METER)  # Static/doesnt scale like this

crashed = False
while not crashed:
    ### CAPTURE
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            crashed = True

    ### PROCESS
    mouse_global_pixels = pygame.mouse.get_pos()
    if mouse_in_frame(mouse_global_pixels, simulation_window_rect):
        mouse_local_pixels = translate_global_to_local(mouse_global_pixels, simulation_window_rect, simulation_origin)
        mouse_local_meters = scale_tuple_pix2meter(mouse_local_pixels)
        wave.adjust_origin_local(mouse_local_meters)  # Relative positioning

    ### RENDER
    guiSim.screen.fill((245, 245, 245))
    wave.render()

    guiSim.render_datanodes()

    guiSim.side_menu.render_nav_backlight()
    guiSim.side_menu.render(events)
    pygame.display.update()
