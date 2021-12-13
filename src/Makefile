PROJ_WS = $(PWD)
GNOI = github.com/openconfig/gnoi
GNOI_PY = github/com/openconfig/gnoi

.phony: all clean

all: pb2_py_gen
	mv ${GNOI}/types/types_pb2_grpc.py ${GNOI_PY}/types/types_pb2_grpc.py
	mv ${GNOI}/common/common_pb2_grpc.py ${GNOI_PY}/common/common_pb2_grpc.py
	mv ${GNOI}/file/file_pb2_grpc.py ${GNOI_PY}/file/file_pb2_grpc.py
	mv ${GNOI}/system/system_pb2_grpc.py ${GNOI_PY}/system/system_pb2_grpc.py
	mv ${GNOI}/cert/cert_pb2_grpc.py ${GNOI_PY}/cert/cert_pb2_grpc.py
	mv ${GNOI}/diag/diag_pb2_grpc.py ${GNOI_PY}/diag/diag_pb2_grpc.py
	mv ${GNOI}/otdr/otdr_pb2_grpc.py ${GNOI_PY}/otdr/otdr_pb2_grpc.py
	mv ${GNOI}/bgp/bgp_pb2_grpc.py ${GNOI_PY}/bgp/bgp_pb2_grpc.py
	mv ${GNOI}/interface/interface_pb2_grpc.py ${GNOI_PY}/interface/interface_pb2_grpc.py
	mv ${GNOI}/layer2/layer2_pb2_grpc.py ${GNOI_PY}/layer2/layer2_pb2_grpc.py
	mv ${GNOI}/mpls/mpls_pb2_grpc.py ${GNOI_PY}/mpls/mpls_pb2_grpc.py


pb2_py_gen: ${GNOI}/types/types.proto \
	${GNOI}/common/common.proto \
	${GNOI}/file/file.proto \
	${GNOI}/system/system.proto \
	${GNOI}/cert/cert.proto \
	${GNOI}/diag/diag.proto \
	${GNOI}/otdr/otdr.proto \
	${GNOI}/bgp/bgp.proto \
	${GNOI}/interface/interface.proto \
	${GNOI}/layer2/layer2.proto \
	${GNOI}/mpls/mpls.proto
	python -m grpc_tools.protoc \
		-I./ -o $@ --include_imports $^ \
		--python_out=.  --grpc_python_out=.\

clean:
	rm -f pb2_py_gen
	find . -name "*pb2*py" | xargs -n 1 rm
