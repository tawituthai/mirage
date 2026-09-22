# MIRAGE Interface Control Document (ICD)

Single place for frames, units, conventions, rates and time tags at every interface.
Rule: if a signal crosses a module boundary, it has a row here before it has code.

| Item | Value |
| --- | --- |
| ICD version | v0 (Phase 0 / Lesson 1) |
| Truth simulator | Basilisk 2.12.0 (pip wheel `bsk`) |
| Python | Python 3.14.4 |
| Last updated | 2026-09-22 |

---

## 1. Reference frames

| Frame | Name | Definition | Status |
| --- | --- | --- | --- |
| N | Inertial | Basilisk inertial frame of the central body (Earth). Treated as ECI; J2000 alignment only once SPICE is added (Lesson 3) | In use |
| B | Body | Fixed to the 6U hub. Origin at hub CoM for now. Axis-to-structure mapping TBD | In use, axes TBD |
| H | Hill / LVLH | r-hat, (h x r)-hat, h-hat. Used for nadir pointing | Phase 5 |
| S_x | Sensor frames | One per sensor; mounting DCM [S B] | Phase 2 |

## 2. Attitude conventions

| Item | Basilisk truth | MIRAGE FSW |
| --- | --- | --- |
| Attitude of B relative to N | MRP `sigma_BN` | Quaternion `q_BN` |
| MRP shadow set | Switched when norm(sigma) > 1 (plots jump; expected) | n/a |
| Quaternion order | Euler parameters [b0, b1, b2, b3], scalar first | Scalar first (TBD: confirm in Lesson 2) |
| DCM | `[BN]` maps N-frame components to B-frame: v_B = [BN] v_N | Same |
| Body rate | `omega_BN_B`: rate of B relative to N, expressed in B, rad/s | Same |
| Sign check | Known-rotation test in `tests/` (Lesson 2) | Same test |

Do not rely on "Hamilton" / "JPL" labels. The Lesson 2 known-rotation test is the definition.

## 3. Units

SI everywhere: m, m/s, kg, kg m^2, N m, rad, rad/s, s, T (magnetic field).
Degrees only in plots and printouts, never in interfaces.
Earth gravitational parameter `mu` in m^3/s^2 (from `simIncludeGravBody`).

## 4. Time

| Item | Value |
| --- | --- |
| Sim time base | int64 nanoseconds since sim start (Basilisk `CurrentNanos`) |
| Calendar epoch | None yet. Added with `spiceInterface` in Lesson 3 |
| FSW time | TBD. HIL target: GPS time delivered by GPS emulator |
| Timestamp meaning | Every measurement carries the sim time at which it is VALID, not when delivered |

## 5. Task rates

| Task | Rate | Period | Notes |
| --- | --- | --- | --- |
| Dynamics (`dynTask`) | 10 Hz | 0.1 s | Integrator step; revisit after Lesson 1 exercise 3 |
| Truth recorder | 1 Hz | 1.0 s | Logging only |
| FSW | TBD | TBD | Phase 4/5 |

## 6. Signals

| Signal | Producer -> Consumer | Frame | Units | Rate | Notes |
| --- | --- | --- | --- | --- | --- |
| r_BN_N | Basilisk `scStateOutMsg` -> recorder | N | m | 1 Hz | Position of B origin rel. N |
| v_BN_N | Basilisk `scStateOutMsg` -> recorder | N | m/s | 1 Hz | Inertial velocity |
| sigma_BN | Basilisk `scStateOutMsg` -> recorder | B rel. N | MRP (-) | 1 Hz | Shadow-set switching |
| omega_BN_B | Basilisk `scStateOutMsg` -> recorder | B | rad/s | 1 Hz | |

## 7. Spacecraft parameters (placeholders)

| Parameter | Value | Frame | Source |
| --- | --- | --- | --- |
| Hub mass | 12.0 kg | - | Placeholder |
| Inertia about CoM | diag(0.14, 0.13, 0.06) kg m^2 | B | Placeholder; replace with CAD |

## 8. Open items

- [ ] Define B axes relative to the 6U structure (which face is +Z)
- [ ] Confirm FSW quaternion convention (Lesson 2)
- [ ] Add SPICE epoch and J2000 alignment of N (Lesson 3)
- [ ] Replace mass properties with CAD values

## Change log

| Date | Version | Change |
| --- | --- | --- |
| 2026-09-22 | v0 | Initial: frames, conventions, Lesson 1 truth signals |
