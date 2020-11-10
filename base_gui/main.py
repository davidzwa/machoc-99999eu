from typing import Any

import numpy as np
import pygame
from pygame import Vector2

from base_gui import constants
from base_gui.app_logging import LOGGER
from base_gui.constants import SCREEN_SIZE, NAV_WIDTH, SIM_SIZE, SimType, SimConsts, MENU_CHECKBOXES_MAC, \
    MENU_CHECKBOX_MAC_AUTOPLAY, AUTOPLAY_SPEED_MS, TIMELINE_SCROLL_DEBOUNCE
from base_gui.simulation.gui_sim_mac import GuiSimMac


def run_mac_simulation(guiSim: GuiSimMac, num_nodes):
    print("Generating guiSimMac with constants")
    guiSim.generate_oracle(num_nodes, SimConsts.DISTANCE_SPREAD_SIGMA_MAC)
    print("Scaling pixels/meter to fit nodes in simulation")
    scale_simulation_fit_nodes(guiSim, guiSim.sim_rect.inflate(-100, -200))
    print("Processing guiSimMac")
    guiSim.run_oracle_preprocess(SimConsts.TIME_MAX_STEPS, SimConsts.TIME_STEP)
    return guiSim


# SimType is ignored as this simulator is currently meant for MAC only
def construct_simulation(simulation_type: SimType):
    simulation_window_rect = pygame.Rect(NAV_WIDTH, 0, SIM_SIZE.x, SIM_SIZE.y)
    simulation_origin = Vector2(int(SIM_SIZE.x / 2), int(SIM_SIZE.y / 2))
    guiSimMac = GuiSimMac(SCREEN_SIZE, simulation_window_rect, simulation_origin)
    guiSimMac.create_game()
    guiSimMac.add_nav_button(label="Run simulation", button_callback=run_simulation)
    guiSimMac.add_nav_button(label="Toggle auto-play", button_callback=toggle_autoplay)
    guiSimMac.add_nav_button(label="Reset to start", button_callback=reset_simulation_to_start)
    guiSimMac.add_nav_checkboxgroup_specific(MENU_CHECKBOXES_MAC)
    guiSimMac.add_sliders(
        Vector2(simulation_window_rect.bottomleft[0] + 50, simulation_window_rect.midbottom[1] - 150),
        Vector2(500, 10)
    )
    guiSimMac.generate_legend(Vector2(NAV_WIDTH + 10, 10), 10)
    return run_mac_simulation(guiSimMac, SimConsts.NUM_NODES_MAC)


def run_simulation(payload: Any):
    LOGGER.info('Rerun simulation')
    reset_simulation_to_start(None)
    nodeCount = guiSim.timeline.nodes_slider.getValue()
    return run_mac_simulation(guiSim, nodeCount)


def toggle_autoplay(payload: Any):
    guiSim.toggle_checkbox_value(1, MENU_CHECKBOX_MAC_AUTOPLAY)


def reset_simulation_to_start(payload: Any):
    guiSim.show_oracle_states_timeindex = 0
    guiSim.timeline.time_slider.setValue(0)


def scale_simulation_fit_nodes(guiSim, rect: pygame.Rect):
    print("SCALING - default scale {}".format(constants.PIXELS_PER_METER))
    guiSim.update_node_positions()
    node_global_positions = [node.global_position for node in guiSim.data_nodes]
    while True:
        every_node_fits = True
        for node_global_position in node_global_positions:
            if constants.PIXELS_PER_METER == 1:
                every_node_fits = True  # Forced to quit
                break
            if not rect.collidepoint(node_global_position[0], node_global_position[1]):
                constants.PIXELS_PER_METER -= 1
                guiSim.update_node_positions()
                node_global_positions = [node.global_position for node in guiSim.data_nodes]
                every_node_fits = False

        if every_node_fits is True:
            print("SCALING done - new Pixels/Meter scale {}".format(constants.PIXELS_PER_METER))
            break


if __name__ == '__main__':
    # Fix seed for debugging purposes
    # np.random.seed(0)

    ## Globals
    guiSimMac = construct_simulation(SimType.MAC)
    print("GuiSimMac - processing done")

    game_quit = False
    guiSim = guiSimMac
    current_sim_type = SimType.MAC
    last_num_nodes = len(guiSim.data_nodes)
    guiSim.timeline.nodes_slider.setValue(last_num_nodes)

    # Auto-play sim variables
    simulation_time = pygame.time.get_ticks()  # integer index < SimConsts.TIME_MAX_STEPS
    last_timeline_change = pygame.time.get_ticks()

    while not game_quit:
        current_time_sim = pygame.time.get_ticks()

        ### CAPTURE
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                game_quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    toggle_autoplay(None)

        guiSim = guiSimMac
        current_sim_type = SimType.MAC
        sliderVal = guiSim.timeline.nodes_slider.getValue()
        SimConsts.set_num_nodes_mac(sliderVal) # Update the constants immediately - for new simulations
        last_num_nodes = sliderVal

        guiSim.timeline.network_load_slider.listen(events)
        guiSim.timeline.nodes_slider.listen(events)
        guiSim.timeline.time_slider.listen(events)

        ### RENDER and UPDATE
        guiSim.screen.fill((245, 245, 245))

        # Calculate timeline slider value based on keys and waiting
        timeVal = guiSim.timeline.time_slider.getValue()
        newTimeValue = timeVal
        if current_time_sim - last_timeline_change > TIMELINE_SCROLL_DEBOUNCE:
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
        networkLoadVal = guiSim.timeline.network_load_slider.getValue()
        SimConsts.set_simconsts_network_load(networkLoadVal)
        font_surface = guiSim.font.render("Network traffic: {} messages/time-step (requires new simulation run)".format(round(networkLoadVal, 3)), True,
                                          pygame.Color("black"))
        guiSim.screen.blit(font_surface, dest=(guiSim.timeline.nodes_slider.x, guiSim.timeline.network_load_slider.y + 20))
        font_surface = guiSim.font.render("Number of nodes: {} (requires new simulation run)".format(sliderVal), True,
                                          pygame.Color("black"))
        guiSim.screen.blit(font_surface, dest=(guiSim.timeline.nodes_slider.x, guiSim.timeline.nodes_slider.y + 20))
        font_surface = guiSim.font.render(
            "Current time: {} steps (scroll with LEFT/RIGHT arrows or use auto-play mode)".format(timeVal), True,
            pygame.Color("black"))
        guiSim.screen.blit(font_surface, dest=(guiSim.timeline.time_slider.x, guiSim.timeline.time_slider.y + 20))

        ### PROCESS mouse & RENDER WAVE and NODES
        autoplay = guiSim.get_checkbox_value(1, MENU_CHECKBOX_MAC_AUTOPLAY)
        if autoplay:
            if current_sim_type is SimType.MAC and current_time_sim - simulation_time > AUTOPLAY_SPEED_MS:
                simulation_time = current_time_sim
                guiSimMac.show_next_oracle_timeindex()
                print("Showing time-index", guiSimMac.show_oracle_states_timeindex)
                guiSimMac.timeline.time_slider.setValue(guiSimMac.show_oracle_states_timeindex)
        else:
            guiSimMac.draw_oraclestate_waves(timeVal)

        # RENDER - Nodes, sliders and menu
        guiSim.render_datanodes()
        guiSim.render_legend()
        guiSim.timeline.render()
        guiSim.side_menu.render_nav_backlight()
        guiSim.side_menu.render(events)
        pygame.display.update()
