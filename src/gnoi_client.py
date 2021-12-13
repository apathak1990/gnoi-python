from __future__ import print_function
import argparse
import grpc
import os
import sys
import inspect
from pathlib import Path
import json
import hashlib
import time

# the Python modules generated from gNOI proto file (using grpc)
import github.com.openconfig.gnoi.file.file_pb2 as file_pb
import github.com.openconfig.gnoi.file.file_pb2_grpc as file_grpc
import github.com.openconfig.gnoi.system.system_pb2 as system_pb
import github.com.openconfig.gnoi.system.system_pb2_grpc as system_grpc
import github.com.openconfig.gnoi.types.types_pb2 as pb_types
import github.com.openconfig.gnoi.types.types_pb2_grpc as types_grpc
import github.com.openconfig.gnoi.common.common_pb2 as pb_common

import github.com.openconfig.gnoi.bgp.bgp_pb2 as bgp_pb
import github.com.openconfig.gnoi.bgp.bgp_pb2_grpc as bgp_grpc

import github.com.openconfig.gnoi.interface.interface_pb2 as interface_pb
import github.com.openconfig.gnoi.interface.interface_pb2_grpc as interface_grpc

import github.com.openconfig.gnoi.layer2.layer2_pb2 as layer2_pb
import github.com.openconfig.gnoi.layer2.layer2_pb2_grpc as layer2_grpc

import github.com.openconfig.gnoi.cert.cert_pb2 as cert_pb
import github.com.openconfig.gnoi.cert.cert_pb2_grpc as cert_grpc

## python modules for Bert
import github.com.openconfig.gnoi.diag.diag_pb2 as diag_pb
import github.com.openconfig.gnoi.diag.diag_pb2_grpc as diag_grpc


from grpc.beta import implementations
import datetime
import time


def xr_setpackage_generator(filename, local_file, chunksz, version, activate, hash_method, hash_type):
    pkg = system_pb.Package(filename=filename, version=version, activate=activate)
    request = system_pb.SetPackageRequest(package=pkg)
    print('generate 1: ', request)
    yield request

    if os.path.isfile(local_file) is False:
    #    print('User error:', local_file, 'does not exist!')
        raise StopIteration
    else:
        print('I am here')

    if hash_type.lower() == 'md5':
        hasher = hashlib.md5()
    elif hash_type.lower() == 'sha256':
        hasher = hashlib.sha256()
    elif hash_type.lower() == 'sha512':
        hasher = hashlib.sha512()

    with open(local_file, 'rb') as f:
        while True:
            chunk = f.read(chunksz)
            if chunk:
                hasher.update(chunk)
                content_req = system_pb.SetPackageRequest(contents=chunk)
                yield content_req
            else:
                break

    hash_type = pb_types.HashType(method=hash_method, hash=hasher.digest())
    print('generate 3: ', hash_type)
    print('hash:', hasher.digest())
    yield system_pb.SetPackageRequest(hash=hash_type)

    raise StopIteration


def xr_setpackage_remote_download_generator(path, protocol, cred, version, activate):
    rdownload = pb_common.RemoteDownload(path=path, \
                                         protocol=protocol, credentials=cred)
    pkg = system_pb.Package(version=version, activate=activate, \
                            remote_download=rdownload)
    print('Print 1:', pkg)
    request = system_pb.SetPackageRequest(package=pkg)
    print(request)
    yield request
    raise StopIteration


def xr_fileput_generator(remote_file, local_file, permissions, chunksz, hash_method, hash_type):
    file_put_details = file_pb.PutRequest.Details(remote_file=remote_file, permissions=int(permissions, 8))
    request = file_pb.PutRequest(open=file_put_details)
    print('generate 1:', request)
    yield request

    if os.path.isfile(local_file) is False:
        print('User error: local_file does not exist:', local_file)
        raise StopIteration
    else:
        print('I am here')
    if hash_type.lower() == 'md5':
        hasher = hashlib.md5()
    elif hash_type.lower() == 'sha256':
        hasher = hashlib.sha256()
    elif hash_type.lower() == 'sha512':
        hasher = hashlib.sha512()
    with open(local_file, 'rb') as f:
        while True:
            chunk = f.read(chunksz)
            if chunk:
                hasher.update(chunk)
                content_req = file_pb.PutRequest(contents=chunk)
                yield content_req
            else:
                break

    hash_type = pb_types.HashType(method=hash_method, hash=hasher.digest())
    print('generate 3:', hash_type)
    print('hash:', hasher.digest())
    hash_req = file_pb.PutRequest(hash=hash_type)
    yield hash_req

    raise StopIteration


def get_cert_type(CertificateType):
    if CertificateType.lower() == 'ct_x509':
        return cert_pb.CertificateType.Name(1)
    elif CertificateType.lower() == 'ct_unknown':
        return cert_pb.CertificateType.Name(0)
    else:
        return 0


def get_key_type(KeyType):
    if KeyType.lower() == 'kt_rsa':
        return cert_pb.KeyType.Name(1)
    elif KeyType.lower() == 'kt_unknown':
        return cert_pb.KeyType.Name(0)
    else:
        return 0


class XrGnoi:
    def __init__(self, server, user, passwd, keep_alive_time=10000,verbose=True, tls='None'):
        print('RPC start time:', datetime.datetime.now().time())
        if tls == 'None':
            self._system = system_grpc.SystemStub(grpc.insecure_channel(server))
            self._file = file_grpc.FileStub(grpc.insecure_channel(server))
            self._bgp = bgp_grpc.BGPStub(grpc.insecure_channel(server))
            self._interface = interface_grpc.InterfaceStub(grpc.insecure_channel(server))
            self._layer2 = layer2_grpc.Layer2Stub(grpc.insecure_channel(server))
            self._cert = cert_grpc.CertificateManagementStub(grpc.insecure_channel(server))
            self._diag = diag_grpc.DiagStub(grpc.insecure_channel(server))
        else:
            f = open(tls, 'rb')
            self._creds = implementations.ssl_channel_credentials(f.read())
            cert = "ems.cisco.com"
            # options = (('grpc.ssl_target_name_override', cert,),)
            options = (('grpc.ssl_target_name_override', cert,),('grpc.keepalive_time_ms',keep_alive_time,),
            ('grpc.keepalive_timeout_ms',keep_alive_time,))
            self._system = system_grpc.SystemStub(grpc.secure_channel(server, self._creds, options))
            self._file = file_grpc.FileStub(grpc.secure_channel(server, self._creds, options))
            self._bgp = bgp_grpc.BGPStub(grpc.secure_channel(server, self._creds, options))
            self._interface = interface_grpc.InterfaceStub(grpc.secure_channel(server, self._creds, options))
            self._layer2 = layer2_grpc.Layer2Stub(grpc.secure_channel(server, self._creds, options))
            self._cert = cert_grpc.CertificateManagementStub(grpc.secure_channel(server, self._creds, options))
            self._diag = diag_grpc.DiagStub(grpc.secure_channel(server, self._creds, options))
        self._metadata = [('username', user), ('password', passwd)]
        self.verbose = verbose

    def get_subcomponent_path(self, slot=None):
        comp = pb_types.PathElem(name='component', key=[])
        comp.key['name'] = slot
        path_elem = [pb_types.PathElem(name='components'),
                     comp, pb_types.PathElem(name='state'), \
                     pb_types.PathElem(name='location'), ]
        sub = pb_types.Path(origin='openconfig-platform', elem=path_elem)
        return sub

    def get_reboot_method(self, reboot_type):
        if reboot_type.lower() == 'cold':
            return system_pb.COLD
        elif reboot_type.lower() == 'powerdown':
            return system_pb.POWERDOWN
        elif reboot_type.lower() == 'warm':
            return system_pb.WARM
        elif reboot_type.lower() == 'powerup':
            return system_pb.POWERUP
        elif reboot_type.lower() == 'unknown':
            return system_pb.UNKNOWN
        elif reboot_type.lower() == 'halt':
            return system_pb.HALT
        elif reboot_type.lower() == 'nsf':
            return system_pb.NSF
        elif reboot_type.lower() == 'reset':
            return system_pb.RESET
        else:
            print('Unknown reboot code given')
            return 8

    def get_l3Protocol(self, l3protocol):
        if l3protocol == 'ipv4':
            return 1
        elif l3protocol == 'ipv6':
            return 2
        else:
            return l3protocol

    def get_l4Protocol(self, l4protocol):
        if l4protocol == 'ICMP' or l4protocol == 'icmp':
            return 0
        elif l4protocol == 'TCP' or l4protocol == 'tcp':
            return 1
        elif l4protocol == 'UDP' or l4protocol == 'udp':
            return 2
        else:
            print('Invalid l4Protocol')
            return None

    def reboot_status(self, slot=None):
        try:
            if slot is None:
                request = system_pb.RebootStatusRequest()
                response = self._system.RebootStatus(request, metadata=self._metadata)
                return response
            else:
                subcomponent = self.get_subcomponent_path(slot=slot)
                request = system_pb.RebootStatusRequest(subcomponents=[subcomponent, ])
                # print(request)
                response = self._system.RebootStatus(request, metadata=self._metadata)
                return response
        except Exception as e:
            print('system.RebootStatus() returns error.')
            if self.verbose:
                print(e)
            return None

    def reboot(self, reboot_method, slot=None, msg='test', delay=0, force=False):
        try:
            if slot is None:
                request = system_pb.RebootRequest(method=reboot_method, delay=delay,
                                                  message=msg, force=force)
                print(request)
            else:
                subcomponent = self.get_subcomponent_path(slot=slot)
                # subcomponent1 = self.get_subcomponent_path(slot='0/1')
                # print('Reboot values :method: ',reboot_method,' delay: ',delay,' '
                # 'message: ',msg,' subcomponents: ',subcomponent,' force: ',force,'')
                request = system_pb.RebootRequest(method=reboot_method, delay=delay, message=msg,
                                                  subcomponents=[subcomponent], force=force)
            print(request)
            return self._system.Reboot(request, metadata=self._metadata)
        except Exception as e:
            print('system.Reboot(', slot, ') returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def setpackage(self, filename=None, local_file=None, chunksz=32 * 1024, version=None, \
                   activate=False, hash_type='MD5'):
        hash_method = self.return_hashtype(hash_type)
        setpackage_request_iterator = xr_setpackage_generator(filename, local_file, \
                                                              chunksz, version, activate, hash_method, hash_type)

        print('Sending SetPackage RPC')
        try:
            response = self._system.SetPackage(setpackage_request_iterator, metadata=self._metadata)
            return response
        except Exception as e:
            print('system.SetPackage() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def return_remote_download_protocol(self, protcol):
        if protcol.lower() == 'sftp':
            return pb_common.RemoteDownload.SFTP
        elif protcol.lower() == 'http':
            return pb_common.RemoteDownload.HTTP
        elif protcol.lower() == 'https':
            return pb_common.RemoteDownload.HTTPS
        elif protcol.lower() == 'scp':
            return pb_common.RemoteDownload.SCP
        elif protcol.lower() == 'unknown':
            return pb_common.RemoteDownload.UNKNOWN
        else:
            return 6

    def get_credentials(self, username, password, hashtype='MD5'):
        if hashtype.lower() == 'md5':
            hasher = hashlib.md5()
        elif hashtype.lower() == 'sha256':
            hasher = hashlib.sha256()
        elif hashtype.lower() == 'sha512':
            hasher = hashlib.sha512()

        hash_method = self.return_hashtype(hashtype)
        hash_type = pb_types.HashType(method=hash_method, hash=hasher.digest())
        return pb_types.Credentials(username=username, cleartext=password)

    def setpackage_remotedownload(self, version=None, activate=False, \
                                  path=None, protocol='sftp', cred=None):
        set_pkg_rdownload_iteator = xr_setpackage_remote_download_generator(path, protocol, cred, version, activate)
        try:
            response = self._system.SetPackage(set_pkg_rdownload_iteator, metadata=self._metadata)
            return response
        except Exception as e:
            print('system.SetPackageRemote() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def return_hashtype(self, hashtype='MD5'):
        if hashtype.lower() == 'md5':
            return pb_types.HashType.MD5
        elif hashtype.lower() == 'sha256':
            return pb_types.HashType.SHA256
        elif hashtype.lower() == 'sha512':
            return pb_types.HashType.SHA512
        else:
            return False

    def file_remove(self, remote_file):
        remove_request = file_pb.RemoveRequest(remote_file=remote_file)
        print(remove_request)
        return self._file.Remove(remove_request, metadata=self._metadata)

    def file_get(self, remote_file):
        file_get_request = file_pb.GetRequest(remote_file=remote_file)
        print(file_get_request)
        return self._file.Get(file_get_request, metadata=self._metadata)

    def clear_bgp_mode(self, bgp_mode, bgp_ip, bgp_routing_instance):
        clear_request = bgp_pb.ClearBGPNeighborRequest(address=bgp_ip, routing_instance=bgp_routing_instance,
                                                       mode=bgp_mode)
        print(clear_request)
        try:
            response = self._bgp.ClearBGPNeighbor(clear_request, metadata=self._metadata)
            return response
        except Exception as E:
            return str(E)
        # return self._bgp.ClearBGPNeighbor(clear_request, metadata=self._metadata)

    def get_interface(self, inter):
        intf1 = pb_types.PathElem(name='component', key=[])
        intf1.key['name'] = inter
        path_elem = [pb_types.PathElem(name='components'), intf1, pb_types.PathElem(name='state'),
                     pb_types.PathElem(name='location'), ]

        get_intf = pb_types.Path(origin='openconfig-platform', elem=path_elem)
        return get_intf

    def loopback_set_request(self, interface, mode):
        intf = self.get_interface(inter=interface)
        loopback_set_request = interface_pb.SetLoopbackModeRequest(mode=mode, interface=intf)
        print(loopback_set_request)
        try:
            response = self._interface.SetLoopbackMode(loopback_set_request, metadata=self._metadata)
            return response
        except Exception as E:
            return str(E)

    def loopback_get_request(self, interface):
        intf = self.get_interface(inter=interface)
        loopback_get_request = interface_pb.GetLoopbackModeRequest(interface=intf)
        print(loopback_get_request)
        try:
            response = self._interface.GetLoopbackMode(loopback_get_request, metadata=self._metadata)
            return response
        except Exception as E:
            return str(E)

    def get_oc_interface(self, inter):
        intf1 = pb_types.PathElem(name='interface', key=[])
        intf1.key['name'] = inter
        path_elem = [pb_types.PathElem(name='interfaces'), intf1, ]
        get_intf = pb_types.Path(origin='openconfig-interfaces', elem=path_elem)
        return get_intf

    def clear_interface_counter(self, interface):
        intf = self.get_oc_interface(inter=interface)
        interface_list = [intf, ]
        clear_request = interface_pb.ClearInterfaceCountersRequest(interface=interface_list)
        print(clear_request)
        try:
            response = self._interface.ClearInterfaceCounters(clear_request, metadata=self._metadata)
            return response
        except Exception as E:
            return str(E)

    def get_lldp_interface(self, inter):

        intf1 = pb_types.PathElem(name='interface', key=[])
        intf1.key['name'] = inter
        path_elem = [pb_types.PathElem(name='interfaces'), intf1, ]
        get_intf = pb_types.Path(origin='openconfig-interfaces', elem=path_elem)
        return get_intf

    def clear_lldp(self, interface):
        intf = self.get_lldp_interface(inter=interface)
        interface_list = [intf, ]
        clear_request = layer2_pb.ClearLLDPInterfaceRequest(interface=intf)
        print(clear_request)
        return self._layer2.ClearLLDPInterface(clear_request, metadata=self._metadata)

    def TracerouteRequest(self, source, destination, initial_ttl, max_ttl, wait, do_not_fragment, do_not_resolve,
                          l3protocol, l4protocol):
        try:
            traceroute_request = system_pb.TracerouteRequest(source=source, destination=destination,
                                                             initial_ttl=initial_ttl, max_ttl=max_ttl, wait=wait,
                                                             do_not_fragment=do_not_fragment,
                                                             do_not_resolve=do_not_resolve, l3protocol=l3protocol,
                                                             l4protocol=l4protocol)
            print(traceroute_request)
            response = self._system.Traceroute(traceroute_request, metadata=self._metadata)
            return response
        except Exception as e:
            print('system.TracerouteRequest() returns error.')
            if self.verbose:
                print(e)
            return None

    def PingRequest(self, destination, source, count, interval, wait, size, do_not_fragment, do_not_resolve,
                    l3protocol):
        try:
            ping_request = system_pb.PingRequest(destination=destination, source=source, count=count, interval=interval,
                                                 wait=wait, do_not_fragment=do_not_fragment,
                                                 do_not_resolve=do_not_resolve, l3protocol=l3protocol, size=size)
            print(ping_request)
            response = self._system.Ping(ping_request, metadata=self._metadata)
            return response
        except Exception as e:
            print('system.PingRequest() returns error.')
            if self.verbose:
                print(e)
            return None

    def time_request(self):
        try:
            time_request = system_pb.TimeRequest()
            print(time_request)
            response = self._system.Time(time_request, metadata=self._metadata)
            return response
        except Exception as e:
            print('system.Time() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def switch_control_processor(self, slot=None):
        try:
            control_processor = self.get_subcomponent_path(slot=slot)
            request = system_pb.SwitchControlProcessorRequest(control_processor=control_processor)
            print(request)
            return self._system.SwitchControlProcessor(request, metadata=self._metadata)
        except Exception as e:
            print('system.SwitchControlProcessor(', slot, ') returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def file_TransferToRemote(self, Local_file, rdownload_protocol, rdownloadpath, rdownload_username,
                              rdownload_password):
        download_protocol = self.return_remote_download_protocol(rdownload_protocol)
        # password = pb_types.Credentials_Cleartext(Cleartext=rdownload_password)
        credentials = pb_types.Credentials(username=rdownload_username, cleartext=rdownload_password)
        # credentials = system.get_credentials(args.rdownload_username,args.rdownload_password)
        remote_download = pb_common.RemoteDownload(path=rdownloadpath, protocol=download_protocol,
                                                   credentials=credentials)
        TransferToRemote_request = file_pb.TransferToRemoteRequest(local_path=Local_file,
                                                                   remote_download=remote_download)
        print(TransferToRemote_request)
        try:
            return self._file.TransferToRemote(TransferToRemote_request, metadata=self._metadata)
        except Exception as e:
            print(str(e))

    def file_put(self, remote_file=None, local_file=None, permissions=None, chunksz=32 * 1024, hash_type='MD5'):
        hash_method = self.return_hashtype(hash_type)
        fileput_request_iterator = xr_fileput_generator(remote_file, local_file, permissions, \
                                                        chunksz, hash_method, hash_type)

        print('Sending FilePut RPC')
        try:
            print('Sending FilePut RPC 2')
            response = self._file.Put(fileput_request_iterator, metadata=self._metadata)
            print('Sending FilePut RPC 3')
            return response
        except Exception as e:
            print('file.Put() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def file_stat(self, file_path):
        file_stat_request = file_pb.StatRequest(path=file_path)
        print(file_stat_request)
        return self._file.Stat(file_stat_request, metadata=self._metadata)

    def cert_rotate(self, CertificateType, MinKeySize, KeyType, CommonName, Country, State, City, Organization,
                    OrganizationalUnit, IpAddress, EmailId, CertificateId, Certificate, PrivateKey, PublicKey):
        cert_rotate_request_iterator = xr_installcert_generator(CertificateType, MinKeySize, KeyType, CommonName, \
                                                                Country, State, City, Organization, OrganizationalUnit, \
                                                                IpAddress, EmailId, CertificateId, Certificate, \
                                                                PrivateKey, PublicKey)

        # next(cert_rotate_request_iterator)
        print('Sending RotateCert RPC')
        try:
            response = self._cert.Install(cert_rotate_request_iterator, metadata=self._metadata)

            print('cert.Rotate past this point')
            return response
        except Exception as e:
            print('cert.Rotate() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def get_cert_request(self):
        get_cert_request = cert_pb.GetCertificatesRequest()

        print('Sending GetCert RPC')
        try:
            response = self._cert.GetCertificates(get_cert_request, metadata=self._metadata)
            return response
        except Exception as e:
            print('cert.Get() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return -1

    def cert_revoke(self, CertificateId):
        cert_revoke_request = cert_pb.RevokeCertificatesRequest(certificate_id=CertificateId)

        print('Sending RotateCert RPC')
        try:
            response = self._cert.RevokeCertificates(cert_revoke_request, metadata=self._metadata)
            return response
        except Exception as e:
            print('cert.Rotate() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def cert_can_generate_csr(self, KeyType, CertificateType, KeySize):
        can_generate_csr_request = cert_pb.CanGenerateCSRRequest(key_type=KeyType, certificate_type=CertificateType, \
                                                                 key_size=KeySize)

        print('Sending CanGenerateCSR RPC')
        try:
            response = self._cert.CanGenerateCSR(can_generate_csr_request, metadata=self._metadata)
            return response
        except Exception as e:
            print('cert.CanGenerateCSR() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None


    ##prbs procs
    def return_prbs_polynomial(self,prbs_pattern):
        if prbs_pattern.lower() == 'pn31':
            return diag_pb.PRBS_POLYNOMIAL_PRBS31
        elif prbs_pattern.lower() == 'pn23':
            return diag_pb.PRBS_POLYNOMIAL_PRBS23
        elif prbs_pattern.lower() == 'pn7':
            return diag_pb.PRBS_POLYNOMIAL_PRBS7
        elif prbs_pattern.lower() == 'pn9':
            return diag_pb.PRBS_POLYNOMIAL_PRBS9
        elif prbs_pattern.lower() == 'pn15':
            return diag_pb.PRBS_POLYNOMIAL_PRBS15
        elif prbs_pattern.lower() == 'pn20':
            return diag_pb.PRBS_POLYNOMIAL_PRBS20
        else:
            return diag_pb.PRBS_POLYNOMIAL_PRBS31

    def get_interface_path(self,intf_id):
        # logical_channel_id = list(args.logical_channel_id.split(','))
        # for channel_id in logical_channel_id:
        comp=pb_types.PathElem(name='channel',key=[])
        comp.key['index'] = intf_id
        path_elem = [pb_types.PathElem(name='terminal-device'),
                     pb_types.PathElem(name='logical-channels'),comp]
        intf_idx = pb_types.Path(elem=path_elem)
        return intf_idx

    def per_port_request(self,operation,logical_channel_id,prbs_pattern=None,test_duration=None):
        # logical_channel_id = list(logical_channel_id.split(','))
        # for channel_id in logical_channel_id:
        prbs_interface = self.get_interface_path(logical_channel_id)
        if operation == 'startbert':
            pattern_prbs = self.return_prbs_polynomial(prbs_pattern)
            per_port_request = diag_pb.StartBERTRequest.PerPortRequest(interface=prbs_interface,
                                                                       prbs_polynomial=pattern_prbs,
                                                                       test_duration_in_secs=test_duration)
            #print('Per Port request', per_port_request)
        elif operation == 'stopbert':
            per_port_request = diag_pb.StopBERTRequest.PerPortRequest(interface=prbs_interface)
        elif operation == 'getbertresult':
            per_port_request = diag_pb.GetBERTResultRequest.PerPortRequest(interface=prbs_interface)
        print('per_port_request for ',operation,' is \n',per_port_request)
        return per_port_request

    def startbert(self,logical_channel_id,prbs_pattern,test_duration,bert_operation_id):
        try:
            per_port_request_list=[]
            logical_channel_id = list(logical_channel_id.split(','))
            prbs_pattern = list(prbs_pattern.split(','))
            test_duration = list(test_duration.split(','))
            test_duration = [int(i) for i in test_duration]
            for channel_id,pattern,duration in zip(logical_channel_id,prbs_pattern,test_duration):
                per_port_request_list.append(self.per_port_request('startbert',channel_id,prbs_pattern=pattern,test_duration=duration))
            request = diag_pb.StartBERTRequest(per_port_requests=per_port_request_list,bert_operation_id=bert_operation_id)
            #print(request)
            return self._diag.StartBERT(request, metadata=self._metadata)
        except Exception as e:
            print('Diag.StartBert returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None
    def stopbert(self,logical_channel_id,bert_operation_id):
        try:
            per_port_request_list=[]
            logical_channel_id = list(logical_channel_id.split(','))
            for channel_id in logical_channel_id:
                per_port_request_list.append(self.per_port_request('stopbert',channel_id))
            request = diag_pb.StopBERTRequest(per_port_requests=per_port_request_list,bert_operation_id=bert_operation_id)
            print(request)
            return self._diag.StopBERT(request,metadata=self._metadata)
        except Exception as e:
            print('Diag.StopBERT returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def getbertresult(self,logical_channel_id,bert_operation_id,result_from_all_ports=False):
        try:
            if result_from_all_ports == 'True':
                result_from_all_ports = True
                request = diag_pb.GetBERTResultRequest(bert_operation_id=bert_operation_id,result_from_all_ports=result_from_all_ports)
                # request = diag_pb.GetBERTResultRequest(result_from_all_ports=result_from_all_ports)
            else:
                per_port_request_list = []
                logical_channel_id = list(logical_channel_id.split(','))
                for channel_id in logical_channel_id:
                    per_port_request_list.append(self.per_port_request('getbertresult', channel_id))
                request = diag_pb.GetBERTResultRequest(per_port_requests=per_port_request_list,bert_operation_id=bert_operation_id)
            return self._diag.GetBERTResult(request,metadata=self._metadata)
        except Exception as e:
            print('Diag.GetBERTResult returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None


def run():
    parser = argparse.ArgumentParser(description='Python gnoi client:')
    parser.add_argument('operation', default='test',
                        help='define the operation. Can be removefile,rebootstatus,fileGet,reboot,set-package,set-package_remote')
    parser.add_argument('server', help='ipaddress of the DUT', )
    parser.add_argument('port', help='grpc port default 57400')
    parser.add_argument('--file', nargs='?', default='disk0:/test.log', help='on-router filename')
    parser.add_argument('--user', nargs='?', default='root', help='login userid')
    parser.add_argument('--passwd', nargs='?', default='lab', help='password')
    parser.add_argument('--remote_file', nargs='?', default='/tmp/test_stream.txt', help='remove_file_absolute_path')
    parser.add_argument('--remote_package', nargs='?', default='/ws/avpathak-bgl/ncs1004-mini-x-7.0.1.117I.iso',
                        help='remote_package_absolute_path')
    parser.add_argument('--reboot_delay', nargs='?', default='0', help='delay in nanoseconds')
    parser.add_argument('--rebootmethod', nargs='?', default='COLD', help='rebootmethod')
    parser.add_argument('--slot', nargs='?', default=None, help='Subcomponent')
    parser.add_argument('--verbose', nargs='?', default=True, help='verbose')
    parser.add_argument('--reboot_message', nargs='?', default='Test Reboot', help='Reboot Message string')
    parser.add_argument('--reboot_force', nargs='?', default='no', help='Force Reboot')
    parser.add_argument('--activate_package', nargs='?', default='no', help='Package_activation_flag')
    parser.add_argument('--hash_type', nargs='?', default='MD5',
                        help='hash type for setpakcage can be MD5 , SHA256, SHA512')
    parser.add_argument('--rdownload_protocol', nargs='?', default='sftp',
                        help='protocol for remotedownload for setpackge rpc can be sftp,scp,http,https,unknown')
    parser.add_argument('--rdownloadpath', nargs='?', default='dummy_path',
                        help='path of remote image as per protocol defined sftp,scp,http,https,unknown')
    parser.add_argument('--rdownload_username', nargs='?', default='test', help='username for remote download')
    parser.add_argument('--rdownload_password', nargs='?', default='test123', help='username for remote download')
    parser.add_argument('--tls', nargs='?', default='None', help='tls file for transport security')

    # Clear BGP related CLI options
    parser.add_argument('--bgp_mode', nargs='?', default='SOFT', help='BGP mode')
    parser.add_argument('--bgpIp', nargs='?', default="", help='BGP IP')
    parser.add_argument('--routing_instance', nargs='?', default="", help='BGP routing instance')

    # Set Loopback Interface CLI options
    parser.add_argument('--interface', nargs='?', default='', help='Interface Name')
    parser.add_argument('--mode', nargs='?', default='', help='Interface Mode')

    # Get Loopback Interface CLI options
    parser.add_argument('--interface_get', nargs='?', default='', help='Interface Name')

    # Clear Loopback Interface
    parser.add_argument('--interface_clear', nargs='?', default='', help='Interface Name')

    # Clear LLDP Interface
    parser.add_argument('--interface_lldp', nargs='?', default='', help='Interface Name')

    # Traceroute
    parser.add_argument('--destination', nargs='?', default='None', help='ping destination address')
    parser.add_argument('--source', nargs='?', default='', help='ping source address')
    parser.add_argument('--count', nargs='?', default=0, help='number of ping packets')
    parser.add_argument('--interval', nargs='?', default=0, help='Nanoseconds between ping requests')
    parser.add_argument('--wait', nargs='?', default=0, help='Nanoseconds to wait for a ping response')
    parser.add_argument('--size', nargs='?', default=0, help='Size of ping request packet. (excluding ICMP header)')
    parser.add_argument('--do_not_fragment', nargs='?', default=False,
                        help='Boolean to set the do not fragment bit. (IPv4 destinations)')
    parser.add_argument('--do_not_resolve', nargs='?', default=False,
                        help='Boolean to not try to resolve the address returned.')
    parser.add_argument('--l3protocol', nargs='?', default='ipv4', help='Layer3 protocol: ipv4 or ipv6.(default=ipv4)')
    parser.add_argument('--initial_ttl', nargs='?', default='1', help='Initial TTL. (default=1)')
    parser.add_argument('--max_ttl', nargs='?', default='30', help='Maximum number of hops. (default=30)')
    parser.add_argument('--l4protocol', nargs='?', default='UDP',
                        help='Layer4 protocol: ICMP, TCP or UDP. (default=UDP)')

    # FilePut
    parser.add_argument('--permissions', nargs='?', default='777',
                        help='file permissions. ex. 775: user read/write/execute, group read/write/execute, global read/execute.')

    # FileState
    parser.add_argument('--path', nargs='?', default='disk0:/', help='on-router filename')

    # Install
    parser.add_argument('--CertificateType', nargs='?', default='',
                        help='The type of certificate which will be associated for this CSR.')
    parser.add_argument('--MinKeySize', nargs='?', default='',
                        help='Minimum size of the key to be used by the target when generating a public/private key pair.')
    parser.add_argument('--KeySize', nargs='?', default='',
                        help='Size of the key to be used by the target when generating a csr')
    parser.add_argument('--KeyType', nargs='?', default='', help='The type of key the target must use.')
    parser.add_argument('--CommonName', nargs='?', default='', help='(eg, your name or your servers hostname)')
    parser.add_argument('--Country', nargs='?', default='US', help='Country Name (2 letter code). (default=US)')
    parser.add_argument('--State', nargs='?', default='CA', help='State or Province Name. (default=CA)')
    parser.add_argument('--City', nargs='?', default='', help='Locality Name (eg, city). ')
    parser.add_argument('--Organization', nargs='?', default='', help='Organization Name (eg, company).')
    parser.add_argument('--OrganizationalUnit', nargs='?', default='', help='Organizational Unit Name (eg, section).')
    parser.add_argument('--IpAddress', nargs='?', default='', help='Server IP Address.')
    parser.add_argument('--EmailId', nargs='?', default='', help='POC Email Address.')
    parser.add_argument('--CertificateId', nargs='?', default='', help='Id with which this CSR will be associated')
    parser.add_argument('--Certificate', nargs='?', default='', help='The actual Certificate.')
    parser.add_argument('--PrivateKey', nargs='?', default='', help='Private encryption key.')
    parser.add_argument('--PublicKey', nargs='?', default='', help='Public encryption key.')

    ##BERT parameters
    parser.add_argument('--bert_operation_id', nargs='?', default='Prbs_test', help='Bert operation id')
    parser.add_argument('--prbs_pattern', nargs='?', default='pn31', help='PRBS pattern to test')
    parser.add_argument('--logical_channel_id', nargs='?', default=None,
                        help='Logical channel index from OC-terminal-device')
    parser.add_argument('--test_duration', nargs='?', default=60, help='PRBS test duration in secs')
    parser.add_argument('--result_from_all_ports', nargs='?', default=False, help='Gets PRBS results from all ports')


    ## KeepAlive Parameters
    parser.add_argument('--keepalive_time',nargs='?', default=10000, help='Keepalive Timer in MS')
    parser.add_argument('--keepalive_timeout',nargs='?', default=10000, help='Keepalive Timeout in MS')

    args = parser.parse_args()
    metadata = [('username', args.user), ('password', args.passwd)]
    host = '%s:%d' % (args.server, int(args.port))
    print('###############################')
    print('RPC to %s' % host)
    print('RPC start time:', datetime.datetime.now().time())

    if (args.operation == 'removefile'):
        file_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose, tls=args.tls)
        print('========File-Remove Request==============')
        try:
            response = file_obj.file_remove(remote_file=args.file)
            print('========File Remove Response=============')
            print('RPC end time:', datetime.datetime.now().time())
            print(response)
            print('File removal  %s successful' % args.file)
        except Exception as e:
            print('Exception seen: \n %s' % e)
    elif (args.operation == 'rebootstatus'):
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                        verbose=args.verbose, tls=args.tls)
        print('========Reboot-Status Request==============')
        response = system.reboot_status(slot=args.slot)
        print('RPC end time:', datetime.datetime.now().time())
        print('========Reboot-status Response=============')
        print('Active : %s' % response.active)
        print('Wait : %s' % response.wait)
        print('When : %s' % response.when)
        print('Reason : %s' % response.reason)
        print('Count : %s' % response.count)
    elif (args.operation == 'fileGet'):
        print('========File get Request=============')
        file_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose, tls=args.tls)
        file_get_response = file_obj.file_get(args.file)
        f = open("%s" % args.remote_file, mode='w+b')
        print('========File get Response=============')
        try:
            for filestream in file_get_response:
                f.write(filestream.contents)
                print(filestream.hash)
            f.close()
        except Exception as e:
            print('Exception seen:\n %s' % e)
        print('RPC end time:', datetime.datetime.now().time())
    elif (args.operation == 'reboot'):
        print('========Reboot Request=============')
        force_reboot = False
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                        verbose=args.verbose, tls=args.tls)
        reboot_method = system.get_reboot_method(args.rebootmethod)
        print('Reboot method set is ', reboot_method)
        if args.reboot_force.lower() == 'yes':
            force_reboot = True
        reboot_delay = int(args.reboot_delay)
        response = system.reboot(reboot_method, slot=args.slot, msg=args.reboot_message,
                                 delay=reboot_delay, force=force_reboot)
        print('========Reboot Response=============')
        print('RPC end time:', datetime.datetime.now().time())
        print(response)
    elif (args.operation == 'set-package'):
        print('========SetPackage Request=============')
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                        verbose=args.verbose, tls=args.tls)
        pkg_act_flag = True
        if args.activate_package.lower() == 'no':
            pkg_act_flag = False

        response = system.setpackage(filename=args.remote_package, local_file=args.file, activate=pkg_act_flag,
                                     hash_type=args.hash_type)
        print('RPC end time:', datetime.datetime.now().time())
        print(response)
    elif (args.operation == 'set-package_remote'):
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                        verbose=args.verbose, tls=args.tls)
        pkg_act_flag = True
        if args.activate_package.lower() == 'no':
            pkg_act_flag = False

        protocol = system.return_remote_download_protocol(args.rdownload_protocol)
        credentials = system.get_credentials(args.rdownload_username, args.rdownload_password)
        response = system.setpackage_remotedownload(path=args.rdownloadpath, protocol=protocol, activate=pkg_act_flag,
                                                    cred=credentials)
        print('RPC end time:', datetime.datetime.now().time())
        print(response)

    elif args.operation == 'clearbgp':
        if args.bgp_mode:
            print("=============Clear BGP request==============")
            bgp = XrGnoi(server=host, user=args.user, passwd=args.passwd, verbose=args.verbose, tls=args.tls)
            request_bgp = bgp.clear_bgp_mode(args.bgp_mode, args.bgpIp, args.routing_instance)
            print("======= Clear BGP Response =======")
            print(request_bgp)

    elif args.operation == 'SetLoopback':
        if args.interface:
            print("===========SetLoopback Request=============")
            interface = XrGnoi(server=host, user=args.user, passwd=args.passwd, verbose=args.verbose, tls=args.tls)
            interface_set = interface.loopback_set_request(args.interface, args.mode)
            print("======Set Loopback Interface======")
            print(interface_set)

    elif args.operation == 'GetLoopback':
        if args.interface_get:
            print("=============Get Loopback Request============")
            interface = XrGnoi(server=host, user=args.user, passwd=args.passwd, verbose=args.verbose, tls=args.tls)
            interface_get = interface.loopback_get_request(args.interface_get)
            print("=======Get Loopback Interface=======")
            print(interface_get)


    elif args.operation == 'ClearInterface':
        if args.interface_clear:
            print("=========Clear Interface Counters==========")
            interface = XrGnoi(server=host, user=args.user, passwd=args.passwd, verbose=args.verbose, tls=args.tls)
            interface_clear = interface.clear_interface_counter(args.interface_clear)
            print("=========Clear Interface Counters Response==========")
            print(interface_clear)

    elif args.operation == 'ClearLLDP':
        if args.interface_lldp:
            print("=========Clear LLDP==========")
            layer2 = XrGnoi(server=host, user=args.user, passwd=args.passwd, verbose=args.verbose, tls=args.tls)
            try:
                lldp_clear = layer2.clear_lldp(args.interface_lldp)
                print("============Clear LLDP Request=============")
                print(lldp_clear)
            except Exception as E:
                print("============Clear LLDP Request=============")
                print(str(E))


    # GNOI Phase 2 starts here
    elif (args.operation == 'Traceroute'):
        print('========Traceroute Request=============')
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd, verbose=args.verbose, tls=args.tls)

        traceroute_response = system.TracerouteRequest(args.source, args.destination, int(args.initial_ttl),
                                                       int(args.max_ttl), int(args.wait), bool(args.do_not_fragment),
                                                       bool(args.do_not_resolve),
                                                       system.get_l3Protocol(args.l3protocol),
                                                       system.get_l4Protocol(args.l4protocol))
        print('========Traceroute Response=============')
        print('RPC end time:', datetime.datetime.now().time())
        try:
            for traceroute_stream in traceroute_response:
                print(traceroute_stream)
                # f.write(filestream.contents)
            # f.close()
        except Exception as e:
            print('Exception seen:\n %s' % e)

    elif (args.operation == 'Ping'):
        print('========Ping Request=============')
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                        verbose=args.verbose, tls=args.tls)

        ping_response = system.PingRequest(args.destination, args.source, int(args.count), int(args.interval),
                                           int(args.wait), int(args.size), bool(args.do_not_fragment),
                                           bool(args.do_not_resolve), system.get_l3Protocol(args.l3protocol))
        print('========Ping Response=============')
        print('RPC end time:', datetime.datetime.now().time())
        try:
            for Pingstream in ping_response:
                print(Pingstream)
        except Exception as e:
            print('Exception seen:\n %s' % e)

    elif (args.operation == 'Time'):
        print('========Time Request=============')
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                        verbose=args.verbose, tls=args.tls)
        time_response = system.time_request()
        print('========Time Response=============')
        print('RPC end time:', datetime.datetime.now().time())

        print('Target Time : %s' % time.ctime(time_response.time / 1000000000))
        print(time.ctime(time.time()))
        print(time_response.time / 1000000000)
        print(time.time())

    elif (args.operation == 'SwitchControlProcessor'):
        print('========SwitchControlProcessor Request=============')
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                        verbose=args.verbose, tls=args.tls)
        response = system.switch_control_processor(slot=args.slot)
        print('========SwitchControlProcessor Response=============')
        print('RPC end time:', datetime.datetime.now().time())
        print(response)

    elif (args.operation == 'TransferToRemote'):
        print('========File Transfer To Remote Request=============')
        file_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose, tls=args.tls)

        TransferToRemote_response = file_obj.file_TransferToRemote(args.file, args.rdownload_protocol,
                                                                   args.rdownloadpath, args.rdownload_username,
                                                                   args.rdownload_password)
        print('========File Transfer To Remote Response=============')
        try:
            if TransferToRemote_response.hash:
                print(TransferToRemote_response.hash)
        except Exception as e:
            print('Exception seen in File Transfer To Remote Response:\n %s' % e)
        print('RPC end time:', datetime.datetime.now().time())

    elif (args.operation == 'filePut'):
        file_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose, tls=args.tls)
        # file_put_request_details = file_pb.PutRequest_Details(RemoteFile=args.file, Permissions=args.permissions)
        file_put_response = file_obj.file_put(remote_file=args.remote_file, local_file=args.file,
                                              permissions=args.permissions)
        print('========File put Request=============')
        try:
            print('========File put Response=============')
            print('RPC end time:', datetime.datetime.now().time())
            print(file_put_response)
            if 'MD5' in file_put_response:
                print('File put  %s successful' % args.file)
        except Exception as e:
            print('Exception seen: \n %s' % e)

    elif (args.operation == 'fileStat'):
        print('========File Stat Request=============')
        file_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose, tls=args.tls)
        try:
            file_stat_response = file_obj.file_stat(args.path)
            print('========File Stat Response=============')
            # print(file_stat_response)
            stat_info = file_stat_response.stats
            for stat in stat_info:
                print('Path:', stat.path)
                # print('LastModified:', stat.last_modified)
                # print('Target Time : %s'%time.ctime(time_response.time / 1000000000))
                print('LastModified: %s' % time.ctime(stat.last_modified / 1000000000))
                print('Permissions:', stat.permissions)
                print('Size:', stat.size)
                print('Umask:', stat.umask)
            return (stat.path, stat.permissions, stat.size, (stat.last_modified / 1000000000))
        except Exception as e:
            print('========File Stat Response=============')
            print(str(e))



    elif (args.operation == 'GetCertificates'):
        cert_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose, tls=args.tls)
        print('========Get Certificate Request=============')
        get_cert_response = cert_obj.get_cert_request()
        try:

            print('========Get Certificate Response=============')
            print('RPC end time:', datetime.datetime.now().time())
            # print(get_cert_response.certificate_info)
            if (get_cert_response == -1):
                print('GetCertificates Failed')
            else:
                print(get_cert_response)
                print('Get Certificate  %s successful' % args.CommonName)
        except Exception as e:
            print('Exception seen: \n %s' % e)
    elif (args.operation == 'RevokeCertificate'):
        cert_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose, tls=args.tls)
        print('========Certificate Revoke Request=============')
        cert_revoke_response = cert_obj.cert_revoke(CertificateId=args.CertificateId.split(','))
        try:
            print('========Certificate Revoke Response=============')
            print('RPC end time:', datetime.datetime.now().time())
            print(cert_revoke_response)
            print('Certificate Revoke  %s successful' % args.CommonName)
        except Exception as e:
            print('Exception seen: \n %s' % e)

    elif (args.operation == 'CanGenerateCSR'):
        cert_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose, tls=args.tls)
        print('========Certificate CanGenerateCSR Request=============')
        cert_type = get_cert_type(args.CertificateType)
        key_type = get_key_type(args.KeyType)
        can_generate_csr_response = cert_obj.cert_can_generate_csr(KeyType=key_type, CertificateType=cert_type, \
                                                                   KeySize=int(args.KeySize))
        try:
            print('========Certificate CanGenerateCSR Response=============')
            print('RPC end time:', datetime.datetime.now().time())
            if can_generate_csr_response:
                print('Target will generate csr with Cert Type: %s, Key Type: %s, Key Size: %s' \
                      % (cert_type, key_type, args.KeySize))
                print('Certificate CanGenerateCSR successful', can_generate_csr_response)
            else:
                print('Target will not generate csr with Cert Type: %s, Key Type: %s, Key Size: %s' \
                      % (cert_type, key_type, args.KeySize))
                print('Certificate CanGenerateCSR  not successful', can_generate_csr_response)
            print(can_generate_csr_response)
        except Exception as e:
            print('Exception seen: \n %s' % e)

##BERT ccode
    elif (args.operation == 'startbert'):
        diag = XrGnoi(server=host,user=args.user,passwd=args.passwd,
                      verbose=args.verbose,tls=args.tls)
        #test_duration = int(args.test_duration)

        # logical_channel_id = list(args.logical_channel_id.split(','))
        # for channel_id in logical_channel_id:
        response = diag.startbert(args.logical_channel_id,args.prbs_pattern,args.test_duration,args.bert_operation_id)
        print('######################')
        print('Diag.StartBert Response\n')
        print(response.bert_operation_id)
        print(response.per_port_responses)
        print('RPC end time:', datetime.datetime.now().time())
        print('RPC end time:', datetime.datetime.utcnow())

    elif (args.operation == 'stopbert'):
        diag = XrGnoi(server=host,user=args.user,passwd=args.passwd,
                      verbose=args.verbose,tls=args.tls)
        response = diag.stopbert(args.logical_channel_id,args.bert_operation_id)
        print('STOPEBERT RESPONSE \n', response)
        print('######################')
        print('Diag.StopBert Response\n')
        ##TODO###S/W issue no response on stop bert
        print(response.bert_operation_id)
        print(response.per_port_responses)
        print('RPC end time:', datetime.datetime.now().time())
        print('RPC end time:', datetime.datetime.utcnow())
    ###TODO Code for GetBertResults for each values
    elif (args.operation == 'getbertresult'):
        diag = XrGnoi(server=host,user=args.user,passwd=args.passwd,
                      verbose=args.verbose,tls=args.tls)
        response = diag.getbertresult(args.logical_channel_id,args.bert_operation_id,args.result_from_all_ports)
        print('GETBERTRESULT RESPONSE\n')
        print('######################')
        #print(response)
        for res in response.per_port_responses:
            print('BERT interface %s'%res.interface)
            print('BERT status %s'%res.status)
            print('BERT bert_operation_id %s'%res.bert_operation_id)
            print('BERT prbs_polynomial %s'%res.prbs_polynomial)
            print('BERT last_bert_start_timestamp %s'%res.last_bert_start_timestamp)
            print('BERT last_bert_get_result_timestamp %s'%res.last_bert_get_result_timestamp)
            print('BERT peer_lock_established %s'%res.peer_lock_established)
            print('BERT peer_lock_lost %s'%res.peer_lock_lost)
            print('BERT total_errors %s'%res.total_errors)
            print('BERT error_count_per_minute %s'%res.error_count_per_minute)
            #print('%s'%res)
            # for per_min in res.error_count_per_minute:
            #     print('BERT error_count_per_minute %s'%per_min)

        print('RPC end time:', datetime.datetime.now().time())
        print('RPC end time:', datetime.datetime.utcnow())


if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())
    run()
