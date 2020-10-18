import numpy as np

num_nodes = 10
mu = 0.0
sigma = 5.0
nodes_x = np.random.normal(mu, sigma, num_nodes)
nodes_y = np.random.normal(mu, sigma, num_nodes)

print(nodes_x, nodes_y)
