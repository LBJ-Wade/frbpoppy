"""Plot intensity profile of theoretical beam patterns."""
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import binned_statistic as bstat

from frbpoppy.survey import Survey

from convenience import plot_aa_style, rel_path

OBSERVATORIES = [('parkes', 'htru'),
                 ('apertif', 'apertif'),
                 ('chime', 'chime')]

n = int(1e6)

plot_aa_style()

for obs in OBSERVATORIES:

    survey = obs[1]
    pattern = obs[0]

    s = Survey(survey)
    s.set_beam(model=pattern)
    int_pro, offset = s.calc_beam(shape=n)

    # Sort the values
    sorted_int = np.argsort(offset)
    int_pro = int_pro[sorted_int]
    offset = offset[sorted_int]

    bins = 1e2

    bin_means, bin_edges, bin_numbers = bstat(offset,
                                              int_pro,
                                              statistic='mean',
                                              bins=bins)

    bin_mins, _, _ = bstat(offset, int_pro, statistic='min', bins=bins)
    bin_maxs, _, _ = bstat(offset, int_pro, statistic='max', bins=bins)

    center = (bin_edges[:-1] + bin_edges[1:]) / 2

    plt.plot(center, bin_means, label=pattern)
    plt.fill_between(center, bin_mins, bin_maxs, alpha=0.2)


plt.xlabel(r'Offset ($^{\circ}$)')
plt.ylabel('Intensity Profile')
plt.xlim(0, 5)
plt.yscale('log')
plt.legend()
plt.tight_layout()
plt.savefig(rel_path('plots/int_pro_surveys.pdf'))
