"""MIRAGE Lesson 1: torque-free 6U in LEO, with truth logging and invariant checks.
Usage:
  python scenarios/spin_viz.py          # headless, full speed: prints checks, shows plots
  python scenarios/spin_viz.py live     # stream to Vizard (start Vizard first, DirectComm)
  python scenarios/spin_viz.py save     # write a .bin for Vizard playback
"""
import sys
import numpy as np
from Basilisk.utilities import (SimulationBaseClass, macros, orbitalMotion,
                                simIncludeGravBody, unitTestSupport, vizSupport)
from Basilisk.utilities import RigidBodyKinematics as rbk
from Basilisk.simulation import spacecraft, simSynch

I_HUB = np.array([[0.14, 0.0, 0.0],
                  [0.0, 0.13, 0.0],
                  [0.0, 0.0, 0.06]])          # kg m^2, about hub CoM, body frame B


def run(mode="none", omega0_B=(0.0, 0.0, np.deg2rad(5.0)),
        dt=0.1, t_stop=95 * 60.0, log_dt=1.0):
    """Run the scenario and return recorded truth as numpy arrays (SI units)."""
    scSim = SimulationBaseClass.SimBaseClass()
    proc = scSim.CreateNewProcess("simProcess")
    task = "dynTask"
    proc.addTask(scSim.CreateNewTask(task, macros.sec2nano(dt)))

    sc = spacecraft.Spacecraft()
    sc.ModelTag = "MIRAGE-6U"
    sc.hub.mHub = 12.0
    sc.hub.IHubPntBc_B = unitTestSupport.np2EigenMatrix3d(I_HUB.flatten().tolist())
    scSim.AddModelToTask(task, sc)

    grav = simIncludeGravBody.gravBodyFactory()
    earth = grav.createEarth()
    earth.isCentralBody = True
    grav.addBodiesTo(sc)

    oe = orbitalMotion.ClassicElements()
    oe.a, oe.e = 6921e3, 0.001                # ~550 km altitude
    oe.i, oe.Omega = np.deg2rad(97.5), np.deg2rad(30.0)
    oe.omega, oe.f = 0.0, 0.0
    rN, vN = orbitalMotion.elem2rv(earth.mu, oe)
    sc.hub.r_CN_NInit = rN                    # m, inertial frame N
    sc.hub.v_CN_NInit = vN                    # m/s
    sc.hub.sigma_BNInit = [[0.0], [0.0], [0.0]]
    sc.hub.omega_BN_BInit = [[w] for w in omega0_B]

    # Truth recorder: sampled every log_dt seconds of SIM time
    rec = sc.scStateOutMsg.recorder(macros.sec2nano(log_dt))
    scSim.AddModelToTask(task, rec)

    if mode == "live":
        clock = simSynch.ClockSynch()         # pace only when a human is watching
        clock.accelFactor = 50.0
        scSim.AddModelToTask(task, clock)
        vizSupport.enableUnityVisualization(scSim, task, sc, liveStream=True)
    elif mode == "save":
        vizSupport.enableUnityVisualization(scSim, task, sc, saveFile=__file__)

    scSim.InitializeSimulation()
    scSim.ConfigureStopTime(macros.sec2nano(t_stop))
    scSim.ExecuteSimulation()

    return {
        "t": rec.times() * macros.NANO2SEC,   # s, sim time
        "r_N": np.array(rec.r_BN_N),           # m, inertial
        "v_N": np.array(rec.v_BN_N),           # m/s, inertial
        "sigma_BN": np.array(rec.sigma_BN),    # MRP, B relative to N
        "omega_B": np.array(rec.omega_BN_B),   # rad/s, body frame
        "mu": earth.mu,                        # m^3/s^2
    }


def invariants(d, I=I_HUB):
    """Quantities that MUST stay constant with no torque and point-mass gravity only.
    Ref: Schaub & Junkins ch. 4; two-body energy E = v^2/2 - mu/r."""
    rn = np.linalg.norm(d["r_N"], axis=1)
    vn = np.linalg.norm(d["v_N"], axis=1)
    E_orb = 0.5 * vn**2 - d["mu"] / rn                            # J/kg
    # H computed in B, rotated to N with [NB] = [BN]^T
    H_N = np.array([rbk.MRP2C(s).T @ (I @ w)
                    for s, w in zip(d["sigma_BN"], d["omega_B"])])  # N m s, inertial
    T_rot = np.array([0.5 * w @ I @ w for w in d["omega_B"]])      # J
    return E_orb, H_N, T_rot


def rel_drift(x):
    """Max deviation from the initial value, relative to the initial magnitude."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    return np.max(np.linalg.norm(x - x[0], axis=1)) / np.linalg.norm(x[0])


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    mode = sys.argv[1] if len(sys.argv) > 1 else "none"
    d = run(mode)
    E_orb, H_N, T_rot = invariants(d)
    print(f"orbital energy rel drift : {rel_drift(E_orb):.2e}")
    print(f"H_N vector rel drift     : {rel_drift(H_N):.2e}")
    print(f"rot. energy rel drift    : {rel_drift(T_rot):.2e}")

    fig, ax = plt.subplots(3, 1, sharex=True)
    ax[0].plot(d["t"], np.rad2deg(d["omega_B"])); ax[0].set_ylabel("omega_BN_B [deg/s]")
    ax[1].plot(d["t"], d["sigma_BN"]);            ax[1].set_ylabel("sigma_BN [-]")
    ax[2].plot(d["t"], H_N);                      ax[2].set_ylabel("H_N [N m s]")
    ax[2].set_xlabel("sim time [s]")
    plt.show()