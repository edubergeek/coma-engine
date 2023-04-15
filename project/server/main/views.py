# project/server/main/views.py

import redis
from rq import Queue, Connection
from flask import render_template, Blueprint, jsonify, request, current_app
from flask_cors import CORS

import json

from project.server.main.tasks import coma_object_images, coma_fits_header, coma_fits_describe, coma_fits_calibrate, coma_fits_photometry, coma_lightcurve, coma_fits_meta
from project.server.main.tasks import coma_insert_telescope, coma_get_observatory, coma_get_telescope, backend_pid

def job_tasks(job):
  job_def = json.loads(job)
  # enumerate the array of tasks
  #for task in job_def:
  
  #with Connection(redis.from_url(current_app.config["REDIS_URL"])):
  #  q = Queue()
  #  task = q.enqueue(coma_describe_fits, fits_file)
  #response_object = {
  #  "status": "success",
  #  "task": { "id": task.get_id() },
  #}
  return job_def

main_blueprint = Blueprint("main", __name__,)
CORS(main_blueprint)

# Configure for Cross-Origin Resource Sharing (CORS)
#  "allow_headers": ["Authorization", "Content-Type"]
cors_get_config = {
  "origins": ["http://localhost:8080", "http://localhost:5004"],
  "methods": ["OPTIONS", "GET"],
  "allow_headers": ["Content-Type"]
}
cors_post_config = {
  "origins": ["http://localhost:8080", "http://localhost:5004", "http://localhost:*", "*"],
  "methods": ["OPTIONS", "POST"],
  "allow_headers": ["Content-Type"]
}
CORS(main_blueprint, resources={"/": cors_get_config})
@main_blueprint.route("/", methods=["GET"])
def home():
  return render_template("main/home.html")


# API for list all URLs
CORS(main_blueprint, resources={"/routes/": cors_get_config})
@main_blueprint.route("/routes/", methods=["GET"])
def list_routes():
  response_object = {
      "routes": {
        "url": "/routes", 
        "method": "GET",
        "description": "List of REST API URLs",
      },
      "lightcurve": {
        "url": "/lightcurve",
        "method": "POST",
        "description": "Query an object light curve",
        "object": "object identifier",
        "begin": "begin date",
        "end": "end date",
      },
      "objects": {
        "url": "/objects", 
        "method": "GET",
        "description": "List of valid object IDs",
      },
      "object-images": {
        "url": "/object/images/<id>", 
        "method": "GET",
        "description": "List object images",
        "<id>": "Object ID",
      },
      "telescope": {
        "url": "/telescope/<code>", 
        "method": "GET",
        "description": "Get telescope attributes",
        "<code>": "Telescope Code",
      },
      "observatory": {
        "url": "/observatory/<code>", 
        "method": "GET",
        "description": "Get observatory attributes",
        "<code>": "Observatory Code",
      },
      "fits-header": {
        "url": "/fits/header",
        "method": "POST",
        "description": "List FITS file header values for a fits file",
        "fits_file": "full path of FITS file",
      },
      "fits-describe": {
        "url": "/fits/describe",
        "method": "POST",
        "description": "Get FITS observation data for a fits file",
        "fits_file": "full path of FITS file",
      },
      "fits-calibrate": {
        "url": "/fits/calibrate",
        "method": "POST",
        "description": "Calibrate FITS image",
        "fits_file": "full path of FITS file",
      },
      "fits-photometry": {
        "url": "/fits/photometry",
        "method": "POST",
        "description": "Run FITS image photometry",
        "fits_file": "full path of FITS file",
        "object": "COMA id of the object, e.g. 9P",
        "method": "COMA photometry method, e.g. TheAperturePhotometry",
        "aperture": "radius/aperture, scalar or vector",
      },
      "fits-meta": {
        "url": "/fits/meta",
        "method": "POST",
        "description": "Write metadata FITS header values",
        "fits_file": "full path of FITS file",
        "key": "header keyword",
        "value": "header value",
        "comment": "header comment",
      },
      "run-job": {
        "url": "/job/run",
        "method": "POST",
        "description": "Launch a job comprising a set of tasks defined in a JSON string",
        "job": "JSON encoded string describing the tasks comprising the job",
      },
      "task-status": {
        "url": "/task/status/<task_id>",
        "method": "GET",
        "description": "Poll task status e.g. finished, failed",
        "<task_id>": "Task UUID",
      },
      "task-result": {
        "url": "/task/result/<task_id>",
        "method": "GET",
        "description": "Retrieve task output as a JSON encoded string",
        "<task_id>": "Task UUID",
      },
  }
  return jsonify(response_object)

# API for list object ids
CORS(main_blueprint, resources={"/objects": cors_get_config})
@main_blueprint.route("/objects", methods=["GET"])
def list_objects():
  response_object = {
    "9p": "9P/1867 G1 (Tempel 1)",
  }
  return jsonify(response_object)


#@main_blueprint.route("/tasks", methods=["POST"])
#def run_task():
#  task_type = request.form["type"]
#  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
#    q = Queue()
#    task = q.enqueue(create_task, task_type)
#  response_object = {
#    "status": "success",
#    "task": { "id": task.get_id() },
#  }
#  return jsonify(response_object), 202


CORS(main_blueprint, resources={"/task/status*": cors_get_config})
@main_blueprint.route("/task/status/<task_id>", methods=["GET"])
def get_status(task_id):
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.fetch_job(task_id)
  if task:
    response_object = {
      "status": "success",
      "task": {
        "id": task.get_id(),
        "status": task.get_status(),
      },
    }
  else:
    response_object = { "status": "error" }
  return jsonify(response_object)

CORS(main_blueprint, resources={"/task/result*": cors_get_config})
@main_blueprint.route("/task/result/<task_id>", methods=["GET"])
def get_result(task_id):
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.fetch_job(task_id)
  if task and task.result:
    response_object = {
      "status": "success",
      "task": {
        "id": task.get_id(),
        "status": task.get_status(),
        "enqueued": task.enqueued_at.isoformat(),
      },
      "data": task.result
    }
  else:
    response_object = { "status": "error" }
  return jsonify(response_object)

CORS(main_blueprint, resources={"/object/images*": cors_get_config})
@main_blueprint.route("/object/images/<obj_id>", methods=["GET"])
def task_object_images(obj_id):
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_object_images, obj_id)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  return jsonify(response_object), 202

CORS(main_blueprint, resources={"/fits/header*": cors_post_config})
@main_blueprint.route("/fits/header", methods=["POST"])
def task_fits_header():
  if request.content_type == "application/json":
    fits_file = request.json["fits_file"]
  else:
    fits_file = request.form["fits_file"]
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_fits_header, fits_file)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  response = jsonify(response_object)
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response, 202

CORS(main_blueprint, resources={"/fits/describe*": cors_post_config})
@main_blueprint.route("/fits/describe", methods=["POST"])
def task_fits_describe():
  if request.content_type == "application/json":
    fits_file = request.json["fits_file"]
  else:
    fits_file = request.form["fits_file"]
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_fits_describe, fits_file)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  response = jsonify(response_object)
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response, 202

CORS(main_blueprint, resources={"/fits/meta*": cors_post_config})
@main_blueprint.route("/fits/meta", methods=["POST"])
def task_fits_meta():
  if request.content_type == "application/json":
    fits_file = request.json["fits_file"]
    objid = request.json["key"]
    method = request.json["value"]
    aperture = request.json["comment"]
  else:
    fits_file = request.form["fits_file"]
    objid = request.form["key"]
    method = request.form["value"]
    aperture = request.form["comment"]
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_fits_meta, fits_file, objid, method, aperture)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  response = jsonify(response_object)
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response, 202

CORS(main_blueprint, resources={"/fits/photometry*": cors_post_config})
@main_blueprint.route("/fits/photometry", methods=["POST"])
def task_fits_photometry():
  if request.content_type == "application/json":
    fits_file = request.json["fits_file"]
    objid = request.json["object"]
    method = request.json["method"]
    aperture = request.json["aperture"]
  else:
    fits_file = request.form["fits_file"]
    objid = request.form["object"]
    method = request.form["method"]
    aperture = request.form["aperture"]
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_fits_photometry, fits_file, objid, method, aperture)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  response = jsonify(response_object)
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response, 202

CORS(main_blueprint, resources={"/fits/calibrate*": cors_post_config})
@main_blueprint.route("/fits/calibrate", methods=["POST"])
def task_fits_calibrate():
  if request.content_type == "application/json":
    fits_file = request.json["fits_file"]
  else:
    fits_file = request.form["fits_file"]
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_fits_calibrate, fits_file)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  response = jsonify(response_object)
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response, 202

CORS(main_blueprint, resources={"/job/run*": cors_post_config})
@main_blueprint.route("/job/run", methods=["POST"])
def task_run_job():
  if request.content_type == "application/json":
    job = request.json["job"]
  else:
    job = request.form["job"]
  response_object = job_tasks(job)
  response = jsonify(response_object)
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response, 202

#def run_task():
#  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
#    q = Queue()
#    task = q.enqueue(create_task, task_type)
#  response_object = {
#    "status": "success",
#    "task": { "id": task.get_id() },
#  }
#  return jsonify(response_object), 202


CORS(main_blueprint, resources={"/insert/telescope*": cors_post_config})
@main_blueprint.route("/insert/telescope", methods=["POST"])
def task_insert_telescope():
  if request.content_type == "application/json":
    telescopeName = request.json["name"]
  else:
    telescopeName = request.form["name"]
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_insert_telescope, telescopeName)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  response = jsonify(response_object)
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response, 202


CORS(main_blueprint, resources={"/observatory*": cors_get_config})
@main_blueprint.route("/observatory/<obs_id>", methods=["GET"])
def task_observatory_info(obs_id):
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_get_observatory, obs_id)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  return jsonify(response_object), 202

CORS(main_blueprint, resources={"/telescope*": cors_get_config})
@main_blueprint.route("/telescope/<tel_id>", methods=["GET"])
def task_get_telescope(tel_id):
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_get_telescope, tel_id)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  return jsonify(response_object), 202

CORS(main_blueprint, resources={"/lightcurve*": cors_get_config})
@main_blueprint.route("/lightcurve", methods=["POST"])
def task_lightcurve():
  if request.content_type == "application/json":
    objid = request.json["object"]
    begin_date = request.json["begin"]
    end_date = request.json["end"]
  else:
    objid = request.form["object"]
    begin_date = request.form["begin"]
    end_date = request.form["end"]
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_lightcurve, objid, begin_date, end_date)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  response = jsonify(response_object)
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response, 202


CORS(main_blueprint, resources={"/backend/status*": cors_get_config})
@main_blueprint.route("/backend/status", methods=["GET"])
def backend_status():
  response_object = {
    "status": "success",
    "backend": {
      "pid": backend_pid(),
#      "status": get_backend_status(),
    },
  }
  return jsonify(response_object)

