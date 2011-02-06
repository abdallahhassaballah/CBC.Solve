from fsirun import *

# Set parameters
p = default_parameters()
p["solve_primal"] = True
p["solve_dual"] = True
p["estimate_error"] = True
p["uniform_timestep"] = True
p["tolerance"] = 1e-6
p["initial_timestep"] = 0.01
p["dorfler_marking"] = False
p["marking_fraction"] = 0.75
p["description"] = "adaptive, k = 0.01, non-Dorfler (0.75)"

# Run problem
run_local("modified_pressure_driven_cavity", p)
