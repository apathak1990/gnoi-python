# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from github.com.openconfig.gnoi.system import system_pb2 as github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2


class SystemStub(object):
    """The gNOI service is a collection of operational RPC's that allow for the
    management of a target outside of the configuration and telemetry pipeline.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Ping = channel.unary_stream(
                '/gnoi.system.System/Ping',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.PingRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.PingResponse.FromString,
                )
        self.Traceroute = channel.unary_stream(
                '/gnoi.system.System/Traceroute',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TracerouteRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TracerouteResponse.FromString,
                )
        self.Time = channel.unary_unary(
                '/gnoi.system.System/Time',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TimeRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TimeResponse.FromString,
                )
        self.SetPackage = channel.stream_unary(
                '/gnoi.system.System/SetPackage',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SetPackageRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SetPackageResponse.FromString,
                )
        self.SwitchControlProcessor = channel.unary_unary(
                '/gnoi.system.System/SwitchControlProcessor',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SwitchControlProcessorRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SwitchControlProcessorResponse.FromString,
                )
        self.Reboot = channel.unary_unary(
                '/gnoi.system.System/Reboot',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootResponse.FromString,
                )
        self.RebootStatus = channel.unary_unary(
                '/gnoi.system.System/RebootStatus',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootStatusRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootStatusResponse.FromString,
                )
        self.CancelReboot = channel.unary_unary(
                '/gnoi.system.System/CancelReboot',
                request_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.CancelRebootRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.CancelRebootResponse.FromString,
                )


class SystemServicer(object):
    """The gNOI service is a collection of operational RPC's that allow for the
    management of a target outside of the configuration and telemetry pipeline.
    """

    def Ping(self, request, context):
        """Ping executes the ping command on the target and streams back
        the results.  Some targets may not stream any results until all
        results are in.  If a packet count is not explicitly provided,
        5 is used.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Traceroute(self, request, context):
        """Traceroute executes the traceroute command on the target and streams back
        the results.  Some targets may not stream any results until all
        results are in.  If a hop count is not explicitly provided,
        30 is used.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Time(self, request, context):
        """Time returns the current time on the target.  Time is typically used to
        test if a target is actually responding.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetPackage(self, request_iterator, context):
        """SetPackage places a software package (possibly including bootable images)
        on the target. The file is sent in sequential messages, each message
        up to 64KB of data. A final message must be sent that includes the hash
        of the data sent. An error is returned if the location does not exist or
        there is an error writing the data. If no checksum is received, the target
        must assume the operation is incomplete and remove the partially
        transmitted file. The target should initially write the file to a temporary
        location so a failure does not destroy the original file.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SwitchControlProcessor(self, request, context):
        """SwitchControlProcessor will switch from the current route processor to the
        provided route processor. If the current route processor is the same as the
        one provided it is a NOOP. If the target does not exist an error is
        returned.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Reboot(self, request, context):
        """Reboot causes the target to reboot, possibly at some point in the future.
        If the method of reboot is not supported then the Reboot RPC will fail.
        If the reboot is immediate the command will block until the subcomponents
        have restarted.
        If a reboot on the active control processor is pending the service must
        reject all other reboot requests.
        If a reboot request for active control processor is initiated with other
        pending reboot requests it must be rejected.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RebootStatus(self, request, context):
        """RebootStatus returns the status of reboot for the target.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CancelReboot(self, request, context):
        """CancelReboot cancels any pending reboot request.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SystemServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Ping': grpc.unary_stream_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.PingRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.PingResponse.SerializeToString,
            ),
            'Traceroute': grpc.unary_stream_rpc_method_handler(
                    servicer.Traceroute,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TracerouteRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TracerouteResponse.SerializeToString,
            ),
            'Time': grpc.unary_unary_rpc_method_handler(
                    servicer.Time,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TimeRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TimeResponse.SerializeToString,
            ),
            'SetPackage': grpc.stream_unary_rpc_method_handler(
                    servicer.SetPackage,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SetPackageRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SetPackageResponse.SerializeToString,
            ),
            'SwitchControlProcessor': grpc.unary_unary_rpc_method_handler(
                    servicer.SwitchControlProcessor,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SwitchControlProcessorRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SwitchControlProcessorResponse.SerializeToString,
            ),
            'Reboot': grpc.unary_unary_rpc_method_handler(
                    servicer.Reboot,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootResponse.SerializeToString,
            ),
            'RebootStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.RebootStatus,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootStatusRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootStatusResponse.SerializeToString,
            ),
            'CancelReboot': grpc.unary_unary_rpc_method_handler(
                    servicer.CancelReboot,
                    request_deserializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.CancelRebootRequest.FromString,
                    response_serializer=github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.CancelRebootResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'gnoi.system.System', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class System(object):
    """The gNOI service is a collection of operational RPC's that allow for the
    management of a target outside of the configuration and telemetry pipeline.
    """

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/gnoi.system.System/Ping',
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.PingRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.PingResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Traceroute(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/gnoi.system.System/Traceroute',
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TracerouteRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TracerouteResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Time(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/gnoi.system.System/Time',
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TimeRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.TimeResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetPackage(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/gnoi.system.System/SetPackage',
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SetPackageRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SetPackageResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SwitchControlProcessor(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/gnoi.system.System/SwitchControlProcessor',
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SwitchControlProcessorRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.SwitchControlProcessorResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Reboot(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/gnoi.system.System/Reboot',
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RebootStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/gnoi.system.System/RebootStatus',
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootStatusRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.RebootStatusResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CancelReboot(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/gnoi.system.System/CancelReboot',
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.CancelRebootRequest.SerializeToString,
            github_dot_com_dot_openconfig_dot_gnoi_dot_system_dot_system__pb2.CancelRebootResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
