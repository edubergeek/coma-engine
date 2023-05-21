# COMAJSONServer.py

# encapsulate Jan Kleyna's COMA JSON API for Python

import os
import json
import mariadb
import logging

class COMADB:
  # default constructor

  def __init__(self):
    self.debug=False
    self.config = {
      'host': os.getenv('COMA_DB_HOST', default="172.17.0.1"),
      'port': int(os.getenv('COMA_DB_PORT', default="0")),
      'user': os.getenv('COMA_DB_USER', default="nobody"),
      'password': os.getenv('COMA_DB_PASS', default=""),
      'database': os.getenv('COMA_DB_NAME', default="coma"),
      'autocommit': True,
    }
    if self.config["port"] > 0:
      logging.basicConfig(filename='/usr/src/app/logs/coma.log', filemode='a', encoding='utf-8', level=logging.DEBUG)
      self.OpenDB()


  def __del__(self):
    self.CloseDB()

  def OpenDB(self, port=0):
    # connection for MariaDB
    #print(self.config)
    logging.debug("OpenDB: " + str(self.config))
    self.conn = mariadb.connect(**self.config)
    #print(self.conn)
    #self.conn = None

  def CloseDB(self):
    self.conn = None

  def Run(self, dmlSQL, dmlData = None):
    # create a connection cursor
    self.cursor = self.conn.cursor()
    # execute a SQL statement
    # TODO check for sql injection
    logging.debug(dmlSQL)
    return self.cursor.execute(dmlSQL, dmlData)
 
  def GetResultHeaders(self):
    # serialize results into JSON
    self.column_headers=[x[0] for x in self.cursor.description]
    return self.column_headers
 
  def GetResults(self):
    # fetch all rows and return as list of dicts
    rv = self.cursor.fetchall()
    self.column_values = []
    # strip unwanted characters from results
    for results in rv:
      row = []
      for r in results:
        if isinstance(r, str):
          row.append(r.replace('\r',""))
        else:
          row.append(r)
      self.column_values.append(row)
      #self.column_values.append(dict(zip(self.column_headers,result)))
    return self.column_values
 
  def InsertRow(self, insertStr, values):
    logging.debug(insertStr)
    try:
      # create a connection cursor
      self.cursor = self.conn.cursor()
      ret = self.cursor.execute(insertStr, values)
      #self.cursor.commit()
    except mariadb.Error as e:
      logging.debug(f"Error adding entry to database: {e}")
      ret = ""
    return ret

  # a subroutine to get the last valid ID and increment by one
  def GetNextID(self, tableName, idName):
    idQuery = "SELECT max(%s) as 'nextid' from %s;" % (idName, tableName)
    self.Run(idQuery)
    self.GetResultHeaders()
    row = self.GetResults()
    return int(row['nextid']) + 1

  def InsertObservatory(self, observatoryName, observatoryCode):
    # create a connection cursor
    tableStr = 'observatories'
    idStr = 'observatoryid'
    nextID = self.GetNextID(tableStr, idStr)
    values = (nextID, observatoryName, observatoryCode)
    insert = "INSERT INTO %s (%s, obsname, obscode) VALUES (?, ?, ?)" % (tableStr, idStr)
    return self.InsertRow(insert, values)

  def InsertTelescope(self, telescopeName):
    # create a connection cursor
    tableStr = 'telescopes'
    idStr = 'telescopeid'
    nextID = self.GetNextID(tableStr, idStr)
    values = (nextID, telescopeName)
    insert = "INSERT INTO %s (%s, telescopename) VALUES (?, ?)" % (tableStr, idStr)
    return self.InsertRow(insert, values)

  def InsertInstrument(self, collection_lid, instrumentName):
    # create a connection cursor
    tableStr = 'instruments'
    idStr = 'instrumentid'
    nextID = self.GetNextID(tableStr, idStr)
    values = (nextID, collection_lid, instrumentName)
    insert = "INSERT INTO %s (%s, acronym, tinstrumentname) VALUES (?, ?, ?)" % (tableStr, idStr)
    return self.InsertRow(insert, values)

  def InsertObject(self, bundle_lid, objectType, objectName, sbnName):
    # create a connection cursor
    tableStr = 'objects'
    idStr = 'objectid'
    nextID = self.GetNextID(tableStr, idStr)
    #values = (nextID, bundle_lid, objectType, objectName, sbnName)
    #insert = "INSERT INTO %s (%s, pds4_lid, objecttype_coma, defaultobjectname, sbn_targetname) VALUES (?, ?, ?, ?, ?)" % (tableStr, idStr)
    values = (nextID, bundle_lid, objectType, objectName)
    insert = "INSERT INTO %s (%s, pds4_lid, objecttype_coma, defaultobjectname) VALUES (?, ?, ?, ?)" % (tableStr, idStr)
    return self.InsertRow(insert, values)

  def InsertEphemeris(self, objectID, jd, ctDatetime, trueAnomaly, hcDist):
    # create a connection cursor
    tableStr = 'objects'
    idStr = 'objectid'
    nextID = self.GetNextID(tableStr, idStr)
    values = (nextID, objectID, jd, ctDatetime, trueAnomaly, hcDist)
    insert = "INSERT INTO %s (%s, targetid, jd, ctdatetime, trueanomaly, hcdist) VALUES (?, ?, ?, ?, ?)" % (tableStr, idStr)
    return self.InsertRow(insert, values)

  def InsertImage(self, imageType, bundle_lid, collection_lid, mjd, expTime, filterCode, filePath, fileName):
    # create a connection cursor
    tableStr = 'images'
    idStr = 'imageid'
    nextID = self.GetNextID(tableStr, idStr)
    objectID = GetObjectID(bundle_lid)
    instrumentID = GetInstrumentID(collection_lid)
    imageTypeID = GetImageTypeID(imageType)
    filterID = GetFilterID(filterCode)
    values = (nextID,  imageTypeID, objectID, instrumentID, filterID, mjd, expTime, filePath, fileName)
    insert = "INSERT INTO %s (%s, imagetypeid, objectid, instrumentid, filterid, mjd_mid, exptime, filepath, filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)" % (tableStr, idStr)
    return self.InsertRow(insert, values)

# imageid       | int(11)       | NO   | PRI | NULL    |       |
# imagedate     | date          | YES  |     | NULL    |       |
# object        | char(10)      | YES  |     | NULL    |       |
# imagetype     | char(40)      | YES  |     | NULL    |       |
# jd            | decimal(15,7) | YES  |     | NULL    |       |
# exptime       | float         | YES  |     | NULL    |       |
# filter        | varchar(2)    | YES  |     | NULL    |       |
# filepath      | varchar(60)   | YES  |     | NULL    |       |
# filename      | varchar(40)   | YES  |     | NULL    |       |

  #a subroutine to get the image type id from an image type
  def GetImageTypeID(self, imageType):
    tableStr = 'imagetypes'
    idStr = 'imagetypeid'
    #split fits_file into path and file name parts
    queryStr = "SELECT %s from %s WHERE imagetypename = '%s';" % (idStr, tableStr, imageType)
    self.Run(queryStr)
    self.GetResultHeaders()
    row = self.GetResults()
    return int(row[idStr])

  #a subroutine to get the filter id from a filter code
  def GetFilterID(self, filterCode):
    tableStr = 'filters'
    idStr = 'filterid'
    #split fits_file into path and file name parts
    queryStr = "SELECT %s from %s WHERE filter_common_name = '%s';" % (idStr, filterCode)
    self.Run(queryStr)
    self.GetResultHeaders()
    row = self.GetResults()
    return int(row[idStr])

  # a subroutine to get the image id from a FITS filename
  def GetImageID(self, fits_file):
    tableStr = 'images'
    idStr = 'imageid'
    #split fits_file into path and file name parts
    queryStr = "SELECT %s from %s WHERE filepath = '%s' AND filename = '%s';" % (idStr, tableStr, fitsPath, fitsFile)
    self.Run(queryStr)
    self.GetResultHeaders()
    row = self.GetResults()
    return int(row[idStr])

  def GetObjectID(self, bundle_lid):
    tableStr = 'objects'
    idStr = 'objectid'
    queryStr = "SELECT %s from %s WHERE pds4_lid = '%s';" % (idStr, tableStr, collection_lid)
    self.Run(queryStr)
    self.GetResultHeaders()
    row = self.GetResults()
    return int(row[idStr])

  #a subroutine to get the instrument id from an instrument_lid (already mapped from Jan's code
  def GetInstrumentID(self, collection_lid):
    tableStr = 'instruments'
    idStr = 'instrumentid'
    #assume telinstruments are inserted using coma-collection-lid as tinstrumentname
    queryStr = "SELECT %s from %s WHERE acronym = '%s';" % (idStr, tableStr, collection_lid)
    self.Run(queryStr)
    self.GetResultHeaders()
    row = self.GetResults()
    return int(row[idStr])

  def InsertCalibration(self, fits_file, instrument_lid, mjdMiddle, filterCode, nStars, zpMag, zpMagErr):
    # create a connection cursor
    tableStr = 'calibrations'
    idStr = 'calibrationid'
    nextID = self.GetNextID(tableStr, idStr)

    # need lookup code for imageID from FITS_FILE name and instumentID from Jan's Instrument code
    imageID = GetImageID(fits_file)
    instrumentID = GetInstrumentID(instrument_lid)
    filterID = GetFilterID(filterCode)

    values = (nextID,  imageID, instrumentID, mjdMiddle, filterID, nStars, zpMag, zpMagErr)
    insert = "INSERT INTO %s (%s, imageid, instrumentid, mjd_middle, filterID, nstars, zpmag, zpmag_error) VALUES (?, ?, ?, ?, ?, ?, ?, ?)" % (tableStr, idStr)
    return self.InsertRow(insert, values)

# imageid                   | int(11)     | NO   | PRI | NULL    |       |
# calibrationid             | int(11)     | NO   |     | NULL    |       |
# instrumentid              | int(11)     | NO   |     | NULL    |       |
# mjd_middle                | double      | YES  |     | NULL    |       |
# filter                    | char(2)     | YES  |     | NULL    |       |
# nstars                    | int(11)     | YES  |     | NULL    |       |
# zpmag                     | double      | YES  |     | NULL    |       |
# zpmag_error               | double      | YES  |     | NULL    |       |
# extinction                | double      | YES  |     | NULL    |       |
# extinction_error          | double      | YES  |     | NULL    |       |
# colorterm                 | double      | YES  |     | NULL    |       |
# colorterm_error           | double      | YES  |     | NULL    |       |
# zpinstmag                 | double      | YES  |     | NULL    |       |
# zpinstmag_err             | double      | YES  |     | NULL    |       |
# pixel_scale               | double      | YES  |     | NULL    |       |
# psf_nobj                  | int(11)     | YES  |     | NULL    |       |
# psf_fwhm_arcsec           | double      | YES  |     | NULL    |       |
# psf_major_axis_arcsec     | double      | YES  |     | NULL    |       |
# psf_minor_axis_arcsec     | double      | YES  |     | NULL    |       |
# psf_pa_pix                | double      | YES  |     | NULL    |       |
# psf_pa_world              | double      | YES  |     | NULL    |       |
# limit_mag_5_sigma         | double      | YES  |     | NULL    |       |
# limit_mag_10_sigma        | double      | YES  |     | NULL    |       |
# ndensity_mag_20           | double      | YES  |     | NULL    |       |
# ndensity_5_sigma          | double      | YES  |     | NULL    |       |
# sky_backd_adu_pix         | double      | YES  |     | NULL    |       |
# sky_backd_photons_pix     | double      | YES  |     | NULL    |       |
# sky_backd_adu_arcsec2     | double      | YES  |     | NULL    |       |
# sky_backd_photons_arcsec2 | double      | YES  |     | NULL    |       |
# sky_backd_mag_arcsec2     | double      | YES  |     | NULL    |       |

