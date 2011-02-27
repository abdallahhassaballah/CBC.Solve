"This module implements residuals used for adaptivity."

__author__ = "Kristoffer Selim and Anders Logg"
__copyright__ = "Copyright (C) 2010 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

# Last changed: 2011-02-27

from dolfin import *

from operators import Sigma_F as _Sigma_F

def inner_product(v, w):
    "Return inner product for mixed fluid/structure space"

    # Define cell integrals
    dx_F = dx(0)

    # Extract variables
    v1_F, q1_F = v
    v2_F, q2_F = w

    # Inner product on subdomains, requiring ident_zeros
    m1 = (inner(v1_F, v2_F) + q1_F*q2_F)*dx_F

    # Inner product on the whole domain
    m2 = (inner(v1_F, v2_F) + q1_F*q2_F)*dx

    return m2

def weak_residual(U0, U1, U, w, kn, problem):
    "Return weak residuals"

    # Extract variables
    U_F0, P_F0 = U0
    U_F1, P_F1 = U1
    U_F,  P_F  = U
    v_F, q_F = w

    # Get problem parameters
    Omega   = problem.mesh()
    rho_F   = problem.fluid_density()
    mu_F    = problem.fluid_viscosity()

    # Define normals
    N = FacetNormal(Omega)
    N_F = N

    # Define cell integrals
    dx_F = dx(0)

    # Define time derivative
    Dt_U_F = rho_F*((U_F1 - U_F0)/kn + dot(grad(U_F), U_F))

    # Define stress
    Sigma_F = _Sigma_F(U_F, P_F, mu_F)

    # Fluid residual
    R_F = inner(v_F, Dt_U_F)*dx_F + inner(grad(v_F), Sigma_F)*dx_F \
        - inner(v_F, mu_F*dot(grad(U_F).T, N_F))*ds \
        + inner(v_F, P_F*N_F)*ds \
        + inner(q_F, div(U_F))*dx_F

    return R_F

def strong_residual(U0, U1, U, Z, EZ, w, kn, problem):
    "Return strong residuals (integrated by parts)"

    # Extract variables
    U_F0, P_F0 = U0
    U_F1, P_F1 = U1
    U_F,  P_F  = U
    Z_F,  Y_F  = Z
    EZ_F, EY_F = EZ

    # Get problem parameters
    Omega   = problem.mesh()
    Omega_F = problem.fluid_mesh()
    rho_F   = problem.fluid_density()
    mu_F    = problem.fluid_viscosity()

    # Define normals
    N = FacetNormal(Omega)
    N_F = N

    # FIXME: Check sign of N_S, should it be -N?

    # Define inner products
    dx_F = dx(0)

    # Define "facet" products
    dS_F  = dS(0)

    # Define midpoint values
    U_F = 0.5 * (U_F0 + U_F1)
    P_F = 0.5 * (P_F0 + P_F1)

    # Define time derivative
    Dt_U_F = rho_F * ((U_F1 - U_F0)/kn + dot(grad(U_F), U_F))

    # Define stress
    Sigma_F = _Sigma_F(U_F, P_F, mu_F)

    # Fluid residual contributions
    R_F0 = w*inner(EZ_F - Z_F, Dt_U_F - div(Sigma_F))*dx_F
    R_F1 = avg(w)*inner(EZ_F('+') - Z_F('+'), jump(Sigma_F, N_F))*dS_F
    R_F2 = w*inner(EZ_F - Z_F, dot(Sigma_F, N_F))*ds
    R_F3 = w*inner(EY_F - Y_F, div(U_F))*dx_F

    return (R_F0, R_F1, R_F2, R_F3)
