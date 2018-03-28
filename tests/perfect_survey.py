"""Testing a perfect survey detected everything."""
from frbpoppy.do_populate import generate
from frbpoppy.do_survey import observe
from frbpoppy.do_plot import plot

days = 7
n_per_day = 5000

# Generate FRB population
population = generate(n_per_day*days,
                      days=days,
                      lum_dist_pars=[1e40, 1e50, -1.5],
                      z_max=5.0,
                      pulse=[0.1, 10],
                      repeat=0.0)

# Observe FRB population
result = observe(population, 'PERFECT')

# Plot populations
plot(population, result, mute=False)
