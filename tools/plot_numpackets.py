import matplotlib
import matplotlib.pyplot as plt
import numpy as np
data = np.array([
    [0.001,	0.002154435, 0.004641589, 0.01,	0.021544347, 0.046415888,
        0.1, 0.215443469, 0.464158883, 1, 2.15443469, 4.641588834, 10],
    [1.3, 2.1, 5.4, 8.0, 18.4, 42.3, 78.5, 120.4, 181.3, 314.2, 377.5, 307.3, 327], # Total
    [1.3, 2.1, 5.4, 8.0, 18.4, 42.2, 76.5, 114.8, 174.6, 308.4, 371.8, 300.0, 320.5]  # Succesful
])

fig, ax = plt.subplots()
print(data)
ax.semilogx(data[0], data[1])
ax.semilogx(data[0], data[2])
plt.title('Message count vs network load')
plt.legend(['Total messages', 'Succesful messages'], numpoints=1)
plt.ylabel('Message count')
plt.xlabel('Network load [messages/sec]')
plt.show()
