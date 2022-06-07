# gnoi_python_client
gnoi python client for openconfig gnoi

The development of a grpc-Python gnoi client requires the following:

python 3.7 and latest version of pip, virtualenv

python 3.7 packages: grpcio, protobuf==3.20.0
gnoi proto files: http://github.com/openconfig/gnoi.git (commit-id: 2e1ce73b56028fa34e860896fa935c21d6446058) .latest as on may 20 , 2020

The commands in this repo sets up the development environment for developing XR gnoi client on an XR CEL7 (ads) machine. Note, the environment works only on ads machine where /router/bin is present and can be found in PATH.

 pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
 pip install protobuf==3.20.0 

