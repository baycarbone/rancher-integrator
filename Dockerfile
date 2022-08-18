FROM python:slim-buster

WORKDIR /usr/src/app

RUN mkdir /usr/src/app/import_manifest

COPY requirements.txt ./
RUN apt update && apt install git -y
RUN pip install --no-cache-dir -r requirements.txt

COPY rancher-integrator.py ./

ENTRYPOINT [ "python", "./rancher-integrator.py"]
