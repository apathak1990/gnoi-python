# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from github.com.openconfig.gnoi.cert import cert_pb2 as github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2


class CertificateManagementStub(object):
    """The Certificate Management Service exported by targets.
    The service primarily exports two main RPCs, Install & Rotate which are used
    for installation of a new certificate, and rotation of an existing
    certificate on a target, along with a few management related RPCs.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Rotate = channel.stream_stream(
                '/gnoi.certificate.CertificateManagement/Rotate',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RotateCertificateRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RotateCertificateResponse.FromString,
                )
        self.Install = channel.stream_stream(
                '/gnoi.certificate.CertificateManagement/Install',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.InstallCertificateRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.InstallCertificateResponse.FromString,
                )
        self.GetCertificates = channel.unary_unary(
                '/gnoi.certificate.CertificateManagement/GetCertificates',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.GetCertificatesRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.GetCertificatesResponse.FromString,
                )
        self.RevokeCertificates = channel.unary_unary(
                '/gnoi.certificate.CertificateManagement/RevokeCertificates',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RevokeCertificatesRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RevokeCertificatesResponse.FromString,
                )
        self.CanGenerateCSR = channel.unary_unary(
                '/gnoi.certificate.CertificateManagement/CanGenerateCSR',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.CanGenerateCSRRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.CanGenerateCSRResponse.FromString,
                )


class CertificateManagementServicer(object):
    """The Certificate Management Service exported by targets.
    The service primarily exports two main RPCs, Install & Rotate which are used
    for installation of a new certificate, and rotation of an existing
    certificate on a target, along with a few management related RPCs.
    """

    def Rotate(self, request_iterator, context):
        """Rotate will replace an existing Certificate on the target by creating a
        new CSR request and placing the new Certificate based on the CSR on the
        target. If the stream is broken or any steps in the process fail the
        target must rollback to the original Certificate.

        The following describes the sequence of messages that must be exchanged
        in the Rotate() RPC.

        Sequence of expected messages:
        Case 1: When Target generates the CSR.

        Step 1: Start the stream
        Client <---- Rotate() RPC stream begin ------> Target

        Step 2: CSR
        Client -----> GenerateCSRRequest----> Target
        Client <----- GenerateCSRResponse <--- Target

        Step 3: Certificate Signing
        Client gets the certificate signed by the CA.

        Step 4: Send Certificate to Target.
        Client --> LoadCertificateRequest ----> Target
        Client <-- LoadCertificateResponse <--- Target

        Step 5: Test/Validation by the client.
        This step should be to create a new connection to the target using
        The new certificate and validate that the certificate works.
        Once verfied, the client will then proceed to finalize the rotation.
        If the new connection cannot be completed the client will cancel the
        RPC thereby forcing the target to rollback the certificate.

        Step 6: Final commit.
        Client ---> FinalizeRequest ----> Target


        Case 2: When Client generates the CSR.
        Step 1: Start the stream
        Client <---- Rotate() RPC stream begin ----> Target

        Step 2: CSR
        Client generates its own certificate.

        Step 3: Certificate Signing
        Client gets the certificate signed by the CA.

        Step 4: Send Certificate to Target.
        Client ---> LoadCertificateRequest ----> Target
        Client <--- LoadCertificateResponse <--- Target

        Step 5: Test/Validation by the client.

        Step 6: Final commit.
        Client ---> FinalizeRequest ----> Target
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Install(self, request_iterator, context):
        """Install will put a new Certificate on the target by creating a new CSR
        request and placing the new Certificate based on the CSR on the target.The
        new Certificate will be associated with a new Certificate Id on the target.
        If the target has a pre existing Certificate with the given Certificate Id,
        the operation should fail.
        If the stream is broken or any steps in the process fail the target must
        revert any changes in state.

        The following describes the sequence of messages that must be exchanged
        in the Install() RPC.

        Sequence of expected messages:
        Case 1: When Target generates the CSR-------------------------:

        Step 1: Start the stream
        Client <---- Install() RPC stream begin ------> Target

        Step 2: CSR
        Client -----> GenerateCSRRequest() ----> Target
        Client <---- GenerateCSRResponse() <---- Target

        Step 3: Certificate Signing
        Client gets the certificate signed by the CA.

        Step 4: Send Certificate to Target.
        Client -> LoadCertificateRequest() ----> Target
        Client <- LoadCertificateResponse() <--- Target

        Case 2: When Client generates the CSR-------------------------:
        Step 1: Start the stream
        Client <---- Install() RPC stream begin ------> Target

        Step 2: CSR
        Client generates its own certificate.

        Step 3: Certificate Signing
        Client gets the certificate signed by the CA.

        Step 4: Send Certificate to Target.
        Client -> LoadCertificateRequest() ----> Target
        Client <- LoadCertificateResponse() <--- Target

        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCertificates(self, request, context):
        """An RPC to get the certificates on the target.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RevokeCertificates(self, request, context):
        """An RPC to revoke specific certificates.
        If a certificate is not present on the target, the request should silently
        succeed. Revoking a certificate should render the existing certificate
        unusable by any endpoints.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CanGenerateCSR(self, request, context):
        """An RPC to ask a target if it can generate a Certificate.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CertificateManagementServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Rotate': grpc.stream_stream_rpc_method_handler(
                    servicer.Rotate,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RotateCertificateRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RotateCertificateResponse.SerializeToString,
            ),
            'Install': grpc.stream_stream_rpc_method_handler(
                    servicer.Install,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.InstallCertificateRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.InstallCertificateResponse.SerializeToString,
            ),
            'GetCertificates': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCertificates,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.GetCertificatesRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.GetCertificatesResponse.SerializeToString,
            ),
            'RevokeCertificates': grpc.unary_unary_rpc_method_handler(
                    servicer.RevokeCertificates,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RevokeCertificatesRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RevokeCertificatesResponse.SerializeToString,
            ),
            'CanGenerateCSR': grpc.unary_unary_rpc_method_handler(
                    servicer.CanGenerateCSR,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.CanGenerateCSRRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.CanGenerateCSRResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'gnoi.certificate.CertificateManagement', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class CertificateManagement(object):
    """The Certificate Management Service exported by targets.
    The service primarily exports two main RPCs, Install & Rotate which are used
    for installation of a new certificate, and rotation of an existing
    certificate on a target, along with a few management related RPCs.
    """

    @staticmethod
    def Rotate(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/gnoi.certificate.CertificateManagement/Rotate',
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RotateCertificateRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RotateCertificateResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Install(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/gnoi.certificate.CertificateManagement/Install',
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.InstallCertificateRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.InstallCertificateResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetCertificates(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/gnoi.certificate.CertificateManagement/GetCertificates',
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.GetCertificatesRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.GetCertificatesResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RevokeCertificates(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/gnoi.certificate.CertificateManagement/RevokeCertificates',
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RevokeCertificatesRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.RevokeCertificatesResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CanGenerateCSR(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/gnoi.certificate.CertificateManagement/CanGenerateCSR',
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.CanGenerateCSRRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_cert_dot_cert__pb2.CanGenerateCSRResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
