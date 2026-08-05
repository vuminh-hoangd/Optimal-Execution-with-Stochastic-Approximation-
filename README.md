@@
-# Optimal Execution: Splitting Orders Across Dark Liquidity Pools
-
-Stochastic-approximation approach to routing an order across $N$ dark
-pools with unknown, time-varying liquidity.
-
-## 1. Problem Formulation
-
-A random volume $V>0$ is executed across $N$ dark pools. Pool $i$ offers
-a rebate $\rho_i\in(0,1)$ on the reference price $S$ and has unobserved
-random capacity $D_i\ge0$. Routing a fraction $r_i$ of $V$ to pool $i$
-fills $\min(r_iV,D_i)$ there; the rest executes on the lit market at $S$.
-
-Minimizing expected execution cost is equivalent to finding $r^*$:
-
-$$
-r^* \in\argmax_{r \in \mathcal{P}_N} \sum_{i=1}^{N} \rho_i \, \mathbb{E}[\min(r_i V, D_i)] =: \argmax_{r \in \mathcal{P}_N} \sum_{i=1}^{N} \varphi_i(r_i),\qquad
-\mathcal P_N := \{r\in\mathbb R_+^N : \sum_{i=1}^N r_i = 1\Big\}.
-$$
+# Optimal Execution: Splitting Orders Across Dark Liquidity Pools
+
+Stochastic-approximation approach to routing an order across $N$ dark
+pools with unknown, time-varying liquidity.
+
+## 1. Problem Formulation
+
+A random volume $V>0$ is executed across $N$ dark pools. Pool $i$ offers
+a rebate $\rho_i\in(0,1)$ on the reference price $S$ and has unobserved
+random capacity $D_i\ge 0$. Routing a fraction $r_i$ of $V$ to pool $i$
+fills $\min(r_i V, D_i)$ there; the rest executes on the lit market at $S$.
+
+Minimizing expected execution cost is equivalent to finding $r^*$:
+
+$$
+r^* \in \argmax_{r \in \mathcal{P}_N} \sum_{i=1}^{N} \rho_i \, \mathbb{E}[\min(r_i V, D_i)]
+=: \argmax_{r \in \mathcal{P}_N} \sum_{i=1}^{N} \varphi_i(r_i),
+\qquad
+\mathcal{P}_N := \{\, r \in \mathbb{R}_+^N : \sum_{i=1}^N r_i = 1 \,\}.
+$$
@@
-By KKT condition, the maximizer $r^*$ is characterized by:
-
-$$
-\mathbb E\Big[\underbrace{V\Big(\rho_i\mathbb 1_{\{r_i^*V<D_i\}} - \tfrac1N\sum_{j=1}^N\rho_j\mathbb 1_{\{r_j^*V<D_j\}}\Big)}_{=:H_i(r^*,Y)}\Big] = 0, \qquad \forall i, \quad Y=(V,D_1,\dots,D_N).
-$$
-
-So $r^*$ solves $h(r):=\mathbb E[H(r,Y)]=0 \iff \begin{bmatrix} \mathbb{E}[H_1(r, Y)] \\ \mathbb{E}[H_2(r, Y)] \\ \vdots \\ \mathbb{E}[H_N(r, Y)] \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ \vdots \\ 0 [...]
-— a zero of an expectation that
-can be **sampled** (one realized fill/no-fill per trading period) even
-though the distribution of $(V,D_i)$ is never known.
+By the KKT conditions, the maximizer $r^*$ is characterized by
+
+$$
+\mathbb{E}\Big[\,V\Big(\rho_i \mathbf{1}_{\{r_i^* V < D_i\}} - \tfrac{1}{N}\sum_{j=1}^N \rho_j \mathbf{1}_{\{r_j^* V < D_j\}}\Big)\Big] = 0,
+\qquad \forall i,
+\quad Y=(V,D_1,\dots,D_N).
+$$
+
+Equivalently, $r^*$ is a root of the mean-field function
+$h(r) := \mathbb{E}[H(r,Y)]$, i.e.
+
+$$
+h(r) = \mathbf{0}
+\quad\Longleftrightarrow\quad
+\begin{bmatrix}
+\mathbb{E}[H_1(r,Y)]\\[2pt]
+\vdots\\[2pt]
+\mathbb{E}[H_N(r,Y)]
+\end{bmatrix}
+=
+\begin{bmatrix}
+0\\[2pt]
+\vdots\\[2pt]
+0
+\end{bmatrix}.
+$$
+
+This is a zero of an expectation that can be sampled (one realized
+fill/no-fill per trading period) even though the distribution of
+$(V,D_i)$ is not known.
@@
-$$
-r^{(k+1)} = \Pi_{\mathcal P_N}\Big(r^{(k)} + \gamma_{k+1}H\big(r^{(k)},Y^{(k+1)}\big)\Big), \qquad \gamma_k=\frac{c}{k},
-$$
-
-with $\Pi_{\mathcal P_N}$ the projection onto the simplex. Under
-$\sum\gamma_k=\infty$, $\sum\gamma_k^2<\infty$ and concavity of $\Phi$, $r^{(k)} \xrightarrow{\mathbb{P}-a.s} r^*$
-a.s.
+$$
+r^{(k+1)} = \Pi_{\mathcal{P}_N}\Big(r^{(k)} + \gamma_{k+1} H\big(r^{(k)}, Y^{(k+1)}\big)\Big),
+\qquad \gamma_k = \frac{c}{k},
+$$
+
+where $\Pi_{\mathcal{P}_N}$ is the projection onto the simplex. Under
+the usual Robbins–Monro step-size conditions ($\sum_k \gamma_k = \infty$,
+$\sum_k \gamma_k^2 < \infty$) and concavity of $\Phi$, we have
+$$
+r^{(k)} \xrightarrow{\text{a.s.}} r^*.
+$$
@@
-Calibrated on real Binance market data 
-benchmarked against an oracle with perfect foresight. 
+Calibrated on real Binance market data and benchmarked against an oracle with perfect foresight. 
@@
-*Note: dark pool capacities $D_i$
- are pseudo-real — no public dark-pool liquidity data exists for crypto, so $D_i$ is proxied from correlated reference-asset volume rather than directly observed.*
+*Note: dark pool capacities $D_i$ are pseudo-real — no public dark-pool liquidity data exists for crypto, so $D_i$ is proxied from correlated reference-asset volume rather than directly observed.*
@@
-*Performance ratio $CR^{opti}/CR^{oracle}$ over time — how much of the
-oracle's unattainable cost saving the online algorithm captures.*
+*Performance ratio $CR^{opti}/CR^{oracle}$ over time — how much of the oracle's unattainable cost saving the online algorithm captures.*
@@
-*Evolution of $r^{(k)}$ per pool, converging away from the uniform
-starting allocation toward the learned optimal split.*
+*Evolution of $r^{(k)}$ per pool, converging away from the uniform starting allocation toward the learned optimal split.*
