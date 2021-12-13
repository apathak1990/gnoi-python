from __future__ import print_function
import argparse
import grpc
import os
import sys
import inspect
from pathlib import Path
import json
import hashlib
import datetime

# the Python modules generated from gNOI proto file (using grpc)
import github.com.openconfig.gnoi.file.file_pb2 as file_pb
import github.com.openconfig.gnoi.file.file_pb2_grpc as file_grpc
import github.com.openconfig.gnoi.system.system_pb2 as system_pb
import github.com.openconfig.gnoi.system.system_pb2_grpc as system_grpc
import github.com.openconfig.gnoi.types.types_pb2 as pb_types
import github.com.openconfig.gnoi.types.types_pb2_grpc as types_grpc
import github.com.openconfig.gnoi.common.common_pb2 as pb_common
## python modules for Bert
import github.com.openconfig.gnoi.diag.diag_pb2 as diag_pb
import github.com.openconfig.gnoi.diag.diag_pb2_grpc as diag_grpc

from grpc.beta import implementations
import datetime
import time


def xr_setpackage_generator(filename,local_file, chunksz, version, activate, hash_method,hash_type):
    pkg = system_pb.Package(filename=filename, version=version, activate=activate)
    request = system_pb.SetPackageRequest(package=pkg)
    print('generate 1: ', request)
    yield request

    if os.path.isfile(local_file) is False:
        print('User error:', local_file, 'does not exist!')
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

def xr_setpackage_remote_download_generator(path,protocol, cred, version, activate):
    rdownload = pb_common.RemoteDownload(path=path, \
                                         protocol=protocol, credentials=cred)
    pkg = system_pb.Package(version=version, activate=activate, \
                            remote_download=rdownload)
    print('Print 1:',pkg)
    request = system_pb.SetPackageRequest(package=pkg)
    print(request)
    yield request
    raise StopIteration


class XrGnoi:
    def __init__(self, server, user, passwd, verbose=True,tls='None'):
        print('RPC start time:',datetime.datetime.now().time())
        if tls == 'None':
            self._system = system_grpc.SystemStub(grpc.insecure_channel(server))
            self._file = file_grpc.FileStub(grpc.insecure_channel(server))
            self._diag = diag_grpc.DiagStub(grpc.insecure_channel(server))
        else:
            f = open(tls, 'rb')
            self._creds = implementations.ssl_channel_credentials(f.read())
            cert = "ems.cisco.com"
            options = (('grpc.ssl_target_name_override', cert,),)
            self._system = system_grpc.SystemStub(grpc.secure_channel(server, self._creds, options))
            #self._system = system_grpc.SystemStub(grpc.secure_channel(server, self._creds))
            self._file = file_grpc.FileStub(grpc.secure_channel(server, self._creds, options))
            self._diag = diag_grpc.DiagStub(grpc.secure_channel(server, self._creds, options))
            #self._file = file_grpc.FileStub(grpc.secure_channel(server, self._creds))
        self._metadata = [('username', user), ('password', passwd)]
        self.verbose = verbose

    def get_subcomponent_path(self,slot=None):
        comp = pb_types.PathElem(name='component', key=[])
        comp.key['name'] = slot
        # path_elem = [pb_types.PathElem(name='components'),
        #              comp,pb_types.PathElem(name='state'), \
        #             pb_types.PathElem(name='location'),]
        # path_elem = [pb_types.PathElem(name='components'),
        #              comp]
        path_elem = [pb_types.PathElem(name='openconfig-platform'),pb_types.PathElem(name='components'),
                     comp,pb_types.PathElem(name='state'), \
                    pb_types.PathElem(name='location'),]


        #sub = pb_types.Path(origin='openconfig-platform', elem=path_elem)
        sub = pb_types.Path(elem=path_elem)
        return sub

    def get_reboot_method(self,reboot_type):
        if reboot_type.lower() == 'cold':
            return system_pb.COLD
        elif reboot_type.lower() == 'powerdown':
            return  system_pb.POWERDOWN
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

    def reboot_status(self,slot=None):
        try:
            if slot is None:
                request = system_pb.RebootStatusRequest()
                response = self._system.RebootStatus(request, metadata=self._metadata)
                return response
            else:
                subcomponent = self.get_subcomponent_path(slot=slot)
                request = system_pb.RebootStatusRequest(subcomponents=[subcomponent,])
                print(request)
                response = self._system.RebootStatus(request, metadata=self._metadata)
                return response
        except Exception as e:
            print('system.RebootStatus() returns error.')
            if self.verbose:
                print(e)
            return None

    def reboot(self,reboot_method,slot=None,  msg='test', delay=0, force=False):
        try:
            if slot is None:
                request = system_pb.RebootRequest(method=reboot_method,delay=delay,
                                                  message=msg,force=force)
                print(request)
            else:
                subcomponent = self.get_subcomponent_path(slot=slot)
                #subcomponent1 = self.get_subcomponent_path(slot='0/1')
                #print('Reboot values :method: ',reboot_method,' delay: ',delay,' '
                #'message: ',msg,' subcomponents: ',subcomponent,' force: ',force,'')
                #request = system_pb.RebootRequest(method=reboot_method,delay=delay,message=msg,
                #                                  subcomponents=[subcomponent],force=force)
                request = system_pb.RebootRequest(method=reboot_method,delay=delay,message=msg,
                                                  subcomponents=[subcomponent],force=force)

            print(request)
            return self._system.Reboot(request, metadata=self._metadata)
        except Exception as e:
            print('system.Reboot(', slot, ') returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def setpackage(self, filename=None,local_file=None, chunksz=32*1024, version=None, \
        activate=False, hash_type='MD5'):
        hash_method = self.return_hashtype(hash_type)
        setpackage_request_iterator = xr_setpackage_generator(filename,local_file, \
                    chunksz, version, activate, hash_method,hash_type)

        print('Sending SetPackage RPC')
        try:
            response = self._system.SetPackage(setpackage_request_iterator,metadata=self._metadata)
            return response
        except Exception as e:
            print('system.SetPackage() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None

    def return_remote_download_protocol(self,protcol):
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

    def get_credentials(self,username,password,hashtype='MD5'):
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
        set_pkg_rdownload_iteator = xr_setpackage_remote_download_generator(path,protocol,cred,version,activate)
        try:
            response = self._system.SetPackage(set_pkg_rdownload_iteator,metadata=self._metadata)
            return response
        except Exception as e:
            print('system.SetPackageRemote() returns error.')
            if self.verbose:
                print('Got exception: ', e)
            return None


    def return_hashtype(self,hashtype='MD5'):
        if hashtype.lower() == 'md5':
            return pb_types.HashType.MD5
        elif hashtype.lower() == 'sha256':
            return  pb_types.HashType.SHA256
        elif hashtype.lower() == 'sha512':
            return pb_types.HashType.SHA512
        else:
            return False


    def file_remove(self,remote_file):
        remove_request = file_pb.RemoveRequest(remote_file=remote_file)
        print(remove_request)
        return self._file.Remove(remove_request, metadata=self._metadata)

    def file_get(self,remote_file):
        file_get_request = file_pb.GetRequest(remote_file=remote_file)
        print(file_get_request)
        return self._file.Get(file_get_request,metadata=self._metadata)

    def return_time(self):
        time_request = system_pb.TimeRequest()
        print(time_request)
        return self._system.Time(time_request,metadata=self._metadata)

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
        # print('per_port_request for ',operation,' is \n',per_port_request)
        return per_port_request

    def startbert(self,logical_channel_id,prbs_pattern,test_duration,bert_operation_id):
        try:
            per_port_request_list=[]
            logical_channel_id = list(logical_channel_id.split(','))
            for channel_id in logical_channel_id:
                per_port_request_list.append(self.per_port_request('startbert',channel_id,prbs_pattern=prbs_pattern,test_duration=test_duration))
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
    parser.add_argument('operation',default='test',help='define the operation. Can be removefile,rebootstatus,fileGet,reboot,set-package,set-package_remote,time')
    parser.add_argument('server', help='ipaddress of the DUT', )
    parser.add_argument('port', help='grpc port default 57400' )
    parser.add_argument('--file', nargs='?',default='disk0:/test.log',help='on-router filename')
    parser.add_argument('--user', nargs='?', default='root', help='login userid')
    parser.add_argument('--passwd', nargs='?', default='lab', help='password')
    parser.add_argument('--remote_file', nargs='?', default='/tmp/test_stream.txt', help='remove_file_absolute_path')
    parser.add_argument('--remote_package', nargs='?', default='/ws/avpathak-bgl/ncs1004-mini-x-7.0.1.117I.iso', help='remote_package_absolute_path')
    parser.add_argument('--reboot_delay', nargs='?', default='0', help='delay in nanoseconds')
    parser.add_argument('--rebootmethod', nargs='?', default='COLD', help='rebootmethod')
    parser.add_argument('--slot', nargs='?', default=None, help='Subcomponent')
    parser.add_argument('--verbose', nargs='?', default=True, help='verbose')
    parser.add_argument('--reboot_message', nargs='?', default='Test Reboot', help='Reboot Message string')
    parser.add_argument('--reboot_force', nargs='?', default='no', help='Force Reboot')
    parser.add_argument('--activate_package', nargs='?', default='no', help='Package_activation_flag')
    parser.add_argument('--hash_type', nargs='?', default='MD5', help='hash type for setpakcage can be MD5 , SHA256, SHA512')
    parser.add_argument('--rdownload_protocol', nargs='?', default='sftp', help='protocol for remotedownload for setpackge rpc can be sftp,scp,http,https,unknown')
    parser.add_argument('--rdownloadpath', nargs='?', default='dummy_path', help='path of remote image as per protocol defined sftp,scp,http,https,unknown')
    parser.add_argument('--rdownload_username', nargs='?', default='test', help='username for remote download')
    parser.add_argument('--rdownload_password', nargs='?', default='test123', help='username for remote download')
    parser.add_argument('--tls', nargs='?', default='None', help='tls file for transport security')

##BERT parameters
    parser.add_argument('--bert_operation_id', nargs='?', default='Prbs_test', help='Bert operation id')
    parser.add_argument('--prbs_pattern', nargs='?', default='pn31', help='PRBS pattern to test')
    parser.add_argument('--logical_channel_id', nargs='?', default=None, help='Logical channel index from OC-terminal-device')
    parser.add_argument('--test_duration', nargs='?', default=60, help='PRBS test duration in secs')
    parser.add_argument('--result_from_all_ports', nargs='?', default=False, help='Gets PRBS results from all ports')


    args = parser.parse_args()
    metadata = [('username', args.user), ('password', args.passwd)]
    host = '%s:%d'%(args.server,int(args.port))
    print('###############################')
    print('RPC to %s'%host)
    print('RPC start time:', datetime.datetime.now().time())

    if (args.operation == 'removefile'):
        file_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose,tls=args.tls)
        print('========File-Remove Request==============')
        try:
            response = file_obj.file_remove(remote_file=args.file)
            print('========File Remove Response=============')
            print('RPC end time:', datetime.datetime.now().time())
            print(response)
            print('File removal  %s successful'%args.file)
        except Exception as e:
            print('Exception seen: \n %s'%e)
    elif (args.operation == 'rebootstatus'):
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose,tls=args.tls)
        print('========Reboot-Status Request==============')
        response = system.reboot_status(slot=args.slot)
        print('RPC end time:', datetime.datetime.now().time())
        print('========Reboot-status Response=============')
        print('Active : %s'%response.active)
        print('Wait : %s'%response.wait)
        print('When : %s'%response.when)
        print('Reason : %s'%response.reason)
        print('Count : %s'%response.count)
    elif (args.operation == 'fileGet'):
        print('========File get Request=============')
        file_obj = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose,tls=args.tls)
        file_get_response = file_obj.file_get(args.file)
        f = open("%s"%args.remote_file,mode='w+b')
        print('========File get Response=============')
        try:
            for filestream in file_get_response:
                f.write(filestream.contents)
                print(filestream.hash)
            f.close()
        except Exception as e:
            print('Exception seen:\n %s'%e)
        print('RPC end time:', datetime.datetime.now().time())
    elif (args.operation == 'reboot'):
        print('========Reboot Request=============')
        force_reboot=False
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose,tls=args.tls)
        reboot_method = system.get_reboot_method(args.rebootmethod)
        print('Reboot method set is ',reboot_method)
        if args.reboot_force.lower() == 'yes':
            force_reboot=True
        reboot_delay = int(args.reboot_delay)
        response = system.reboot(reboot_method,slot=args.slot,msg=args.reboot_message,
                                 delay=reboot_delay,force=force_reboot)
        print('========Reboot Response=============')
        print('RPC end time:', datetime.datetime.now().time())
        print(response)
    elif (args.operation == 'set-package'):
        print('========SetPackage Request=============')
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose,tls=args.tls)
        pkg_act_flag = True
        if args.activate_package.lower() == 'no':
            pkg_act_flag = False

        response = system.setpackage(filename=args.remote_package,local_file=args.file,activate=pkg_act_flag,hash_type=args.hash_type)
        print('RPC end time:', datetime.datetime.now().time())
        print(response)
    elif (args.operation == 'set-package_remote'):
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose,tls=args.tls)
        pkg_act_flag = True
        if args.activate_package.lower() == 'no':
            pkg_act_flag = False

        protocol = system.return_remote_download_protocol(args.rdownload_protocol)
        credentials = system.get_credentials(args.rdownload_username,args.rdownload_password)
        response = system.setpackage_remotedownload(path=args.rdownloadpath, protocol=protocol, activate=pkg_act_flag,
                                                    cred=credentials)
        print('RPC end time:', datetime.datetime.now().time())
        print(response)
    elif (args.operation == 'time'):
        system = XrGnoi(server=host, user=args.user, passwd=args.passwd,
                          verbose=args.verbose,tls=args.tls)
        response = system.return_time()
        print('Epoch Time stamp',response.time)
        float_time = response.time/1000000000
        curr_on_router_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float_time))
        print('Current on router time  as per UTC Time-Zone:',curr_on_router_time)
        print('RPC end time:', datetime.datetime.now().time())

##BERT ccode
    elif (args.operation == 'startbert'):
        diag = XrGnoi(server=host,user=args.user,passwd=args.passwd,
                      verbose=args.verbose,tls=args.tls)
        test_duration = int(args.test_duration)

        # logical_channel_id = list(args.logical_channel_id.split(','))
        # for channel_id in logical_channel_id:
        response = diag.startbert(args.logical_channel_id,args.prbs_pattern,test_duration,args.bert_operation_id)
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
        print(response)
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
            # for per_min in res.error_count_per_minute:
            #     print('BERT error_count_per_minute %s'%per_min)

        print('RPC end time:', datetime.datetime.now().time())
        print('RPC end time:', datetime.datetime.utcnow())


if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())
    run()
