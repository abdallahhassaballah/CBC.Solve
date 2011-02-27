from pylab import *

# Displacement functional
#P1 = [-0.00812774, -0.00854478, -0.00868839, -0.00875618, -0.00878991]
#P2 = [-0.00865696, -0.00873283, -0.00877648, -0.00880243, -0.00879446]

# Integral of traction
P1 = [-0.52899165266, -0.532277953108, -0.540408795185, -0.546991733039, -0.550656799983, -0.552861669711]
P2 = [-0.52899165266, -0.532277953108, -0.540408795185, -0.546991733039]

plot(P1, 'g-o')
plot(P2, 'b-o')
grid(True)
legend(["P1", "P2"])
show()