FROM ubuntu:22.04

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get install -y --no-install-recommends wget build-essential python3 pip git
RUN apt-get install -y --no-install-recommends vim

WORKDIR /usr/local/src
RUN git clone https://github.com/asas-sn/skypatrol.git
RUN pip3 install skypatrol/

#RUN pip3 install skypatrol jupyter notebook seaborn
RUN pip3 install jupyter notebook seaborn
RUN mkdir -p /coma
WORKDIR /coma
COPY coma-skypatrol.py .
COPY COMA-SkyPatrol.ipynb .

#ENTRYPOINT ["sleep", "86400"]
