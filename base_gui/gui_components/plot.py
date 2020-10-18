# Integrate matplotlib with pygame
# import matplotlib
# import matplotlib.backends.backend_agg as agg
# import matplotlib.pyplot as plt
#
# matplotlib.use("Agg")
#
# fig = plt.figure(figsize=[3, 3])
# ax = fig.add_subplot(111)
# canvas = agg.FigureCanvasAgg(fig)
#
#
# def plot(data):
#     ax.plot(data)
#     canvas.draw()
#     renderer = canvas.get_renderer()
#     raw_data = renderer.tostring_rgb()
#     size = canvas.get_width_height()
#     return pygame.image.fromstring(raw_data, size, "RGB")
#
#
# a = np.array([1, 2, 3])
# plot_surface = plot(a)
# screen.blit(plot_surface, (200, 0))
