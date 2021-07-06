import rancher
import petname
import argparse

class RancherRegsitration:
    def __init__(self, rancher_url, access_key, secret_key, cert_verify=True):
        self.client = self._create_client(rancher_url, access_key, secret_key, cert_verify)

    def _create_client(self, rancher_url, access_key, secret_key, cert_verify):
        return rancher.Client(url=rancher_url,
                                access_key=access_key,
                                secret_key=secret_key,
                                verify=cert_verify)

    def register_cluster(self, name=petname.Generate()):

        # import cluster
        cluster_data = self.client.create_cluster(name=name)

        # create registration token for the cluster
        reg_data = self.client.create_clusterRegistrationToken(clusterId=cluster_data.data_dict()["id"])

        # get url of k8s import manifest
        return reg_data.data_dict()['manifestUrl']

def main():

    parser = argparse.ArgumentParser(description='Handle cluster registration in rancher')
    parser.add_argument('-l', '--url', help='Rancher url')
    parser.add_argument('-u', '--username', help='API access key')
    parser.add_argument('-p', '--password', help='API secret key')
    parser.options = parser.parse_args()

    rancher_url = 'https://' + parser.options.url + '/v3'
    access_key = parser.options.username
    secret_key = parser.options.password
    r = RancherRegsitration(rancher_url, access_key, secret_key, False)
    manifest = r.register_cluster()
    print(manifest)

if __name__ == "__main__":
    main()