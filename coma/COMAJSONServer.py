# COMAJSONServer.py

# encapsulate Jan Kleyna's COMA JSON API for Python

from subprocess import Popen, PIPE, CalledProcessError
import os
import requests
import json
import time
import logging

def readPipeline(p):
  result = ""
  done=0
  for tries in range(50):
    for line in iter(p.readline()):
      if line == "}":
        done+=1
      result = result + line
      if done==2:
        break
    if done==2:
      break
  return result

class COMAAPI:
  # default constructor

  def __init__(self):
    self.debug=False
    logging.basicConfig(filename='/coma/coma.log', filemode='a', encoding='utf-8', level=logging.DEBUG)
    self.uuid = "abc123"
    self.COMAServerPollCount= int(os.getenv('COMA_SERVER_POLL_COUNT', default="60"))
    self.COMAServerPollInterval= int(os.getenv('COMA_SERVER_POLL_INTERVAL', default="1"))
    self.COMAServerPath= os.getenv('COMA_SERVER_PATH', default="/coma/bin/coma-json-server")
    self.COMAServerPort = int(os.getenv('COMA_SERVER_PORT', default="5054"))
    self.COMAServerHost = os.getenv('COMA_SERVER_HOST', default="172.17.0.1")
    COMAServerSubmit = os.getenv('COMA_SERVER_SUBMIT', default="submit-json")
    COMAServerRetrieve = os.getenv('COMA_SERVER_RETRIEVE', default="retrieve-json")
    self.COMAServerSubmitURL = "http://%s:%d/%s" % (self.COMAServerHost, self.COMAServerPort, COMAServerSubmit)
    self.COMAServerRetrieveURL = "http://%s:%d/%s" % (self.COMAServerHost, self.COMAServerPort, COMAServerRetrieve)
    self.LaunchServer()

  def __del__(self):
    self.StopServer()

  def LaunchServer(self, port=0):
    if self.COMAServerPort == 0:
      self.pCOMAServer = Popen(["/bin/sh", self.COMAServerPath], bufsize=1, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
      self.fRequest = self.pCOMAServer.stdin
      self.fResponse = self.pCOMAServer.stdout
    #else
    # check here for coma-json-server listening on configured port
      

  def StopServer(self):
    if self.COMAServerPort == 0:
      self.pCOMAServer.kill()

  def GetPID(self):
    cmd = "ps -ef | grep coma-json-server | grep 5054 | head -1"
    result = os.popen(cmd).read()
    logging.debug(result)
    val = result.split()
    if len(val) > 2:
      return int(val[2])

  def SetUUID(self, uuid):
    self.uuid = uuid

  def GetResponse(self):
    if self.COMAServerPort == 0:
      response = readPipeline(self.fResponse)
    else:
      trys = self.COMAServerPollCount
      request = { "id": self.uuid }
      print(request)
      for t in range(trys):
        ## should move this sleep back under the final else case below

        req = requests.get(self.COMAServerRetrieveURL, params=request)
        logging.debug(self.COMAServerRetrieveURL)
        rsp = req.json()
        if rsp is None:
          time.sleep(self.COMAServerPollInterval)
          response = ""
        else:
          logging.debug(json.dumps(rsp))
          if rsp["TYPE"] == "RESPONSE":
            if "ERROR" in rsp.keys():
              response = json.dumps(rsp["ERROR"])
            else:
              response = json.dumps(rsp["PARAMETERS"])
            break
          elif rsp["STATUS"] == "ERROR":
            response = json.dumps(rsp)
            break
          else:
            time.sleep(self.COMAServerPollInterval)
            response = json.dumps(rsp)

    return response
 
  def SendRequest(self, command, parameters):
    request = "{ \"type\":\"request\", \"command\": \"%s\", \"id\":\"%s\", \"parameters\": %s }" % (command, self.uuid, parameters)
    if self.COMAServerPort == 0:
      self.fRequest.write(request)
      self.fRequest.flush()
    else:
      request = { "request": request }
      logging.debug(self.COMAServerSubmitURL)
      logging.debug(request)
      req = requests.post(self.COMAServerSubmitURL, data=request)
      response = json.dumps(req.json())
      logging.debug(response)
 
  def HeaderFITS(self, fits):
    print(fits)
    params = "{ \"FITS-FILE\": \"%s\" }" % (fits)
    self.SendRequest("read-fits-header", params)
    return self.GetResponse()

  def WriteFITS(self, fits, key, value, comment = None):
    print(fits)
    params = "{ \"FITS-FILE\": \"%s\"," % (fits)
    params += " \"KEYWORD\": \"%s\"," % (key)
    params += " \"VALUE\": \"%s\"," % (value)
    if comment is not None:
      params += " \"COMMENT\": \"%s\"," % (comment)
    params += "}"
    self.SendRequest("write-fits-header", params)
    return self.GetResponse()

  def DescribeFITS(self, fits):
    print(fits)
    params = "{ \"FITS-FILE\": \"%s\" }" % (fits)
    self.SendRequest("describe-fits-long", params)
    #self.SendRequest("describe-fits", params)
    return self.GetResponse()

  def CalibrateFITSPhotometry(self, fits, objid, method, aperture):
    params = "{ \"FITS-FILE\": \"%s\"," % (fits)
    params += " \"STAMP-CENTER-METHOD\": \"ORBIT\","
    params += " \"POSITION\": \"OBJECT\","
    params += " \"ORBIT\": \"MPC-ORBIT\","
    params += " \"OBJECT-NAME\": \"%s\"," % (objid)
    params += " \"PHOTOMETRY-REQUESTS\": [ {"
    if method == "TheAperturePhotometry":
      params += " \"ID\": \"%s\"," % (method)
      params += " \"PHOTOMETRY-TYPE\": \"APERTURE\","
      params += " \"APERTURES\": %s," % (aperture)
      params += " \"TUNE-POSITION\": \"true\","
      params += " \"BACKGROUND-RADIUS\": \"AUTO\","
    params += " }]"
    params += "}"
    self.SendRequest("do-photometry", params)
    return self.GetResponse()

  def CalibrateFITS(self, fits):
    params = "{ \"FITS-FILE\": \"%s\"," % (fits)
    params += "}"
    self.SendRequest("calibrate-image", params)
    return self.GetResponse()

  def GetOrbit(self, objid, mjd):
    params = "{ \"METHOD\": \"orbit\","
    params += " \"OBJECT\": \"%s\"," % (objid)
    params += " \"EPOCH-MJD\": %f," % (mjd)
    params += "}"
    self.SendRequest("get-orbit", params)
    return self.GetResponse()

  def GetEphemeris(self, objid, obscode, dt_min, utc_start, utc_end):
    params = "{ \"METHOD\": \"ORBIT\","
    params += " \"ORBIT\": \"jpl-orbit\","
    params += " \"OBJECT\": \"%s\"," % (objid)
    params += " \"OBSCODE\": \"%s\"," % (obscode)
    params += " \"DT-MINUTES\": %d," % (dt_min)
    params += " \"UTC-START\": \"%s\"," % (utc_start)
    params += " \"UTC-END\": \"%s\"," % (utc_end)
    params += "}"
    self.SendRequest("get-ephem", params)
    return self.GetResponse()


