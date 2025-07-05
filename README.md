# coma-engine

This code implements a REST API developed for Karen Meech's COMA project funded by NASA (citation).
It uses Flask for the web API, Redis Queue for task orchestration and Docker/Docker Compose for virtualization.
The baseline code was forked from mjhea0/flask-redis-queue on GitHub.
It encapsulates SQL query tasks using the COMA database (MariaDB).
It encapsulates low-level astronomy functions implemented in Jan Kleyna's coma-json-server API.
It includes an ASAS-SN SkyPatrol 2.0 Jupyter notebook to extract ASAS-Sn comet light curves.

### Quick Start

Get the code:

```sh
git clone https://github.com/edubergeek/coma-engine
```

Build the containers:

```sh
$ cd coma-engine
$ docker-compose build
```

Spin up the containers:

```sh
$ cd coma-engine
$ docker-compose up -d
```

Shut it down:

```sh
$ cd coma-engine
$ docker-compose down
```

Access the REST API:
Open your browser to http://localhost:5004
