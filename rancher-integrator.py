import rancher
import petname
import argparse
import time
import urllib
import ssl

class RancherRegsitration:
    def __init__(self, rancher_url, access_key, secret_key, cert_verify=True):
        self.client = self._create_client(rancher_url, access_key, secret_key, cert_verify)

    def _create_client(self, rancher_url, access_key, secret_key, cert_verify):
        return rancher.Client(url=rancher_url,
                                access_key=access_key,
                                secret_key=secret_key,
                                verify=cert_verify)

    def register_cluster(self, name):
        if name is None:
            name = petname.Generate()
        # import cluster
        cluster_data = self.client.create_cluster(name=name)

        time.sleep(5)
        # create registration token for the cluster
        reg_data = self.client.create_clusterRegistrationToken(clusterId=cluster_data.data_dict()["id"])

        linkToFile = reg_data.data_dict()['manifestUrl']
        localDestination = "./import_manifest/import_" + name + ".yaml"
        resultFilePath, responseHeaders = urllib.request.urlretrieve(linkToFile, localDestination)
        # get url of k8s import manifest
        return name + ' - ' + reg_data.data_dict()['manifestUrl']

    def unregister_cluster(self, name):
        # get cluster by name
        cluster = self.client.list_cluster(name=name)

        # get cluster by id
        cluster_id = cluster.data[0]['id']
        cluster = self.client.by_id_cluster(cluster_id)

        # unregister cluster
        resp = self.client.delete(cluster)

        return resp

def main():

    parser = argparse.ArgumentParser(
        prog='rancher-integrator',
        description='Handle cluster registration in rancher',
        epilog="See '<command> --help' to read about a specific sub-command."
    )

    # rancher connection details as positional arguments
    parser.add_argument('url', help='Rancher url')
    parser.add_argument('username', help='API access key')
    parser.add_argument('password', help='API secret key')
    parser.add_argument('-i', '--insecure', help='Allow insecure https', action="store_true")
    parser.add_argument('-w', '--wait', help='Run forever', action="store_true")

    # subparser for the different commands e.g. register, unregister
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    # register subparser
    register_parser = subparsers.add_parser('register', help='REGISTER a cluster in rancher')
    register_parser.add_argument('-n', '--name', help='new cluster name')

    # unregister subparser
    unregister_parser = subparsers.add_parser('unregister', help='UNREGISTER a cluster from rancher')
    unregister_parser.add_argument('name', help='cluster name')

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

        if args.wait:
            loop_forever = True
            while loop_forever:
                try:
                    time.sleep(10)
                except KeyboardInterrupt:
                    loop_forever = False

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
