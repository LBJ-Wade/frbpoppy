"""Do things with frbcat."""
import pandas as pd

from frbcat import TNS as BaseTNS

from frbpoppy.misc import pprint
from frbpoppy.paths import paths
from frbpoppy.population import Population


class TNS(BaseTNS):
    """
    Add frbpoppy functionality to Frbcat.

    Get the pandas dataframe with Frbcat().df
    """

    def __init__(self, frbpoppy=True, **kwargs):
        """Initialize."""
        super(TNS, self).__init__(**kwargs, path=paths.frbcat())
        mute = False
        if 'mute' in kwargs:
            mute = kwargs['mute']

        # Transform the data
        if frbpoppy is True:
            self.frbpoppify()
            self.match_surveys(interrupt=not mute)

        # Just for neating up
        self.df = self.df.sort_values('photometry_date', ascending=False)
        self.df = self.df.reindex(sorted(self.df.columns), axis=1)

    def frbpoppify(self):
        """Prep data for frbpoppy."""
        # Drop confusing columns
        self.df.drop(['ra', 'decl'], axis=1, errors='ignore', inplace=True)

        # Conversion table
        convert = {'galactic_max_dm': 'dm_mw',
                   'burst_width': 'w_eff',
                   'burst_width_err': 'w_eff_err',
                   'burst_bandwidth': 'bw',
                   'ra_frac': 'ra',
                   'dec_frac': 'dec',
                   'flux': 's_peak',
                   'flux_err': 's_peak_err',
                   'gl_frac': 'gl',
                   'gb_frac': 'gb',
                   'host_redshift': 'z',
                   'scattering_time': 't_scat',
                   'scattering_time_err': 't_scat_err',
                   'sampling_time': 't_samp'
                   }

        self.df.rename(columns=convert, inplace=True)

        # Add some extra columns
        self.df['population'] = 'frbcat'

        # Gives somewhat of an idea of the pulse width upon arrival at Earth
        self.df['w_arr'] = (self.df['w_eff']**2 -
                            # self.df['t_dm']**2 -
                            self.df['t_scat']**2 -
                            self.df['t_samp']**2)**0.5

    def match_surveys(self, interrupt=True):
        """Match up frbs with surveys."""
        self.df['survey'] = None

        # Add single survey instruments
        # Bit rough, but will work in a pinch
        def cond(telescope=None, mode=None):
            mask = (self.df.survey.isnull())
            if telescope:
                mask &= (self.df.telescope.str.lower() == telescope.lower())
            if mode:
                mask &= (self.df.telescope_mode.str.lower() == mode.lower())
            return mask

        # Should be accurate up till 2020
        self.df.at[cond('WSRT', 'Apertif'), 'survey'] = 'wsrt-apertif'
        self.df.at[cond('askap', 'Incoherent'), 'survey'] = 'askap-incoh'
        self.df.at[cond('askap', '900MHz'), 'survey'] = 'askap-incoh'
        self.df.at[cond('askap', 'Coherent'), 'survey'] = 'askap-coh'
        self.df.at[cond('askap', 'FlysEye'), 'survey'] = 'askap-fly'
        self.df.at[cond('CHIME'), 'survey'] = 'chime-frb'
        self.df.at[cond('MOST'), 'survey'] = 'utmost-1d'
        self.df.at[cond('VLA'), 'survey'] = 'vla-realfast'
        self.df.at[cond('GMRT'), 'survey'] = 'gmrt'
        self.df.at[cond('SRT'), 'survey'] = 'srt'
        self.df.at[cond('GBT', 'GUPPI'), 'survey'] = 'gbt-guppi'
        self.df.at[cond('EFFELSBERG'), 'survey'] = 'effelsberg'
        self.df.at[cond('OVRO', 'DSA-10'), 'survey'] = 'dsa10'
        self.df.at[cond('FAST'), 'survey'] = 'fast-crafts'
        self.df.at[cond('LPA'), 'survey'] = 'pushchino'
        self.df.at[cond('Arecibo', 'ALFA'), 'survey'] = 'arecibo-palfa'
        self.df.at[cond('Arecibo', 'L-Wide'), 'survey'] = 'arecibo-l-wide'

        # Parkes is more tricky
        c = 'photometry_date'
        pmsurv = cond('Parkes') & (self.df.back_end == 'AFB-MB20')
        self.df.at[pmsurv, 'survey'] = 'parkes-pmsurv'
        htru = cond('Parkes') & (self.df[c].dt.year > 2008)
        htru &= (self.df[c].dt.year < 2015)
        self.df.at[htru, 'survey'] = 'parkes-htru'
        # This means the default survey for Parkes is superb!
        superb = cond('Parkes') & (self.df[c].dt.year >= 2015)
        self.df.at[superb, 'survey'] = 'parkes-superb'

        # Manually add some tricky ones
        self.df.at[self.df.name == 'FRB 20010125A', 'survey'] = 'parkes-swmb'
        self.df.at[self.df.name == 'FRB 20150807A', 'survey'] = 'parkes-party'
        ppta = [171209, 171209, 180309, 180309, 180311, 180311, 180714, 180714]
        for frb in ppta:
            mask = self.df.name == f'FRB 20{frb}A'
            self.df.at[mask, 'survey'] = 'parkes-ppta'

        # Check whether any FRBs have not yet been assigned
        no_surveys = self.df['survey'].isnull()
        if interrupt and any(no_surveys):
            pprint(f'There are {sum(no_surveys)} FRBs with undefined surveys')
            m = 'TNS().match_surveys() in frbpoppy/tns.py should be updated'
            pprint(m)

    def to_pop(self, df=None):
        """
        Convert to a Population object.
        """
        if not isinstance(df, pd.DataFrame):
            df = self.df

        pop = Population()
        pop.name = 'tns'
        frbs = pop.frbs
        frbs.name = df.name.values
        frbs.dm = df.dm.values
        frbs.dm_mw = df.dm_mw.values
        frbs.gl = df.gl.values
        frbs.gb = df.gb.values
        frbs.ra = df.ra.values
        frbs.dec = df.dec.values
        frbs.z = df.z.values
        frbs.t_scat = df.t_scat.values
        frbs.w_eff = df.w_eff.values
        frbs.snr = df.snr.values
        frbs.s_peak = df.s_peak.values
        frbs.fluence = df.fluence.values

        return pop


if __name__ == '__main__':
    tns = TNS()
    import IPython; IPython.embed()
