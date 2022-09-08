#!/usr/bin/python
"""A credit-control test client (RFC4006)"""

from diameter import *
from diameter.node import *
import logging


def unittest():
    pass


import sys

if len(sys.argv)!=5:
    print "usage: <host-id> <realm> <peer> <peer-port>"
    sys.exit(99)

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(name)s %(levelname)s %(message)s')

cap = Capability()
cap.addAuthApp(ProtocolConstants.DIAMETER_APPLICATION_CREDIT_CONTROL)
cap.addAcctApp(ProtocolConstants.DIAMETER_APPLICATION_CREDIT_CONTROL)
settings = NodeSettings(sys.argv[1], sys.argv[2], \
                        9999, cap, 0, "cc_test_client", 1)

print SimpleSyncClient
ssc = SimpleSyncClient(settings,[Peer(sys.argv[3],int(sys.argv[4]))])

ssc.start()

ssc.waitForConnection()

#import sys
#print "Hit enter to stop server"
#sys.stdin.readline()

#build a simple CC one-time event message
req = Message()
# < Diameter Header: 272, REQ, PXY >
req.hdr.command_code = ProtocolConstants.DIAMETER_COMMAND_CC
req.hdr.application_id = ProtocolConstants.DIAMETER_APPLICATION_CREDIT_CONTROL
req.hdr.setRequest(True)
req.hdr.setProxiable(True)

# < Session-Id >
req.append(AVP(ProtocolConstants.DI_SESSION_ID,ssc.node.makeNewSessionId()))

# { Origin-Host }
# { Origin-Realm }
ssc.node.addOurHostAndRealm(req)

# { Destination-Realm }
req.append(AVP_UTF8String(ProtocolConstants.DI_DESTINATION_REALM,"example.net"))
# { Auth-Application-Id }
req.append(AVP_Unsigned32(ProtocolConstants.DI_AUTH_APPLICATION_ID,ProtocolConstants.DIAMETER_APPLICATION_CREDIT_CONTROL)) # a lie but a minor one
# { Service-Context-Id }
req.append(AVP_UTF8String(ProtocolConstants.DI_SERVICE_CONTEXT_ID,"cc_test@example.net"))
# { CC-Request-Type }
req.append(AVP_Unsigned32(ProtocolConstants.DI_CC_REQUEST_TYPE,ProtocolConstants.DI_CC_REQUEST_TYPE_EVENT_REQUEST))
# { CC-Request-Number }
req.append(AVP_Unsigned32(ProtocolConstants.DI_CC_REQUEST_NUMBER,0))
# [ Destination-Host ]
# [ User-Name ]
req.append(AVP_UTF8String(ProtocolConstants.DI_USER_NAME,"user@example.net"))
# [ CC-Sub-Session-Id ]
# [ Acct-Multi-Session-Id ]
# [ Origin-State-Id ]
req.append(AVP_Unsigned32(ProtocolConstants.DI_ORIGIN_STATE_ID,ssc.node.node_state.state_id))
# [ Event-Timestamp ]
import time
req.append(AVP_Time(ProtocolConstants.DI_EVENT_TIMESTAMP,time.time()))
#*[ Subscription-Id ]
# [ Service-Identifier ]
# [ Termination-Cause ]
# [ Requested-Service-Unit ]
req.append(AVP_Grouped(ProtocolConstants.DI_REQUESTED_SERVICE_UNIT,
                       [AVP_Unsigned64(ProtocolConstants.DI_CC_SERVICE_SPECIFIC_UNITS,42).setM()]
                      )
          )
# [ Requested-Action ]
req.append(AVP_Unsigned32(ProtocolConstants.DI_REQUESTED_ACTION,ProtocolConstants.DI_REQUESTED_ACTION_DIRECT_DEBITING))
#*[ Used-Service-Unit ]
# [ Multiple-Services-Indicator ]
#*[ Multiple-Services-Credit-Control ]
#*[ Service-Parameter-Info ]
req.append(AVP_Grouped(ProtocolConstants.DI_SERVICE_PARAMETER_INFO,
                       [AVP_Unsigned32(ProtocolConstants.DI_SERVICE_PARAMETER_TYPE,42),
                        AVP_OctetString(ProtocolConstants.DI_SERVICE_PARAMETER_VALUE,"Hovercraft")
                       ]
                      )
          )
# [ CC-Correlation-Id ]
# [ User-Equipment-Info ]
#*[ Proxy-Info ]
#*[ Route-Record ]
#*[ AVP ]

setMandatory_RFC3588(req)
setMandatory_RFC4006(req)

res = ssc.sendRequest(req)

ssc.stop()
