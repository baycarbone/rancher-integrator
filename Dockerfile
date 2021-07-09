FROM python:3

WORKDIR /usr/src/app
RUN mkdir /usr/src/app/import_manifest

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY rancher-integrator.py ./

ENTRYPOINT [ "python", "./rancher-integrator.py"]
