import rancher
import petname
import argparse
import time
import urllib
import ssl
import sys
import requests
import logging
import re
import os
from pathlib import Path
import random
from json.decoder import JSONDecodeError

class RancherRegsitration:
    def __init__(self, rancher_url, access_key, secret_key, cert_verify=True):
        # clear log file
        with open('error.log', 'w'):
            pass
        logging.basicConfig(filename='error.log', level=logging.ERROR)
        logging.getLogger().addHandler(logging.StreamHandler())
        self.client = self._create_client(rancher_url, access_key, secret_key, cert_verify)

    def _create_client(self, rancher_url, access_key, secret_key, cert_verify=True):
        '''Create a client for the Rancher API'''

        try:
            client = rancher.Client(url=rancher_url,
                                access_key=access_key,
                                secret_key=secret_key,
                                verify=cert_verify)
        except requests.exceptions.ConnectionError as err:
            if 'Temporary failure in name resolution' in str(err):
                logging.error('Failed to create a Rancher API client, please check the Rancher API url %s.', rancher_url)
                sys.exit()
            elif 'CERTIFICATE_VERIFY_FAILED' in str(err):
                logging.error('Failed to create a Rancher API client due to certificate verification failure. Perhaps you might want to try with the --insecure option.')
                sys.exit()
        except rancher.ApiError as err:
            logging.error('Failed to create a Rancher API client, please check the API credentials: %s.', err)
            sys.exit()
        except JSONDecodeError as err:
            logging.error('Failed to create a Rancher API client, please check the API connection details. JSONDecodeError: %s', err)
            sys.exit()

        return client

    def verify_api_client(self):
        '''Verify if the API client allows cluster management'''

        temp_cluster = "to-delete-" + str(random.randint(0000,9999))
        try:
            self.client.create_cluster(name=temp_cluster)
        except rancher.ApiError as err:
            if re.search(r'Forbidden.*cannot create resource "clusters"', str(err)):
                logging.error('Failed to create temp cluster %s, please check the API credentials as they do not allow the creation of clusters.', temp_cluster)
                return False
            elif re.search(r'NotUnique.*Cluster name', str(err)):
                logging.error('Failed to create temp cluster %s, a cluster with the same name already exists.', temp_cluster)
                return False
            else:
                logging.error('Failed to create temp cluster %s, API error: %s.', temp_cluster, err)
                return False

        time.sleep(1)
        try:
            self.unregister_cluster(temp_cluster)
        except rancher.ApiError as err:
            logging.error('Failed to create temp cluster %s, API error: %s.', temp_cluster, err)
            return False

        return True

    def register_cluster(self, name):
        '''Register a cluster in a Rancher platform and retrieve the Kubernetes import manifest'''

        if name is None:
            name = petname.Generate()

        # import cluster
        try:
            cluster_data = self.client.create_cluster(name=name)
        except rancher.ApiError as err:
            if re.search(r'Forbidden.*cannot create resource "clusters"', str(err)):
                logging.error('Failed to register cluster %s, please check the API credentials as they do not allow the creation of clusters.', name)
                sys.exit()
            elif re.search(r'NotUnique.*Cluster name', str(err)):
                logging.error('Failed to register cluster %s, a cluster with the same name already exists.', name)
                sys.exit()
            elif 'InvalidFormat' in str(err):
                logging.error('Failed to register cluster, the format of the cluster name is invalid: %s.', name)
                sys.exit()
            else:
                logging.error('Failed to register cluster %s, API error: %s.', name, err)
                sys.exit()

        # create registration token for the cluster
        token_created = False
        count = 0
        while count < 5 and not token_created:
            try:
                reg_data = self.client.create_clusterRegistrationToken(clusterId=cluster_data.data_dict()['id'])
                token_created = True
            except rancher.ApiError as err:
                if re.search(r'Forbidden.*cannot create resource "clusterregistrationtokens"', str(err)):
                    logging.warning('Unable to retrieve the cluster registration token for cluster: %s. Will retry in 1 second.', name)
                    count += 1
                    time.sleep(1)
        if count == 5:
            logging.error('Failed to retrieve a cluster registration token for cluster: %s. Max retry attempts reached.', name)
            sys.exit()

        # fetch registration token for the cluster
        import_manifest_url = reg_data.data_dict()['manifestUrl']
        storage_directory = Path('import_manifest')

        # if the destination directory already exists, just delete it
        if storage_directory.exists():
            for f in storage_directory.iterdir():
                f.unlink()
            storage_directory.rmdir()
        storage_directory.mkdir()
        manifest_file_name = name + '.yaml'

        try:
            resultFilePath, responseHeaders = urllib.request.urlretrieve(import_manifest_url, storage_directory / manifest_file_name)
        except urllib.error.HTTPError as err:
            logging.error('Failed to retrieve the import manifest (%s) for cluster: %s. Error: %s', import_manifest_url, name, err)
            self.unregister_cluster(name)
            sys.exit()

        # return name, url and location of path of import manifest
        return [name, import_manifest_url, str(storage_directory / manifest_file_name)]

    def unregister_cluster(self, name):
        # get cluster by name
        try:
            cluster = self.client.list_cluster(name=name)
        except rancher.ApiError as err:
            logging.error('Failed to unregister cluster %s, API error', err)
            sys.exit()

        # get cluster by id
        try:
            cluster_id = cluster.data[0]['id']
        except IndexError:
            logging.error('Failed to unregister cluster, %s is not a registered cluster.', name)
            sys.exit()

        try:
            cluster = self.client.by_id_cluster(cluster_id)
        except rancher.ApiError as err:
            logging.error('Failed to unregister cluster %s, API error', err)
            sys.exit()

        # unregister cluster
        try:
            resp = self.client.delete(cluster)
        except rancher.ApiError as err:
            logging.error('Failed to unregister cluster %s, API error', err)
            sys.exit()

        return resp

def main():

    parser = argparse.ArgumentParser(
        prog='rancher-integrator',
        description='Handle cluster registration in rancher',
        epilog="See '<command> --help' to read about a specific sub-command."
    )

    # rancher connection details as positional arguments
    parser.add_argument('--url', default=os.getenv('RANCHER_INTEGRATOR_URL'), help='Rancher url')
    parser.add_argument('--username', default=os.getenv('RANCHER_INTEGRATOR_USERNAME'), help='API access key')
    parser.add_argument('--password', default=os.getenv('RANCHER_INTEGRATOR_PASSWORD'), help='API secret key')
    parser.add_argument('-i', '--insecure', default=os.getenv('RANCHER_INTEGRATOR_INSECURE'),  help='Toggle insecure https')
    parser.add_argument('-w', '--wait', default=os.getenv('RANCHER_INTEGRATOR_WAIT'), help='Toggle run forever')

    # subparser for the different commands e.g. register, unregister
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    # register subparser
    register_parser = subparsers.add_parser('register', help='REGISTER a cluster in rancher')
    register_parser.add_argument('-n', '--name', help='new cluster name')

    # unregister subparser
    unregister_parser = subparsers.add_parser('unregister',  help='UNREGISTER a cluster from rancher')
    unregister_parser.add_argument('name', default=os.getenv('RANCHER_INTEGRATOR_NAME'), help='cluster name')

    # verify_api subparser
    verify_api_parser = subparsers.add_parser('verify', help='VERIFY the API credentials are suitable for cluster management')

    args = parser.parse_args()

    if args.command is not None:
        rancher_url = 'https://' + args.url + '/v3'
        access_key = args.username
        secret_key = args.password

        # create RancherRegsitration object with connection details
        if args.insecure:
            ssl._create_default_https_context = ssl._create_unverified_context
            r = RancherRegsitration(rancher_url, access_key, secret_key, False)
        else:
            r = RancherRegsitration(rancher_url, access_key, secret_key)

        if args.command == 'register':
            manifest = r.register_cluster(args.name)
            print(manifest)
        elif args.command == 'unregister':
            resp = r.unregister_cluster(args.name)
            print(resp)
        elif args.command == 'verify':
            resp = r.verify_api_client()
            print(resp)

        if args.wait == True:
            loop_forever = True
            while loop_forever:
                try:
                    time.sleep(10)
                except KeyboardInterrupt:
                    loop_forever = False

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
