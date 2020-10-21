import logging
import random
from typing import Any

import pygame
from pygame import Vector2

from base_gui.app_logging import LOGGER
from base_gui.constants import SCREEN_SIZE, NAV_WIDTH, SIM_SIZE, SimType, SimConsts, MENU_CHECKBOXES_MAC, \
    MENU_CHECKBOXES_ROUTING, \
    MENU_CHECKBOX_SIMTYPE_INDEX
from base_gui.simulation.gui_sim_mac import GuiSimMac
from base_gui.simulation.gui_sim_routing import GuiSimRouting


def start_simulation(payload: Any):
    LOGGER.info('start clicked')


def construct_simulation(simulation_type: SimType):
    simulation_window_rect = pygame.Rect(NAV_WIDTH, 0, SIM_SIZE.x, SIM_SIZE.y)
    simulation_origin = Vector2(int(SIM_SIZE.x / 2), int(SIM_SIZE.y / 2))
    if simulation_type is SimType.MAC:
        guiSimMac = GuiSimMac(SCREEN_SIZE, simulation_window_rect, simulation_origin)
        guiSimMac.create_game()
        guiSimMac.add_nav_button(label="Simulate", button_callback=start_simulation)
        guiSimMac.add_nav_button(label="Stop", button_callback=None)
        guiSimMac.add_nav_button(label="Reset", button_callback=None)
        guiSimMac.add_nav_checkboxgroup_specific(MENU_CHECKBOXES_MAC)
        guiSimMac.add_timeline(
            Vector2(simulation_window_rect.midbottom[0] - 150, simulation_window_rect.midbottom[1] - 100),
            Vector2(300, 10)
        )
        guiSimMac.add_wavefront()
        guiSimMac.generate_oracle(SimConsts.NUM_NODES_MAC, SimConsts.DISTANCE_SPREAD_SIGMA_MAC)
        return guiSimMac
    else:
        guiSimRouting = GuiSimRouting(SCREEN_SIZE, simulation_window_rect, simulation_origin)
        guiSimRouting.create_game()
        guiSimRouting.add_nav_button(label="Simulate", button_callback=start_simulation)
        guiSimRouting.add_nav_button(label="Stop", button_callback=None)
        guiSimRouting.add_nav_button(label="Reset", button_callback=None)
        guiSimRouting.add_nav_checkboxgroup_specific(MENU_CHECKBOXES_ROUTING)
        guiSimRouting.add_timeline(
            Vector2(simulation_window_rect.midbottom[0] - 150, simulation_window_rect.midbottom[1] - 100),
            Vector2(300, 10)
        )
        guiSimRouting.generate_nodes_multivariate(SimConsts.NUM_NODES_ROUTING, SimConsts.DISTANCE_SPREAD_SIGMA_ROUTING)
        return guiSimRouting


def mouse_in_frame(mouse_coord, rect):
    return mouse_coord[0] > rect.left \
           and mouse_coord[0] < rect.left + rect.width \
           and mouse_coord[1] > rect.top \
           and mouse_coord[1] < rect.top + rect.height


guiSimMac = construct_simulation(SimType.MAC)
guiSimRouting = construct_simulation(SimType.ROUTING)

pygame.draw.
print("Processing guiSimMac")
guiSimMac.run_oracle_preprocess(SimConsts.TIME_MAX_STEPS, SimConsts.TIME_STEP)
print("GuiSimMac done")

game_quit = False
guiSim = guiSimMac
current_sim_type = SimType.MAC
last_num_nodes = len(guiSim.data_nodes)
while not game_quit:
    ### CAPTURE
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            game_quit = True

    # Switch over sim-type based on checkbox in menu
    if not guiSim.get_checkbox_value(0, MENU_CHECKBOX_SIMTYPE_INDEX) \
            and current_sim_type is SimType.ROUTING:
        guiSim = guiSimMac
        # Synchronize SIM-TYPE state to avoid going back-and-forth (inconsistent main menu between sim instances)
        guiSim.reset_checkbox(0, MENU_CHECKBOX_SIMTYPE_INDEX, False)
        logging.info("Switched to MAC simulator.")
        current_sim_type = SimType.MAC
        sliderVal = guiSim.timeline.nodes_slider.getValue()
        last_num_nodes = sliderVal
    elif guiSim.get_checkbox_value(0, MENU_CHECKBOX_SIMTYPE_INDEX) \
            and current_sim_type is not SimType.ROUTING:
        guiSim = guiSimRouting
        # Synchronize SIM-TYPE state to avoid going back-and-forth (inconsistent main menu between sim instances)
        guiSim.reset_checkbox(0, MENU_CHECKBOX_SIMTYPE_INDEX, True)
        logging.info("Switched to ROUTING simulator.")
        current_sim_type = SimType.ROUTING
        sliderVal = guiSim.timeline.nodes_slider.getValue()
        last_num_nodes = sliderVal

    guiSim.timeline.nodes_slider.listen(events)
    guiSim.timeline.time_slider.listen(events)
    sliderVal = guiSim.timeline.nodes_slider.getValue()
    if sliderVal != last_num_nodes:
        last_num_nodes = sliderVal
        # Too heavy
        # guiSim.generate_nodes_multivariate(last_num_nodes, SimConsts.DISTANCE_SPREAD_SIGMA_MAC)
    timeVal = guiSim.timeline.time_slider.getValue()

    ### RENDER
    guiSim.screen.fill((245, 245, 245))

    # RENDER - Update text by grabbing guiSim children
    font_surface = guiSim.font.render("Number of nodes: {} ".format(sliderVal), True, pygame.Color("black"))
    guiSim.screen.blit(font_surface, dest=(guiSim.timeline.nodes_slider.x, guiSim.timeline.nodes_slider.y + 20))
    font_surface = guiSim.font.render("Current time: {} sec".format(timeVal), True, pygame.Color("black"))
    guiSim.screen.blit(font_surface, dest=(guiSim.timeline.time_slider.x, guiSim.timeline.time_slider.y + 20))

    ### PROCESS mouse & RENDER WAVE and NODES
    if current_sim_type is SimType.MAC:
        # mouse_global_pixels = pygame.mouse.get_pos()
        # if mouse_in_frame(mouse_global_pixels, guiSim.sim_rect):
        #     mouse_local_pixels = translate_global_to_local(mouse_global_pixels, guiSim.sim_rect, guiSim.local_origin)
        #     mouse_local_meters = scale_tuple_pix2meter(mouse_local_pixels)

        random_node = random.choice(guiSimMac.data_nodes)
        guiSimMac.wave.adjust_origin_local(random_node.position_meters)  # Relative positioning
        guiSimMac.render_wave()
    guiSim.render_datanodes()

    # RENDER - Nodes and menu
    guiSim.timeline.render()
    guiSim.side_menu.render_nav_backlight()
    guiSim.side_menu.render(events)
    pygame.display.update()
