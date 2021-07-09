# rancher-integrator
Script capable of registering (and if needed unregistering) a Kubernetes cluster into an 
existing Rancher container management platform. The registration manifest is also retrieved and 
stored in a predefined location.

The script makes use of the following python client for the Rancher API:  
https://github.com/rancher/client-python


## Usage
```bash
usage: rancher-integrator [-h] [-i] [-w] url username password {register,unregister} ...

Handle cluster registration in rancher

positional arguments:
  url                   Rancher url
  username              API access key
  password              API secret key
  {register,unregister}
                        Sub-commands
    register            REGISTER a cluster in rancher
    unregister          UNREGISTER a cluster from rancher

optional arguments:
  -h, --help            show this help message and exit
  -i, --insecure        Allow insecure https
  -w, --wait            Run forever
```
