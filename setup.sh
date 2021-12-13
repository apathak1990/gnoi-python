#!/bin/bash

# Setup development environment for XR gnoi python client

#
# Setup gnoi repo. Only needed when regenerate *_pb2*.py
#
setup_gnoi_repo() {
    if [[ ! -d src/github.com/openconfig/gnoi/.git ]]; then
	mkdir -p src/github.com/openconfig > /dev/null
	pushd src/github.com/openconfig > /dev/null
	git clone https://github.com/openconfig/gnoi.git 
	pushd gnoi > /dev/null
	git branch -d xr_gnoi_client_phase_4 >& /dev/null
	git checkout -b xr_gnoi_client_phase_4 0b5aea31df40c60251a246ba9047cd256488036b > /dev/null
	popd > /dev/null
	popd > /dev/null
   fi
}

# Setting python 2.7 virtualenv and all grpc packages
if [[ ! -f xr-venv/bin/activate ]]; then
	#virtualenv ./xr-venv
        /router/bin/python3 -m venv ./xr-venv3
	source xr-venv3/bin/activate > /dev/null
        pip install --upgrade pip
	pip install grpcio > /dev/null
	pip install grpcio-tools > /dev/null
fi

# Uncomment the next line if need to generate pb2:
setup_gnoi_repo

# Prompt user on how to continue ...
echo "XR gnoi python phase 4 client environment is ready."
echo "Execute \"source xr-venv3/bin/activate\" to start"
