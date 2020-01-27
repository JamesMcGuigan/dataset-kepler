import re

import pandas as pd

# Kepler Dataset Columns are subdivided into categories
# - Source: https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html
# - NOTE: columns with ONLY NaN:     ['koi_longp', 'koi_ingress', 'koi_model_dof', 'koi_model_chisq', 'koi_sage']
# - NOTE: columns with SINGLE value: ['koi_vet_stat', 'koi_vet_date', 'koi_disp_prov', 'koi_eccen', 'koi_limbdark_mod', 'koi_ldm_coeff4', 'koi_ldm_coeff3', 'koi_trans_mod']
# - NOTE: columns with SINGLE value (after cleanup): [ koi_parm_prov ]
koi_columns = {
    'id':          [
        'kepid', 'kepoi_star', 'kepoi_name',  # NOTE: kepoi_star added by PreProcessing
    ],
    'archive':     [
        'kepler_name', 'koi_disposition',
        # 'koi_vet_stat', 'koi_vet_date'          # Ignore: Single Value ONLY
    ],
    'disposition': [
        'koi_pdisposition', 'koi_score',
        'koi_fpflag_nt', 'koi_fpflag_ss', 'koi_fpflag_co', 'koi_fpflag_ec',
        # 'koi_disp_prov',                        # Ignore: Single Value ONLY
        'koi_comment'
    ],
    'transit': [
        'koi_period', 'koi_time0bk', 'koi_time0',
        # 'koi_eccen',                            # Ignore: Single Value ONLY
        # 'koi_longp',                            # Ignore: only contains NaN
        'koi_impact', 'koi_duration',
        # 'koi_ingress',                          # Ignore: only contains NaN
        'koi_depth', 'koi_ror', 'koi_srho', 'koi_fittype', 'koi_prad', 'koi_sma', 'koi_incl', 'koi_teq', 'koi_insol',
        'koi_dor',
        # 'koi_limbdark_mod',                     # Ignore: only contains NaN
        'koi_ldm_coeff1', 'koi_ldm_coeff2',
        # 'koi_ldm_coeff3', 'koi_ldm_coeff4',     # Ignore: Single Value ONLY
        # 'koi_parm_prov'                         # Ignore: Single Value ONLY
    ],
    'TCE': [
        'koi_max_sngle_ev', 'koi_max_mult_ev', 'koi_model_snr', 'koi_count', 'koi_num_transits', 'koi_tce_plnt_num',
        'koi_tce_delivname', 'koi_quarters',
        # 'koi_trans_mod',                        # Ignore: Single Value ONLY
        # 'koi_model_dof', 'koi_model_chisq',     # Ignore: only contains NaN
        # 'koi_datalink_dvr', 'koi_datalink_dvs'  # Ignore: URL ids
    ],
    'stellar': [
        'koi_steff', 'koi_slogg', 'koi_smet', 'koi_srad', 'koi_smass',
        # 'koi_sage',  # Ignore: only contains NaN
        'koi_sparprov',
    ],
    'KIC': [
        'ra', 'dec', 'koi_kepmag', 'koi_gmag', 'koi_rmag', 'koi_imag', 'koi_zmag', 'koi_jmag', 'koi_hmag', 'koi_kmag'
    ],
    'pixels': [
        'koi_fwm_sra', 'koi_fwm_sdec', 'koi_fwm_srao', 'koi_fwm_sdeco', 'koi_fwm_prao', 'koi_fwm_pdeco', 'koi_fwm_stat_sig',
        'koi_dicco_mra', 'koi_dicco_mdec', 'koi_dicco_msky', 'koi_dikco_mra', 'koi_dikco_mdec', 'koi_dikco_msky'
    ]
}
koi_column_types = {
    'category': [
        'kepoi_star',
        'koi_disposition', 'koi_vet_stat',
        'koi_pdisposition', 'koi_disp_prov',
        'koi_fpflag_nt', 'koi_fpflag_ss', 'koi_fpflag_co', 'koi_fpflag_ec',
        'koi_quarters',
        'koi_sparprov',
        'koi_fittype',
    ],
    'datetime64': [
        'koi_vet_date',
    ],
    'uint8': [
        'koi_fpflag_nt',
        'koi_fpflag_ss',
        'koi_fpflag_co',
        'koi_fpflag_ec',
    ]
}
koi_fillna = {
    # 'kepler_name': '',
    'koi_score':   0,
    'koi_comment': '',
    'koi_tce_delivname': '',
}
koi_mappings = {
    'koi_fpflag_nt':     lambda num: int(not not num),                            # remove: 465
    'koi_parm_prov':     lambda str: re.sub(r'_(q|dr)\d+|(q|dr)\d+_', '', str),   # cleanup: ['q1_q17_dr25_koi', 'q1_q16_koi', 'q1_q17_dr24_koi']
    'koi_tce_delivname': lambda str: re.sub(r'_(q|dr)\d+|(q|dr)\d+_', '', str),   #
    'koi_disp_prov':     lambda str: re.sub(r'_(q|dr)\d+|(q|dr)\d+_', '', str),   # cleanup: q1_q17_dr25_sup_koi
    'koi_sparprov':      lambda str: re.sub(r'_(q|dr)\d+|(q|dr)\d+_', '', str),   # cleanup: [q1_q17_dr25_stellar, stellar_q1_q16, NaN, Solar, stellar_q1_q17]
}


# Load CSV file
koi = {}
koi['all'] = pd.read_csv('./data/kepler_koi.csv',
                         comment='#',
                         parse_dates=koi_column_types['datetime64'],
                         infer_datetime_format=True)
koi['all'].set_index('kepoi_name', inplace=True, drop=False)


# Injected Fields
koi['all'].insert( koi['all'].columns.get_loc('kepoi_name'), 'kepoi_star', value=None)
koi['all']['kepoi_star'] = koi['all']['kepoi_name'].apply(lambda str: re.sub(r'\..*$', '', str))


# Convert Columns dtypes - before postprocessing
for category, columns in koi_column_types.items():
    for key in columns:
        koi['all'][key] = koi['all'][key].astype(category)


# Fill NaN
for key, value in koi_fillna.items():
    koi['all'][key].fillna( value, inplace=True )


# Mappings - clean up erroneous data
for key, func in koi_mappings.items():
    if key in koi['all'].columns:
        koi['all'][key] = koi['all'][key].apply( func )


# Convert Columns dtypes - after postprocessing
for category, columns in koi_column_types.items():
    for key in columns:
        koi['all'][key] = koi['all'][key].astype(category)


# Export Datastructure
for key, columns in koi_columns.items():
    # columns = ['kepoi_name'] + columns
    koi[key] = koi['all'][ columns ]
    pass