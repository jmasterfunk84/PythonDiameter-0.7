import threading
import logging
from diameter.node import *
#import diameter.node
#.NodeManager import NodeManager
from diameter.node.Error import NotRoutableError,NotARequestError

class SimpleSyncClient(NodeManager):
    """
    A simple Diameter client that support synchronous request-answer calls.
    It does not support receiving requests.
    """
    
    def __init__(self,settings,peers):
        """
        Constructor for SimpleSyncClient
          settings  The settings to use for this client
          peers     The upstream peers to use
        """
        NodeManager.__init__(self,settings)
        self.peers = peers
    
    def start(self):
        """
        Starts this client. The client must be started before sending
        requests. Connections to the configured upstream peers will be
        initiated but this method may return before they have been
        established.
        See also: NodeManager.waitForConnection
        """
        NodeManager.start(self)
        for p in self.peers:
            self.node.initiateConnection(p,True)
    
    class __SyncCall:
        def __init__(self):
            self.answer_ready = False
            self.answer = None
            self.cv = threading.Condition()
    
    def handleAnswer(self,answer, answer_connkey, state):
        "Dispatches an answer to threads waiting for it."
        state.cv.acquire()
        state.answer = answer
        state.answer_ready = True
        state.cv.notify()
        state.cv.release()
    
    def sendRequest(self,request):
        """
        Send a request and wait for an answer.
          request  The request to send
        The answer to the request. Null if there is no answer (all peers
        down, or other error)
        """
        
        sc = SimpleSyncClient.__SyncCall()
        
        try:
            self.sendRequest_any(request, self.peers, sc)
            #ok, sent
            sc.cv.acquire()
            while not sc.answer_ready:
                sc.cv.wait()
            sc.cv.release()
        except NotRoutableError:
            self.logger.log(logging.DEBUG,"SimpleSyncClient.sendRequest(): not routable")
        except NotARequestError:
            #just return null
            pass
        return sc.answer

def _unittest():
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(name)s %(levelname)s %(message)s')
    
    from diameter.node import Capability,NodeSettings
    from diameter import ProtocolConstants,Message
    cap = Capability();
    cap.addAuthApp(ProtocolConstants.DIAMETER_APPLICATION_NASREQ)
    settings = NodeSettings("isjsys.int.i1.dk","i1.dk",1,cap,3868,"pythondiameter",1)
    
    ssc = SimpleSyncClient(settings,[])
    ssc.start()
    
    msg = Message()
    msg.hdr.application_id = ProtocolConstants.DIAMETER_APPLICATION_ACCOUNTING
    msg.hdr.command_code = ProtocolConstants.DIAMETER_COMMAND_ACCOUNTING
    msg.hdr.setRequest(True)
    msg.hdr.setProxiable(True)
    
    answer = ssc.sendRequest(msg)
    assert not answer
    
    ssc.stop()
    del ssc
