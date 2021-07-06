import rancher
import petname

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
    rancher_url = 'https://rancher.maas/v3'
    access_key = 'token-fc4gq'
    secret_key = 'xwzp5qwqrk7qtwgrc8lrfpfzrtwq6cspgfff8mzwkfd4pfpzb6plmf'
    r = RancherRegsitration(rancher_url, access_key, secret_key, False)
    manifest = r.register_cluster()
    print(manifest)

if __name__ == "__main__":
    main()