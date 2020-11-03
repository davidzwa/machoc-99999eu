import logging
from typing import Any

import numpy as np
import pygame
from pygame import Vector2

from base_gui.app_logging import LOGGER
from base_gui.constants import SCREEN_SIZE, NAV_WIDTH, SIM_SIZE, SimType, SimConsts, MENU_CHECKBOXES_MAC, \
    MENU_CHECKBOXES_ROUTING, \
    MENU_CHECKBOX_SIMTYPE_INDEX, MENU_CHECKBOX_MAC_AUTOPLAY
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
        # guiSimMac.add_wavefront()
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

if __name__ == '__main__':
    np.random.seed(1) # Fix seed for debugging purposes

    guiSimMac = construct_simulation(SimType.MAC)
    guiSimRouting = construct_simulation(SimType.ROUTING)

    print("Processing guiSimMac")
    guiSimMac.run_oracle_preprocess(SimConsts.TIME_MAX_STEPS, SimConsts.TIME_STEP)
    print("GuiSimMac done")

    game_quit = False
    guiSim = guiSimMac
    current_sim_type = SimType.MAC
    last_num_nodes = len(guiSim.data_nodes)
    guiSim.timeline.nodes_slider.setValue(last_num_nodes)

    # Auto-play sim variables
    step_difference_millis = 200  # 4 steps per second
    simulation_time = pygame.time.get_ticks()  # integer index < SimConsts.TIME_MAX_STEPS
    timeline_debounce = 75  # minimum ticks between timeline update by LEFT/RIGHT arrows
    last_timeline_change = pygame.time.get_ticks()

    while not game_quit:
        current_time_sim = pygame.time.get_ticks()

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
        # Updating nodes is not smart for now, maybe later.
        # if sliderVal != last_num_nodes:
        #     last_num_nodes = sliderVal

        ### RENDER
        guiSim.screen.fill((245, 245, 245))

        # Calculate timeline slider value based on keys and waiting
        timeVal = guiSim.timeline.time_slider.getValue()
        newTimeValue = timeVal
        if current_time_sim - last_timeline_change > timeline_debounce:
            last_timeline_change = current_time_sim
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                newTimeValue -= 1
            if keys[pygame.K_RIGHT]:
                newTimeValue += 1
            if newTimeValue <= 0:
                timeVal = 0
            elif newTimeValue > SimConsts.TIME_MAX_STEPS - 1:
                timeVal = SimConsts.TIME_MAX_STEPS - 1
            else:
                timeVal = newTimeValue
            guiSim.timeline.time_slider.setValue(timeVal)

        # RENDER - Update text by grabbing guiSim children
        font_surface = guiSim.font.render("Number of nodes: {} ".format(sliderVal), True, pygame.Color("black"))
        guiSim.screen.blit(font_surface, dest=(guiSim.timeline.nodes_slider.x, guiSim.timeline.nodes_slider.y + 20))
        font_surface = guiSim.font.render("Current time: {} sec".format(timeVal), True, pygame.Color("black"))
        guiSim.screen.blit(font_surface, dest=(guiSim.timeline.time_slider.x, guiSim.timeline.time_slider.y + 20))

        ### PROCESS mouse & RENDER WAVE and NODES
        autoplay = guiSim.get_checkbox_value(1, MENU_CHECKBOX_MAC_AUTOPLAY)
        if autoplay:
            if current_sim_type is SimType.MAC and current_time_sim - simulation_time > step_difference_millis:
                simulation_time = current_time_sim
                # mouse_global_pixels = pygame.mouse.get_pos()
                # if mouse_in_frame(mouse_global_pixels, guiSim.sim_rect):
                #     mouse_local_pixels = translate_global_to_local(mouse_global_pixels, guiSim.sim_rect, guiSim.local_origin)
                #     mouse_local_meters = scale_tuple_pix2meter(mouse_local_pixels)
                # guiSimMac.wave.adjust_origin_local(random_node.position_meters)  # Relative positioning
                guiSimMac.show_next_oracle_timeindex()
                print(guiSimMac.show_oracle_states_timeindex)
                guiSimMac.timeline.time_slider.setValue(guiSimMac.show_oracle_states_timeindex)
        else:
            guiSimMac.draw_oraclestate_waves(timeVal)
        guiSim.render_datanodes()

        # RENDER - Nodes and menu
        guiSim.timeline.render()
        guiSim.side_menu.render_nav_backlight()
        guiSim.side_menu.render(events)
        pygame.display.update()
