"""
check_condition_c.py

Empirical verification of Proposition 3.1 conditions (C) and (C<) from
"Optimal split of orders across liquidity pools: a stochastic algorithm approach".

Condition (C):   min_i φ'i(0) >= max_i φ'i(1/(N-1))
Condition (C<): min_i φ'i(0) >  max_i φ'i(1/(N-1))

where φ'i(u) = ρi * E[ V * 1_{uV < Di} ]

If (C) holds:   argmax over the simplex P_N is a compact convex set and
                 argmax_H_N = argmax_P_N (unconstrained = constrained).

If (C<) holds:  strictly, the maximizer lies in int(P_N) - every pool
                 receives strictly positive allocation.
"""

import numpy as np


def phi_prime(u: float,
              V: np.ndarray,
              Di: np.ndarray,
              rho_i: float) -> float:
    """Empirical estimate of φ'i(u) = ρ_i * E[ V * 1_{uV < Di} ].

    V   : array of traded volumes  
    Di : array of dark pool i capacities 
    rho_i : rebate parameter for pool i
    """
    indicator = (u * V < Di).astype(float)
    return rho_i * np.mean(V * indicator)


def check_condition_c(darkpool) -> dict:
    """Check conditions (C) and (C<) for a DarkPool instance.

    Parameters
    ----------
    darkpool : DarkPool

    Returns
    -------
    dict with keys:
        'phi_prime_at_0'      : array of φ'i(0) for each pool
        'phi_prime_at_bound'  : array of φ'i(1/(N-1)) for each pool
        'min_phi_prime_0'     : min_i φ'i(0)           (LHS of both conditions)
        'max_phi_prime_bound' : max_i φ'i(1/(N-1))     (RHS of both conditions)
        'C_holds'             : bool - does (C) hold?    (>=)
        'C_strict_holds'      : bool - does (C<) hold?  (>)
    """
    V = np.array(darkpool.dico_volumes[darkpool.traded_asset], dtype=float)
    N = len(darkpool.reference_assets)
    u_bound = 1.0 / (N - 1)

    phi_at_0 = np.zeros(N)
    phi_at_bound = np.zeros(N)

    print("=" * 65
          )
    print("Proposition 3.1 — Condition (C) / (C<) Check")
    print("=" * 65)
    print(f"N = {N} pools,  u_bound = 1/(N-1) = {u_bound:.4f}")
    print(f"ρ = {darkpool.rho}")
    print(f"Number of time periods: {len(V)}")
    print("-" * 65)

    for i, asset in enumerate(darkpool.reference_assets):
        Di = np.array(darkpool.dico_darkpools[asset], dtype=float)

        phi_at_0[i] = phi_prime(0.0, V, Di, darkpool.rho[i])
        phi_at_bound[i] = phi_prime(u_bound, V, Di, darkpool.rho[i])

        print(f"  Pool {i} ({asset}):")
        print(f"    ρ{i} = {darkpool.rho[i]:.4f}")
        print(f"    φ'{i}(0)              = {phi_at_0[i]:.6f}")
        print(f"    φ'{i}(1/(N-1)={u_bound:.4f}) = {phi_at_bound[i]:.6f}")
        print()

    lhs = phi_at_0.min()
    rhs = phi_at_bound.max()

    C_holds = lhs >= rhs
    C_strict = lhs > rhs

    print("-" * 65)
    print(f"  LHS = min_i φ'i(0)         = {lhs:.8f}   (pool {phi_at_0.argmin()})")
    print(f"  RHS = max_i φ'i(1/(N-1))   = {rhs:.8f}   (pool {phi_at_bound.argmax()})")
    print(f"  Gap = LHS - RHS             = {lhs - rhs:.8f}")
    print("-" * 65)

    if C_strict:
        print("  (C<) HOLDS (strict inequality)")
        print("  => argmax_P_N Φ = argmax_H_N Φ ⊂ int(P_N)")
        print("  => Every pool receives strictly positive allocation at optimum.")
        print("  => The equalized-marginal Lagrangian derivation is rigorous.")
    elif C_holds:
        print("  (C) HOLDS (weak inequality, not strict)")
        print("  => argmax_P_N Φ = argmax_H_N Φ (constrained = unconstrained)")
        print("  => But some pool may sit exactly at ri* = 0 (boundary).")
    else:
        print("  (C) FAILS")
        print("  => Cannot guarantee argmax_H_N = argmax_P_N.")
        print("  => The simplified Lagrangian characterization may miss the true")
        print("     constrained optimum. The algorithm still converges (projection")
        print("     handles boundary cases), but the equalization condition")
        print("     φ'i(r*i) = λ for all i may not hold at the true r*.")
    print("=" * 65)

    return {
        "phi_prime_at_0": phi_at_0,
        "phi_prime_at_bound": phi_at_bound,
        "min_phi_prime_0": lhs,
        "max_phi_prime_bound": rhs,
        "C_holds": C_holds,
        "C_strict_holds": C_strict,
    }



