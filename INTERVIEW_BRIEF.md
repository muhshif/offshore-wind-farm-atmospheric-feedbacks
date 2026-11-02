# 3 November 2026 — TU Delft interview quick brief

## 45–60 second explanation (adapt and say in your own words)

"I prepared a small numerical prototype to familiarize myself with wind-farm wake physics before our discussion. It uses an idealized Jensen wake formulation for a synthetic nine-turbine layout. I compared the baseline wind-deficit pattern with sensitivity to rotor spacing, wake-expansion assumptions, and flow direction. It helped me distinguish engineering wake estimates from the bigger atmospheric question in this project. The next step, which directly matches the position, would be controlled high-resolution atmospheric simulations with and without wind-farm effects, analyzing boundary-layer dynamics, moisture transport, cloud response, and precipitation with observational evaluation. My previous experience with high-resolution regional climate modelling and precipitation diagnostics would be especially transferable to that next stage."

Do not imply this simple prototype models precipitation, turbulence, stable/unstable boundary layers, ocean coupling, or validates WRF/ICON results.

## What you can explain on screen

1. Figure 01: deficit localizes downstream, expands with distance, recovers as it spreads.
2. Figure 02: larger `k` causes faster recovery within the Jensen formula. Larger spacing generally reduces interactions in aligned conditions. `k` is **not** a stability simulation.
3. Figure 03: wake overlap depends on orientation of turbines relative to the wind.

## Key physics to discuss

- Momentum extraction creates wakes; turbines can also perturb mixing and turbulence.
- Atmospheric stability and turbulence control wake persistence, especially over sea.
- Wake-induced wind, turbulence, and thermal structure changes may influence moist processes, but the sign and statistical significance of precipitation response are **not predetermined**.
- Use matched **no-farm vs farm** model experiments under different weather regimes, plus sensitivity/ensemble tests.
- Candidate diagnostics: hub-height winds, vertical profiles, TKE, boundary-layer height, moisture flux convergence, omega/w, relative humidity, cloud water, rain rate, and accumulated precipitation.
- A simplified vertically integrated atmospheric moisture budget is \(\partial_t PW + \nabla_h\cdot IVT = E-P\), where PW is precipitable water, IVT is vertically integrated horizontal water-vapour transport, E is surface evaporation, and P is precipitation, provided the budget includes the appropriate processes and definitions. Precipitation cannot be inferred from wind deficits alone.

## Questions worth asking Dr Porchetta

- "Is the intended modelling framework WRF with an existing wind-farm parameterization, or is the choice of model still open?"
- "Are you prioritizing convective or stratiform precipitation regimes, and do you already have observed events selected?"
- "Which uncertainty sources are most important early on: wind-farm drag/TKE parameterization, atmospheric resolution, or baseline precipitation variability?"

## If they ask what you did not do

"I did not conduct mesoscale feedback simulations or infer precipitation changes. This was an intentionally limited demonstration of first-order wake behaviour, to prepare for a more rigorous paired atmospheric modelling design."
