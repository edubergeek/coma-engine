import requests
import logging
import json
import csv
import time
from itertools import chain
from os.path import exists
from os.path import basename
from os.path import dirname
from astropy.time import Time
import argparse

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")

parser = argparse.ArgumentParser()
parser.add_argument("fits", help="FITS file to ingest")
parser.add_argument("object", help="central object in FITS file")
parser.add_argument("-i", "--id", type=int, default=1, help="image ID")
parser.add_argument("-m", "--method", default='TheAperturePhotometry', help="aperture photometry method to use")
parser.add_argument("-a", "--aperture", default='[5,10]', help="aperture list, e.g. [5,10]")
parser.add_argument("-v", "--verbosity", action="count", default=0)
args = parser.parse_args()

if args.verbosity > 0:
  requests_log.propagate = True
  if args.verbosity > 4:
    requests_log.setLevel(logging.DEBUG)
  elif args.verbosity > 3:
    requests_log.setLevel(logging.INFO)
  elif args.verbosity > 2:
    requests_log.setLevel(logging.WARN)
  elif args.verbosity > 1:
    requests_log.setLevel(logging.INFO)
  else:
    requests_log.setLevel(logging.CRITICAL)
else:
  requests_log.propagate = False
  requests_log.setLevel(logging.NOTSET)

IMGFILE='image.csv'
img_header = False
if exists(IMGFILE):
  img_file = open(IMGFILE, 'a')
else:
  img_file = open(IMGFILE, 'w')
  img_header = True

# create the csv writer object
img_writer = csv.writer(img_file)

CALFILE='calibration.csv'
cal_header = False
if exists(CALFILE):
  cal_file = open(CALFILE, 'a')
else:
  cal_file = open(CALFILE, 'w')
  cal_header = True

# create the csv writer object
cal_writer = csv.writer(cal_file)
 
PHOTFILE='photometry.csv'
phot_header = False
if exists(PHOTFILE):
  phot_file = open(PHOTFILE, 'a')
else:
  phot_file = open(PHOTFILE, 'w')
  phot_header = True

# create the csv writer object
phot_writer = csv.writer(phot_file)
 

##################################################

FITS=args.fits
OBJECT=args.object
ARGS={
  'fits_file': FITS
}


################
def LookupTelescope(telescope):
  if telescope.startswith('uh88'):
    return 1
  if telescope.startswith('cfht'):
    return 2
  if telescope.startswith('ps1'):
    return 3
  return 0

def LookupInstrument(instrument):
  if instrument.startswith('uh88-tektronix-2048-ccd'):
    return 1
  elif instrument.startswith('cfht-megacam-one-chip'):
    return 2
  elif instrument.startswith('ps1-chip-stamp'):
    return 3
  return 0

def MJDtoDate(mjd):
  t = Time(mjd, format='mjd', scale='utc')
  timestr = t.strftime('%Y-%m-%d')
  return timestr

def LookupObject(object):
  if object == 'C/2017 K2':
    return 1049
  if object == '97ba6 R600':
    return 700
  return 0

def FilePath(fullpath):
  path_name = dirname(fullpath)
  return path_name

def FileName(fullpath):
  file_name = basename(fullpath)
  return file_name

def ImageRow(id, desc, objid):
  row = [id]
  row.append(desc['OBSCODE'])
  row.append(LookupTelescope(desc['INSTRUMENT']))
  row.append(LookupInstrument(desc['INSTRUMENT']))
  row.append('COMA')
  row.append(MJDtoDate(desc['MJD-MID']))
  row.append(objid)
  row.append(desc['OBSTYPE'])
  row.append(desc['MJD-MID'])
  row.append(desc['EXPTIME'])
  row.append(desc['FILTER'])
  row.append(FilePath(desc['FITS-FILE']))
  row.append(FileName(desc['FITS-FILE']))
  return row

################
# First describe FITS file
API='https://coma.ifa.hawaii.edu/api/fits/describe'
response = [requests.post(API, data=ARGS, verify=False)]
cursor=0
print("Status code: ", response[cursor].status_code)
if response[cursor].status_code <= 202:
  data = response[cursor].json()
  if data['status'] == 'success':
    guid = data['task']['id']

data = {}
while cursor < 10 and 'data' not in data:
  API='https://coma.ifa.hawaii.edu/api/task/result/%s' %(guid)
  response.append(requests.get(API, verify=False))
  cursor+=1
  print("Status code: ", response[cursor].status_code)
  if response[cursor].status_code <= 202:
    data = response[cursor].json()
    if 'data' not in data:
      time.sleep(1)

description = json.loads(data['data'])
print(description)

del description['TYPE']

# Counter variable used for writing
# headers to the CSV file
if img_header:
  header = [
    'imageid',
    'obscode',
    'telescopeid',
    'instrumentid',
    'imagestr',
    'imagedate',
    'objectid',
    'imagetype',
    'mjd_mid',
    'exptime',
    'filter',
    'filepath',
    'filename'
  ]
  img_writer.writerow(header)
  img_header = False

objid = LookupObject(description['OBJECT'])
if objid:
  img_writer.writerow(ImageRow(args.id, description, objid))

def CalibrationRow(id, desc, calib):
  row = [id]
  # assume calibrationid == imageid for now
  row.append(id)
  row.append(LookupInstrument(desc['INSTRUMENT']))
  row.append(desc['MJD-MID'])
  row.append(calib['PHOT-CALIB-INFO']['FILTER'])
  row.append(calib['PHOT-CALIB-INFO']['CATALOG'])
  row.append(calib['PHOT-CALIB-INFO']['NSTARS'])
  row.append(calib['PHOT-CALIB-INFO']['ZPMAG'])
  row.append(calib['PHOT-CALIB-INFO']['ZPMAGERR'])
  row.append(calib['PHOT-CALIB-INFO']['ZPINSTMAG'])
  row.append(calib['PHOT-CALIB-INFO']['ZPINSTMAGERR'])
  row.append(calib['QUALITIES-INFO']['PIXEL-SCALE'])
  row.append(calib['QUALITIES-INFO']['PSF-NOBJ'])
  row.append(calib['QUALITIES-INFO']['PSF-FWHM-ARCSEC'])
  row.append(calib['QUALITIES-INFO']['PSF-MAJOR-AXIS-ARCSEC'])
  row.append(calib['QUALITIES-INFO']['PSF-MINOR-AXIS-ARCSEC'])
  row.append(calib['QUALITIES-INFO']['PSF-PA-PIX'])
  row.append(calib['QUALITIES-INFO']['PSF-PA-WORLD'])
  row.append(calib['QUALITIES-INFO']['MAG-5-SIGMA'])
  row.append(calib['QUALITIES-INFO']['MAG-10-SIGMA'])
  row.append(calib['QUALITIES-INFO']['NDENSITY-MAG-20'])
  row.append(calib['QUALITIES-INFO']['NDENSITY-5-SIGMA'])
  row.append(calib['QUALITIES-INFO']['SKY-BACKD-ADU-PIX'])
  row.append(calib['QUALITIES-INFO']['SKY-BACKD-PHOTONS-PIX'])
  row.append(calib['QUALITIES-INFO']['SKY-BACKD-ADU-ARCSEC2'])
  row.append(calib['QUALITIES-INFO']['SKY-BACKD-PHOTONS-ARCSEC2'])
  row.append(calib['QUALITIES-INFO']['SKY-BACKD-MAG-ARCSEC2'])

  return row

################
# Next calibrate FITS file
API='https://coma.ifa.hawaii.edu/api/fits/calibrate'
response = [requests.post(API, data=ARGS, verify=False)]
cursor=0
print("Status code: ", response[cursor].status_code)
if response[cursor].status_code <= 202:
  data = response[cursor].json()
  if data['status'] == 'success':
    guid = data['task']['id']

data = {}
while cursor < 60 and 'data' not in data:
  API='https://coma.ifa.hawaii.edu/api/task/result/%s' %(guid)
  response.append(requests.get(API, verify=False))
  cursor+=1
  print("Status code: ", response[cursor].status_code)
  if response[cursor].status_code <= 202:
    data = response[cursor].json()
    if 'data' not in data:
      time.sleep(1)

calibration = json.loads(data['data'])
print(calibration)
#qualities = calibration['QUALITIES-INFO']
#wcs = calibration['WCS-INFO']
#wcscal = wcs['WCS']
#del wcs['WCS']
#photcalib = calibration['PHOT-CALIB-INFO']

#del calibration['TYPE']

if cal_header:
  header = [
    'imageid',
    'calibrationid',
    'instrumentid',
    'mjd_middle',
    'filter',
    'catalog',
    'nstars',
    'zpmag',
    'zpmag_error',
    #'extinction',
    #'extinction_error',
    #'colorterm',
    #'colorterm_error',
    'zpinstmag',
    'zpinstmag_err',
    'pixel_scale',
    'psf_nobj',
    'psf_fwhm_arcsec',
    'psf_major_axis_arcsec',
    'psf_minor_axis_arcsec',
    'psf_pa_pix',
    'psf_pa_world',
    'limit_mag_5_sigma',
    'limit_mag_10_sigma',
    'ndensity_mag_20',
    'ndensity_5_sigma',
    'sky_backd_adu_pix',
    'sky_backd_photons_pix',
    'sky_backd_adu_arcsec2',
    'sky_backd_photons_arcsec2',
    'sky_backd_mag_arcsec2',
  ]
  cal_writer.writerow(header)
  cal_header = False

print(calibration.keys())
if calibration['TYPE'] == 'ERROR':
  print("%s %s: %s" % (calibration['TYPE'], calibration['ERROR'], calibration['DESCRIPTION'])) 
else:
  cal_writer.writerow(CalibrationRow(args.id, description, calibration))

def PhotometryRow(id, desc, photo):
  row = []
  # this should match the number of aperture sizes we supplied, in this case 2 ([5,10])
  apertures = len(photo['PHOTOMETRY-RESULTS'][0]['APERTURES'])
  for a in range(apertures):
    r = [((id-182)*2)-1+a]
    r.append(id)
    r.append(LookupObject(desc['OBJECT']))
    # assume calibrationid == imageid for now
    r.append(id)
    r.append(photo['PHOTOMETRY-RESULTS'][0]['ID'])
    r.append(photo['PHOTOMETRY-RESULTS'][0]['APERTURES'][a])
    r.append(photo['FILTER'])
    r.append(photo['XPIX-OBJECT-INPUT'])
    r.append(photo['YPIX-OBJECT-INPUT'])
    r.append(photo['DEC-OBJECT-INPUT'])
    r.append(photo['RA-OBJECT-INPUT'])
    r.append(photo['ZPMAG'])
    r.append(photo['ZPMAGERR'])
    # the 0 index is for methods, in this case we only supplied 1 method
    r.append(photo['PHOTOMETRY-RESULTS'][0]['BACKGROUND-RADII'][a])
    r.append(photo['PHOTOMETRY-RESULTS'][0]['BACKGROUND-FLUX-ADU/ARCSEC2'][a])
    r.append(photo['PHOTOMETRY-RESULTS'][0]['BACKGROUND-FLUX-PHOTONS/ARCSEC2'][a])
    r.append(photo['PHOTOMETRY-RESULTS'][0]['APERTURE-MAGS'][a])
    r.append(photo['PHOTOMETRY-RESULTS'][0]['APERTURE-MAG-ERRORS'][a])
    row.append(r)
  return row

################
# Next do photometry on FITS file
API='https://coma.ifa.hawaii.edu/api/fits/photometry'
ARGS['method'] = args.method
ARGS['aperture'] = args.aperture
ARGS['object'] = OBJECT
response = [requests.post(API, data=ARGS, verify=False)]
cursor=0
print("Status code: ", response[cursor].status_code)
if response[cursor].status_code <= 202:
  data = response[cursor].json()
  if data['status'] == 'success':
    guid = data['task']['id']

data = {}
while cursor < 100 and 'data' not in data:
  API='https://coma.ifa.hawaii.edu/api/task/result/%s' %(guid)
  response.append(requests.get(API, verify=False))
  cursor+=1
  print("Status code: ", response[cursor].status_code)
  if response[cursor].status_code <= 202:
    data = response[cursor].json()
    if 'data' not in data:
      time.sleep(1)

photometry = json.loads(data['data'])
print(photometry)

if phot_header:
  header = [
    'photid',
    'imageid',
    'objectid',
    'calibrationid',
    'phot_type',
    'aperture',
    'filter',
    'xpix-object',
    'ypix-object',
    'dec-object',
    'ra-object',
    'zpmag',
    'zpmagerr',
    'aperture_backd_radii',
    'backd_flux_adu_persec',
    'backd_flux_photon_persec',
    'mag',
    'mag_err',
  ]
  phot_writer.writerow(header)
  phot_header = False

if photometry['TYPE'] == 'ERROR':
  print("%s %s: %s" % (photometry['TYPE'], photometry['ERROR'], photometry['DESCRIPTION'])) 
else:
  rows = PhotometryRow(args.id, description, photometry)
  for row in rows:
    phot_writer.writerow(row)

###############################################

img_file.close()
cal_file.close()
phot_file.close()
