#!venv/bin/python

from flask import Flask, Response, render_template, request

import json
import zmap

app = Flask(__name__)
app.jinja_env.globals["valid_args"] = dict([(k, v) for k, v in zmap.ZMapConfig.VALID_ARGS.iteritems() if k in zmap.global_config["allowed_args"]])

jobs = {}

@app.route("/")
def home():
   return render_template('home.html')

# List all current jobs
@app.route("/jobs", methods=["GET"])
def list_jobs():
   report = dict([(job_id, job.report()) for job_id, job in jobs.iteritems()])
   return render_template('jobs.html', jobs=report)

@app.route("/jobs.json", methods=["GET"])
def list_jobs_json():
   report = dict([(job_id, job.report()) for job_id, job in jobs.iteritems()])

   return Response(json.dumps(report), mimetype="application/json")

# Create a job
@app.route("/jobs", methods=["POST"])
def start():
   config = dict((k, v) for k, v in request.form.iteritems() if len(v) > 0)
   job = zmap.zmap_gen(config)
   job.start()
   jobs[job.job_id] = job
   return "", 201

# Delete a job
@app.route("/jobs/<job_id>", methods=["DELETE"])
def stop(job_id):
   job_id = int(job_id)
   if job_id in jobs:
      jobs[job_id].stop()
      del jobs[job_id]
      return "", 204
   else:
      return "Job id not found", 404

# View a job
@app.route("/jobs/<job_id>", methods=["GET"])
def progress(job_id):
   job_id = int(job_id)
   if job_id in jobs:
      return render_template('job.html', job=jobs[job_id].report())

@app.route("/jobs/<job_id>.json", methods=["GET"])
def progress_json(job_id):
   job_id = int(job_id)
   if job_id in jobs:
      return Response(json.dumps(jobs[job_id].report()), mimetype="application/json")
   else:
      return "Job id not found", 404

if __name__ == "__main__":
   Flask.debug = True
   app.run(host='0.0.0.0', port=80)
