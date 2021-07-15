# rancher-integrator
Script capable of registering (and if needed unregistering) a Kubernetes cluster into an 
existing Rancher container management platform. The registration manifest is also retrieved and 
stored in a predefined location.

More information about the cluster registration process can be found at:  
https://rancher.com/docs/rancher/v2.5/en/cluster-provisioning/registered-clusters/

The script makes use of the following python client for the Rancher API:  
https://github.com/rancher/client-python


## Usage
```bash
usage: rancher-integrator [-h] [-l URL] [-u USERNAME] [-p PASSWORD] [-c CERT_CHECK] [-w WAIT] {register,unregister,verify} ...

Handle cluster registration in rancher

positional arguments:
  {register,unregister,verify}
                        Sub-commands
    register            REGISTER a cluster in rancher
    unregister          UNREGISTER a cluster from rancher
    verify              VERIFY the API credentials are suitable for cluster management

optional arguments:
  -h, --help            show this help message and exit
  -l URL, --url URL     Rancher url
  -u USERNAME, --username USERNAME
                        API access key
  -p PASSWORD, --password PASSWORD
                        API secret key
  -c CERT_CHECK, --cert_check CERT_CHECK
                        Toggle certificate check (True|False)
  -w WAIT, --wait WAIT  Toggle run forever (True|False)

See '<command> --help' to read about a specific sub-command
```

The following environment variables can be used instead of command line arguments.
However in case both are set, command line arguments take precedence over environment variables.
```
RANCHER_INTEGRATOR_URL
RANCHER_INTEGRATOR_USERNAME
RANCHER_INTEGRATOR_PASSWORD
RANCHER_INTEGRATOR_INSECURE
RANCHER_INTEGRATOR_WAIT
RANCHER_INTEGRATOR_CLUSTER_NAME
```

## Container version
https://hub.docker.com/repository/docker/baycarbone/rancher-integrator