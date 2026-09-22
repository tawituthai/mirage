"""Lesson 1 tests: Basilisk truth conserves the invariants of a torque-free rigid body
in point-mass gravity. If these fail, nothing built on top of the sim can be trusted.

Refs:
  - Schaub & Junkins, Analytical Mechanics of Space Systems, ch. 4
    (Euler's rotational equations; torque-free motion conserves H_N and T_rot)
  - Two-body specific orbital energy: E = v^2/2 - mu/r (constant under point-mass gravity)
"""
import numpy as np
import pytest

from scenarios.spin_viz import run, invariants, rel_drift

TOL = 1e-6          # max relative drift allowed over the run
T_STOP = 600.0      # s of sim time (10 min) - keeps the test fast


@pytest.fixture(scope="module")
def tumbling():
    """Intermediate-axis spin with small off-axis rates: the attitude motion is
    non-trivial (Dzhanibekov flip), so conservation is a real test."""
    return run("none", omega0_B=(0.001, np.deg2rad(5.0), 0.001), t_stop=T_STOP)


def test_orbital_energy_conserved(tumbling):
    E_orb, _, _ = invariants(tumbling)
    assert rel_drift(E_orb) < TOL


def test_inertial_angular_momentum_conserved(tumbling):
    """H must be constant in N (not in B). Fails if [BN] vs [NB] is mixed up."""
    _, H_N, _ = invariants(tumbling)
    assert rel_drift(H_N) < TOL


def test_rotational_energy_conserved(tumbling):
    _, _, T_rot = invariants(tumbling)
    assert rel_drift(T_rot) < TOL


def test_recorder_timing(tumbling):
    """Recorder logs at 1 s sim time from t=0: sanity check on the time base."""
    t = tumbling["t"]
    assert t[0] == pytest.approx(0.0)
    assert np.allclose(np.diff(t), 1.0)
    assert T_STOP - 1.0 <= t[-1] <= T_STOP   # last-sample inclusion is Basilisk-version dependent


def test_attitude_actually_moves(tumbling):
    """Guard against a silent no-op sim: body rates must change during a tumble."""
    w = tumbling["omega_B"]
    assert np.max(np.linalg.norm(w - w[0], axis=1)) > 1e-4