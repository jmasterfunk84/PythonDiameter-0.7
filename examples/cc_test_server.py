#!/usr/bin/python
"""A credit-control test server (RFC4006)"""

from diameter import *
from diameter.node import *
import logging


class cc_test_server(NodeManager):
    "A simple Credit-control server that accepts and grants everything"
    def __init__(self,settings):
        NodeManager.__init__(self,settings)
        self.requests_processed=0
    
    def handleRequest(self,request,connkey,peer):
        answer = Message()
        answer.prepareResponse(request)
        a = request.find(ProtocolConstants.DI_SESSION_ID)
        if a:
            answer.append(a)
        answer.append(AVP_Unsigned32(ProtocolConstants.DI_RESULT_CODE, ProtocolConstants.DIAMETER_RESULT_SUCCESS))
        self.node.addOurHostAndRealm(answer)
        a = request.find(ProtocolConstants.DI_AUTH_APPLICATION_ID)
        if a:
            answer.append(a)
        a = request.find(ProtocolConstants.DI_CC_REQUEST_TYPE)
        if a:
            answer.append(a)
        a = request.find(ProtocolConstants.DI_CC_REQUEST_NUMBER)
        if a:
            answer.append(a)
        
        a = request.find(ProtocolConstants.DI_REQUESTED_SERVICE_UNIT)
        if a:
            import copy
            a = copy.deepcopy(a)
            a.code = ProtocolConstants.DI_GRANTED_SERVICE_UNIT
            answer.append(a)
        
        Utils.copyProxyInfo(request,answer)
        Utils.setMandatory_RFC3588(answer)
        self.answer(answer,connkey)
        
        self.requests_processed+=1


import sys

if len(sys.argv)<3:
    print "usage: <host-id> <realm> [<port>]"
    sys.exit(99)

if len(sys.argv)>=4:
    listen_port=int(sys.argv[4])
else:
    listen_port=3868

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(name)s %(levelname)s %(message)s')

cap = Capability()
cap.addAuthApp(ProtocolConstants.DIAMETER_APPLICATION_CREDIT_CONTROL)
cap.addAcctApp(ProtocolConstants.DIAMETER_APPLICATION_CREDIT_CONTROL)
settings = NodeSettings(sys.argv[1], sys.argv[2], \
                        9999, cap, listen_port, "TestServer", 1);

ts = cc_test_server(settings);
ts.start()
print "Hit enter to stop server"
sys.stdin.readline()
ts.stop(0.050) #Stop but allow 50ms graceful shutdown

print "requests_processed:", ts.requests_processed
