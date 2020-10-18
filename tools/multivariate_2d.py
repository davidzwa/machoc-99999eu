import numpy as np
import matplotlib.pyplot as plt

mean = [0, 0] # Centered around coordinate (0,0)
cov = [[1, 0], [0, 1]]  # spherical covariance
# cov = [[1, 0], [0, 100]]  # diagonal covariance

# Diagonal covariance means that points are oriented along x or y-axis:
x, y = np.random.multivariate_normal(mean, cov, 10).T
plt.plot(x, y, 'x')
plt.axis('equal')
plt.show()
