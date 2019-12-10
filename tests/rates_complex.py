"""Try creating the most realistic event rates."""
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

from frbpoppy import (CosmicPopulation, Survey, LargePopulation, pprint,
                      unpickle)

from convenience import plot_aa_style, rel_path

REMAKE = True
ALPHAS = np.around(np.linspace(-0.2, -2.5, 7), decimals=2)
SURVEYS = ('palfa', 'htru', 'askap-fly')
SIZE = 1e5


def complex_rates(remake=REMAKE, alphas=ALPHAS, size=SIZE, surveys=SURVEYS):
    """Calculate expected rates for a complex populations."""
    rates = defaultdict(list)

    # Don't always regenerate a population
    if remake is False:
        for alpha in alphas:
            for s in surveys:
                surv_rates = unpickle(f'complex_alpha_{alpha}_{s}').rates()
                pprint(f'Alpha:{alpha:.2}, Survey: {s}, Det: {surv_rates.det}')
                rate = (surv_rates.det / surv_rates.days)
                rates[s].append(rate)
    else:
        pops = []
        for alpha in alphas:
            pop = CosmicPopulation.complex(size)
            pop.alpha = alpha
            pop.name = f'complex_alpha_{alpha}'
            pops.append(pop)

            # Set up surveys
            ss = []
            for s in surveys:
                survey = Survey(name=s, beam_pattern='airy',
                                n_sidelobes=1)
                ss.append(survey)

            surv_pops = LargePopulation(pop, *ss).pops

            for i, s in enumerate(surveys):
                surv_rates = surv_pops[i].rates()
                pprint(f'Alpha:{alpha:.2}, Survey: {s}, Det: {surv_rates.det}')
                rate = (surv_rates.det / surv_rates.days)
                rates[s].append(rate)

    # Scale rates to HTRU
    for s in surveys:
        if s != 'htru':
            norm = []
            for i, r in enumerate(rates[s]):
                norm.append(r/rates['htru'][i])
            rates[s] = norm
    rates['htru'] = [r/r for r in rates['htru']]

    return rates


def main():
    """Plot expected complex rates."""
    plot_aa_style()

    rates = complex_rates()
    for surv in rates:
        rate = rates[surv]
        plt.plot(ALPHAS, rate, label=surv)

    plt.xlabel(r'$\alpha_{\text{in}}$')
    plt.ylabel(r'Events / htru')
    plt.yscale('log')
    plt.xlim((min(ALPHAS), max(ALPHAS)))
    plt.legend()
    plt.gca().invert_xaxis()
    plt.tight_layout()
    plt.grid()
    plt.savefig(rel_path('./plots/complex_rates.pdf'))


if __name__ == '__main__':
    main()
