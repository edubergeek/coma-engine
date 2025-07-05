import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from astropy.time import Time

import pandas as pd

from pyasassn.client import SkyPatrolClient

DEBUG=True

client = SkyPatrolClient()
if DEBUG:
  client.random_sample(100, catalog="comets")

#comet_name = 'P/2016 A7'
#comet_name = '2P/EnckeMPEC2023'
#comet_name = 'C/2022 A2'
#comet_name = 'C/2022 P1'
#comet_name = 'C/2022 E3'
#comet_name = 'C/2023 E1'
#comet_name = 'C/2022 A2'
#comet_name = 'C/2021 X1'
comet_name = 'C/2021 T4'
#comet_name = 'C/2020 V2'
#comet_name = 'C/2019 U5'
#comet_name = 'C/2021 X1'
#comet_name = 'C/2021 T4'
#comet_name = 'C/2019 T2'
#comet_name = 'C/2017 K2'
#comet_name = '121P'
#comet_name = '12P'
#comet_name = '2P'

comet_regexp = comet_name.replace(' ','') + '%'
query = """
SELECT mpc_entry FROM comets WHERE mpc_entry LIKE '%s'
"""
query = query %(comet_regexp)
if DEBUG:
  print(query)

lcs = client.adql_query(query, download=True, threads=8)

j = lcs.data['jd']
m = lcs.data['mag']
t_jd = Time(j, format='jd')
t_utc = t_jd.to_value('iso', 'date_hms')  
t_ymd = t_jd.to_value('datetime64', 'date')  
t_mjd = t_jd.to_value('mjd')  
lcs.data['utc'] = t_utc
lcs.data['date'] = t_ymd
lcs.data['mjd'] = t_mjd
date_form = DateFormatter("%y-%m")

if DEBUG:
  print(lcs.data['mjd'])

filtered = lcs.data[lcs.data['mag_err'] < 0.5] 

mpc_comet = comet_name
mpc_start_ts = filtered.describe()['date']['min']
td = pd.Timedelta(1, "min")
mpc_end_ts = mpc_start_ts + td
mpc_start = mpc_start_ts.strftime('%Y-%m-%dT%H:%M:%S')
mpc_end = mpc_end_ts.strftime('%Y-%m-%dT%H:%M:%S')
filtered.sort_values(by='mjd', inplace = True)
if DEBUG:
  print(mpc_start_ts)
  print(mpc_start)
  print(mpc_end)
  print(mpc_end_ts)
  print(filtered['mjd'])

assdf_g = filtered[filtered['phot_filter']=='g']
assdf_g['object'] = assdf_g['mpc_entry']
assdf_g['telescope'] = 'ASAS-SN'
assdf_g['filter'] = 'G_ASASSN'
assdf_g['aperture'] = 16
assdf_g['zp_mag'] = assdf_g['limit']
assdf_g['zp_mag_err'] = float('nan')	
assdf_g['phase_angle'] = float('nan')	
assdf_g['heliocentric_au'] = float('nan')	
assdf_g['geocentric_au'] = float('nan')	
assdf_g['true_anomaly'] = float('nan')
assdf_g = assdf_g.drop(['mpc_entry', 'limit', 'jd', 'flux', 'flux_err', 'fwhm', 'image_id','camera','quality','phot_filter'], axis=1)
assdf_g = assdf_g.drop(['flux_3','flux_err_3','mag_3','mag_err_3','limit_3'], axis=1)
assdf_g = assdf_g.drop(['flux_4','flux_err_4','mag_4','mag_err_4','limit_4'], axis=1)
assdf_g = assdf_g.drop(['flux_5','flux_err_5','mag_5','mag_err_5','limit_5'], axis=1)
assdf_g = assdf_g.drop(['flux_6','flux_err_6','mag_6','mag_err_6','limit_6'], axis=1)
assdf_g = assdf_g.drop(['flux_7','flux_err_7','mag_7','mag_err_7','limit_7'], axis=1)
assdf_g = assdf_g.drop(['flux_8','flux_err_8','mag_8','mag_err_8','limit_8'], axis=1)

file_name = comet_name.replace('/','-').replace(' ','_')
file_name = 'ASASSN_'+file_name+'.csv'

export_col = [
  'object',
  'telescope',
  'filter',
  'aperture',
  'utc',
  'mjd',
  'mag',
  'mag_err',
  'zp_mag',
  'zp_mag_err',
  'phase_angle',
  'heliocentric_au',
  'true_anomaly',
  'geocentric_au'
]

assdf_g.to_csv(file_name, index=False, columns = export_col)

