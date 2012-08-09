"This module specifies the Jacobian forms for the monolithic FSI problem."

__author__ = "Gabriel Balaban"
__copyright__ = "Copyright (C) 2010 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

from dolfin import *
from cbc.swing.operators import *
from cbc.twist import PiolaTransform
from cbc.swing.operators import Sigma_F as _Sigma_F
from cbc.swing.operators import Sigma_S as _Sigma_S
from cbc.swing.operators import Sigma_M as _Sigma_M
from cbc.swing.operators import F, J, I

##Throughout this module the following notation is used.

##U_F Fluid Velocity
##P_F Fluid Pressure
##L_U Fluid lagrange multiplier that enforces kinematic continuity of fluid and structure

##D_S Structure displacement
##U_S Structure Velocity

##D_F Fluid Domain Displacement
##L_D Fluid Domain lagrange multiplier that enforces displacement matching with structure on FSI boundary

##Test functions are related to their trial functions by the following letter substitution.
## u-> v , p-> q, l-> m, d -> c

def fsi_jacobian(Iulist,Iudotlist,Iumidlist,U1list,Umidlist,Udotlist,Vlist,
                 dotVlist,matparams,measures,forces,normals,params):
    """"
    Build the jacobian forms for the full FSI problem
    including the fluid, structure and mesh equations

    Iulist   - Trial(increment) function list
             - IU_F,IP_F,IL_U,ID_S,IU_S,ID_F,IL_D

    Iudotlist - Trial function time derivative list
              - IU_Fmid,IP_Fmid,IL_Umid,ID_Smid,IU_Smid,ID_Fmid,IL_Dmid

    Iumidlist - Trial function time approximation list
              - IU_Fdot,IP_Fdot,IL_Udot,ID_Sdot,IU_Sdot,ID_Fdot,IL_Ddot
    
    U1list   - List of current fsi variables
             - U1_F,P1_F,L1_U,D1_S,U1_S,D1_F,L1_D

    Umidlist - List of time approximated fsi variables.
             - U_Fmid,P_Fmid,L_Umid,D_Smid,U_Smid,D_Fmid,L_Dmid

    Vlist    - List of Test functions
             - v_F,q_F,m_U,c_S,v_S,c_F,m_D

    dotVlist - List of time integrated by parts test functions used in the
             - dual problem. For the FSI jacobian dotVlist = Vlist.
               
    matparams - Dictionary of material parameters
              - mu_F,rho_F,mu_S,lmbda_S,rho_S,mu_FD,lmbbda_M

    measures  - Dictionary of measures
              - dxF,dxS,dxM,dsF,dsS,dFSI
               (dx = interior, ds = exterior boundary, dFSI = FSI interface)

    normals - Dictionary of outer normals
            - N_F, N_S           
    """
    info_blue("Creating Jacobian Forms")

    #Unpack Functions
    U1_F,P1_F,L1_U,D1_S,U1_S,D1_F,L1_D = U1list
    u_Fdot,p_Fdot,l_Fdot,u_Sdot,p_Sdot,u_Mdot,l_Mdot = Udotlist

    #Unpack Trial Functions
    IU_F,IP_F,IL_U,ID_S,IU_S,ID_F,IL_D = Iulist

    #Unpack Test Functions
    v_F,q_F,m_U,c_S,v_S,c_F,m_D = Vlist

    #Unpack Test Functions
    dotv_F,dotq_F,dotm_U,dotc_S,dotv_S,dotc_F,dotm_D = dotVlist

    #Unpack Material Parameters
    mu_F = matparams["mu_F"]
    rho_F = matparams["rho_F"]
    mu_S = matparams["mu_S"]
    lmbda_S = matparams["lmbda_S"]
    rho_S = matparams["rho_S"]
    #To the user "M-mesh", here "FD-Fluid Domain"
    mu_FD = matparams["mu_M"]
    lmbda_FD = matparams["lmbda_M"]

    #Unpack Measures
    dxF = measures["dxF"]
    dxS = measures["dxS"]
    dxM = measures["dxM"]
    dsF = measures["dsF"]
    dsS = measures["dsS"]
    #dsM = measures["dsM"] (not in use at the moment)
    dFSI = measures["dFSI"]

    #Unpack Normals
    N_F = normals["N_F"]
    N_S = normals["N_S"]

    #Unpack forces
    F_F = forces["F_F"]
    F_S = forces["F_S"]
    F_FD = forces["F_M"]
    G_S = forces["G_S"]
    G_F = forces["G_F"]

    #Unpack the time approximated functions 
    IU_Fmid,IP_Fmid,IL_Umid,ID_Smid,IU_Smid,ID_Fmid,IL_Dmid = Iumidlist
    IU_Fdot,IP_Fdot,IL_Udot,ID_Sdot,IU_Sdot,ID_Fdot,IL_Ddot = Iudotlist
    U_Fmid,P_Fmid,L_Umid,D_Smid,U_Smid,D_Fmid,L_Dmid = Umidlist
    u_Fdot,p_Fdot,l_Fdot,u_Sdot,p_Sdot,u_Mdot,l_Mdot = Udotlist    

    #Diagonal Blocks
    j_F = J_BlockF(IU_Fdot,IU_Fmid,IP_F,U_Fmid,u_Mdot,v_F,dotv_F,q_F,D1_F,
                   rho_F,mu_F,N_F,dxF,dsF,G_F)
    
    j_S = J_BlockS(ID_Sdot,IU_Sdot,ID_Smid,IU_Smid,D_Smid,U_Smid,c_S,dotc_S,
                   v_S,dotv_S,mu_S,lmbda_S,rho_S,dxS)
    
    j_FD = J_BlockFD(ID_Fdot,ID_Fmid,c_F,c_F,mu_FD,lmbda_FD,dxM)
    
    #Interface Block
    j_FSI = J_FSI(IU_F,IU_Fmid,IP_Fmid,ID_F,ID_Fmid,ID_S,IU_S,IL_D,IL_U,U_Fmid,P_Fmid,
                  D_Fmid,v_F,c_S,c_F,m_D,m_U,mu_F,N_F,dFSI)

    #Fluid-Fluid Domain Block
    if params["optimization"]["simplify_jacobian"] == True:
        #Effect of D_F on U_F is restricted to the interface since
        #nodes far away from the interface are almost uneffected by D_F.
        j_FFD = J_BlockFFD_simplified(U_Fmid, u_Fdot,P1_F, D1_F, ID_F, u_Mdot, ID_Fdot,
                                      v_F, dotv_F, q_F, rho_F, mu_F,N_F, dxF,dsF,dFSI,G_F,F_F)
    else:
        j_FFD = J_BlockFFD(U_Fmid, u_Fdot,P1_F, D1_F, ID_F, u_Mdot, ID_Fdot,
                           v_F, dotv_F, q_F, rho_F, mu_F,N_F, dxF,dsF,G_F,F_F)

    j = j_F + j_S + j_FD + j_FFD + j_FSI

    return j

def dD_FSigmaF(U_M,dD_F,U_F,P_F,mu_F):
    """Derivative of Sigma_F with respect to D_F"""
    ret =   J(U_M)*tr(dot(grad(dD_F), inv(F(U_M))))*dot(Sigma_F(U_F, P_F, U_M, mu_F), inv(F(U_M)).T)
    ret += - J(U_M)*dot(mu_F*(dot(grad(U_F), dot(inv(F(U_M)), dot(grad(dD_F), inv(F(U_M)))))), inv(F(U_M)).T)
    ret += - J(U_M)*dot(mu_F*(dot(inv(F(U_M)).T, dot(grad(dD_F).T, dot(inv(F(U_M)).T, grad(U_F).T )))), inv(F(U_M)).T)
    ret += - J(U_M)*dot(dot(Sigma_F(U_F, P_F, U_M, mu_F), inv(F(U_M)).T), dot(grad(dD_F).T, inv(F(U_M)).T))
    return ret

def J_BlockF(dotdU,dU,dP,U,dotU_M,v,dotv,q,U_M,rho,mu,N_F,dxF,dsF,g_F=None):
    """Fluid Diagonal Block, Fluid Domain """
    
    #DT (without ALE term)
    J_FF =  inner(dotv, rho*J(U_M)*dotdU)*dxF                              
    J_FF +=  inner(v, rho*J(U_M)*dot(dot(grad(dU), inv(F(U_M))), U - dotU_M))*dxF  
    J_FF +=  inner(v, rho*J(U_M)*dot(grad(U), dot(inv(F(U_M)), dU)))*dxF

    #div Sigma_F
    J_FF +=  inner(grad(v), J(U_M)*mu*dot(grad(dU), dot(inv(F(U_M)), inv(F(U_M)).T)))*dxF     
    J_FF +=  inner(grad(v), J(U_M)*mu*dot(inv(F(U_M)).T, dot(grad(dU).T, inv(F(U_M)).T)))*dxF 
    J_FF += -inner(grad(v), J(U_M)*dP*inv(F(U_M)).T)*dxF                                       

    #div U_F (incompressibility)
    J_FF +=  inner(q, div(J(U_M)*dot(inv(F(U_M)), dU)))*dxF

    #Do nothing BC if in use.
    if g_F is None or g_F == []:
        J_FF  += -inner(v, dot(J(U_M)*mu*dot(inv(F(U_M)).T, dot(grad(dU).T, inv(F(U_M)).T)), N_F))*dsF
        J_FF  +=  inner(v, J(U_M)*dP*dot(I, dot(inv(F(U_M)).T, N_F)))*dsF

    return J_FF

def J_BlockFFD(U, dotU, P, U_M, dD_F,dotU_M, dotdD_F, v_F,dotv, q, rho, mu,N_F, dxF,ds_F,g_F = None,F_F = None):
    """Fluid-Fluid Domain coupling"""
    
    #DT  
    J_FM =  inner(v_F, rho*J(U_M)*tr(dot(grad(dD_F), inv(F(U_M))))*dotU)*dxF
    J_FM +=  inner(v_F, rho*J(U_M)*tr(dot(grad(dD_F), inv(F(U_M))))*dot(grad(U), dot(inv(F(U_M)), U - dotU_M)))*dxF
    J_FM += -inner(v_F,rho*J(U_M)*dot((dot(grad(U), dot(inv(F(U_M)), \
             dot(grad(dD_F), inv(F(U_M)))))), U - dotU_M ))*dxF
    J_FM += -inner(v_F, rho*J(U_M)*dot(grad(U), dot(inv(F(U_M)),dotdD_F)))*dxF

    #SigmaF
    J_FM += inner(grad(v_F),dD_FSigmaF(U_M,dD_F,U,P,mu))*dxF

    #Div U_F (incompressibility)
    J_FM +=  inner(q, div(J(U_M)*tr(dot(grad(dD_F), inv(F(U_M))))*dot(inv(F(U_M)), U)))*dxF
    J_FM += -inner(q, div(J(U_M)*dot(dot(inv(F(U_M)), grad(dD_F)), dot(inv(F(U_M)), U))))*dxF

    ##Add the terms for the Do nothing boundary if necessary
    if g_F is None:
         #Derivative of do nothing tensor with J factored out
        dSigma  =  tr(grad(dD_F)*inv(F(U_M)))*(mu*inv(F(U_M)).T*grad(U).T - P*I)*inv(F(U_M)).T
        dSigma += -mu*inv(F(U_M)).T*grad(dD_F).T*inv(F(U_M)).T*grad(U).T*inv(F(U_M)).T
        dSigma += -(mu*inv(F(U_M)).T*grad(U).T - P*I)*inv(F(U_M)).T*grad(dD_F).T*inv(F(U_M)).T

        #Add the J                           
        dSigma = J(U_M)*dSigma        
        J_FM += -inner(v_F,dot(dSigma,N_F))*ds_F

    #If a fluid body force has been specified, it will end up here. 
    if F_F is not None:
        J_FM += -inner(v_F,J(U_M)*tr(dot(grad(dD_F),inv(F(U_M))))*F_F)*dxF
    return J_FM

def J_BlockFFD_simplified(U, dotU, P, U_M, dD_F,dotU_M, dotdD_F, v_F,dotv, q,
                          rho, mu,N_F, dxF,ds_F,dFSI,g_F = None,F_F = None):
    """Fluid-Fluid Domain coupling"""
    
    #DT  
    J_FM =  inner(v_F, rho*J(U_M)*tr(dot(grad(dD_F), inv(F(U_M))))*dotU)('+')*dFSI
    J_FM +=  inner(v_F, rho*J(U_M)*tr(dot(grad(dD_F), inv(F(U_M))))*dot(grad(U), dot(inv(F(U_M)),\
                                                                                     U - dotU_M)))('+')*dFSI
    J_FM += -inner(v_F,rho*J(U_M)*dot((dot(grad(U), dot(inv(F(U_M)), \
             dot(grad(dD_F), inv(F(U_M)))))), U - dotU_M ))('+')*dFSI
    J_FM += -inner(v_F, rho*J(U_M)*dot(grad(U), dot(inv(F(U_M)),dotdD_F)))('+')*dFSI

    #SigmaF
    J_FM += inner(grad(v_F),dD_FSigmaF(U_M,dD_F,U,P,mu))('+')*dFSI

    #Div U_F (incompressibility)
    J_FM +=  inner(q, div(J(U_M)*tr(dot(grad(dD_F), inv(F(U_M))))*dot(inv(F(U_M)), U)))('+')*dFSI
    J_FM += -inner(q, div(J(U_M)*dot(dot(inv(F(U_M)), grad(dD_F)), dot(inv(F(U_M)), U))))('+')*dFSI
    ##Add the terms for the Do nothing boundary if necessary
    if g_F is None:
         #Derivative of do nothing tensor with J factored out
        dSigma  =  tr(grad(dD_F)*inv(F(U_M)))*(mu*inv(F(U_M)).T*grad(U).T - P*I)*inv(F(U_M)).T
        dSigma += -mu*inv(F(U_M)).T*grad(dD_F).T*inv(F(U_M)).T*grad(U).T*inv(F(U_M)).T
        dSigma += -(mu*inv(F(U_M)).T*grad(U).T - P*I)*inv(F(U_M)).T*grad(dD_F).T*inv(F(U_M)).T

        #Add the J                           
        dSigma = J(U_M)*dSigma        
        J_FM += -inner(v_F,dot(dSigma,N_F))*ds_F

    #If a fluid body force has been specified, it will end up here. 
    if F_F is not None:
        J_FM += -inner(v_F,J(U_M)*tr(dot(grad(dD_F),inv(F(U_M))))*F_F)*dxF
    return J_FM

def J_BlockS(dotdD_S, dotdU_S, dD_S, dU_S, D_S, U_S, c_S,dotc_S, v_S, dotv_S, mu_S, lmbda_S, rho_S, dxS): 
    "Structure diagonal block"
    F_S = grad(D_S) + I                 #I + grad U_s
    E_S = 0.5*(F_S.T*F_S - I)           #Es in the book
    dE_S = 0.5*(grad(dD_S).T*F_S + F_S.T*grad(dD_S))#Derivative of Es wrt to US in the book
    dUsSigma_S = grad(dD_S)*(2*mu_S*E_S + lmbda_S*tr(E_S)*I) + F_S*(2*mu_S*dE_S + lmbda_S*tr(dE_S)*I)

    J_S = inner(dotc_S, rho_S*dotdU_S)*dxS + inner(grad(c_S), dUsSigma_S)*dxS \
           + inner(dotv_S, dotdD_S - dU_S)*dxS   
    return J_S

def J_BlockFD(dD_Fdot,dD_F,c_F,dotc_F,mu_FD,lmbda_FD,dx_F):
    """Fluid Domain diagonal block"""
    Sigma_FD = _Sigma_M(dD_F, mu_FD, lmbda_FD)
    J_FD = inner(dotc_F, dD_Fdot)*dx_F + inner(sym(grad(c_F)), Sigma_FD)*dx_F
    return J_FD

def J_FSI(dU_F,dU_Fmid,dP_Fmid,dD_F,dD_Fmid,dD_S,dU_S,dL_D,dL_U,U_Fmid,P_Fmid,D_Fmid,
          v_F,c_S,c_F,m_D,m_U,mu_F,N_F,dFSI):
    """Derivative of the Interface Residual"""

    J_FSI = inner(m_D, dD_F - dD_S)('+')*dFSI 
    J_FSI += inner(c_F, dL_D)('+')*dFSI #Lagrange Multiplier
    
    J_FSI += inner(m_U,dU_F - dU_S)('+')*dFSI
    J_FSI += inner(v_F,dL_U)('+')*dFSI #Lagrange Multiplier

    Sigma_F = PiolaTransform(_Sigma_F(dU_Fmid, dP_Fmid, D_Fmid, mu_F), D_Fmid)
    J_FSI += -(inner(c_S('-'),dot(Sigma_F('+'),N_F('-'))))*dFSI
    
    J_FSI += -inner(c_S('-'),dot(dD_FSigmaF(D_Fmid,dD_Fmid,U_Fmid,P_Fmid,mu_F)('+'),N_F('-')))*dFSI
    return J_FSI
