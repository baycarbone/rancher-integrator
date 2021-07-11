# rancher-integrator
Script capable of registering (and if needed unregistering) a Kubernetes cluster into an 
existing Rancher container management platform. The registration manifest is also retrieved and 
stored in a predefined location.

The script makes use of the following python client for the Rancher API:  
https://github.com/rancher/client-python


## Usage
```bash
usage: rancher-integrator [-h] [--url URL] [--username USERNAME] [--password PASSWORD] [-i INSECURE] [-w WAIT] {register,unregister,verify} ...

Handle cluster registration in rancher

positional arguments:
  {register,unregister,verify}
                        Sub-commands
    register            REGISTER a cluster in rancher
    unregister          UNREGISTER a cluster from rancher
    verify              VERIFY the API credentials are suitable for cluster management

optional arguments:
  -h, --help            show this help message and exit
  --url URL             Rancher url
  --username USERNAME   API access key
  --password PASSWORD   API secret key
  -i INSECURE, --insecure INSECURE
                        Toggle insecure https
  -w WAIT, --wait WAIT  Toggle run forever
```
