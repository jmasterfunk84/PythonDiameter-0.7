.SUFFIXES: .py .pyc

.py.pyc:
	@echo "python $<"
	@python -c "import `echo $< |sed -e 's/\.py$$//g' -e 's/\//./g' `"

PYCS=diameter/Error.pyc \
     diameter/AVP.pyc \
     diameter/AVP_Unsigned32.pyc \
     diameter/AVP_Unsigned64.pyc \
     diameter/AVP_Integer32.pyc \
     diameter/AVP_Integer64.pyc \
     diameter/AVP_Float32.pyc \
     diameter/AVP_Float64.pyc \
     diameter/AVP_Grouped.pyc \
     diameter/AVP_Address.pyc \
     diameter/AVP_OctetString.pyc \
     diameter/AVP_Time.pyc \
     diameter/AVP_UTF8String.pyc \
     diameter/MessageHeader.pyc \
     diameter/Message.pyc \
     diameter/ProtocolConstants.pyc \
     diameter/Utils.pyc \
     diameter/__init__.pyc \
     diameter/node/Error.pyc \
     diameter/node/NodeSettings.pyc \
     diameter/node/NodeState.pyc \
     diameter/node/ConnectionTimers.pyc \
     diameter/node/ConnectionBuffers.pyc \
     diameter/node/Connection.pyc \
     diameter/node/AVP_FailedAVP.pyc \
     diameter/node/Capability.pyc \
     diameter/node/Peer.pyc \
     diameter/node/Node.pyc \
     diameter/node/NodeManager.pyc \
     diameter/node/SimpleSyncClient.pyc \
     diameter/node/__init__.pyc \

default: $(PYCS)

.PHONY: unittest
unittest:
	for f in $(PYCS); do \
		bname=`echo "$$f"|sed -e 's/\.pyc$$//g' -e 's/\//./g'`; \
		echo "$$bname"; \
		python -c "from $$bname import _unittest; _unittest()"; \
	done

.PHONY: clean
clean:
	rm -f $(PYCS)

.PHONY: doc
doc:
	rm -rf doc
	mkdir -p doc
	./ipydoc.py -p 8008 >/dev/null &
	sleep 1
	(cd doc; wget -nH -r http://127.0.0.1:8008/diameter.html)
	kill `pgrep -f ipydoc.py`


BNAME=PythonDiameter-$(shell cat version)

.PHONY: srcdist
srcdist:
	ln -sf `basename $(shell pwd)` ../$(BNAME)
	cd .. && tar cvfz $(BNAME)/$(BNAME)-src.tar.gz \
	    $(BNAME)/Makefile \
	    `find $(BNAME)/diameter -name \*.py` \
	    `find $(BNAME)/examples -name \*.py` \
	    $(BNAME)/version $(BNAME)/LICENSE \
	    $(BNAME)/TODO \
	    $(BNAME)/README.src
	rm -f ../$(BNAME)
	

.PHONY: dist
dist: srcdist


.PHONY: run_cc_server
run_cc_server:
	PYTHONPATH=$(PWD) python examples/cc_test_server.py isjsys.int.i1.dk example.net
.PHONY: run_cc_client
run_cc_client:
	PYTHONPATH=$(PWD) python examples/cc_test_client.py somehost.example.net example.net isjsys.int.i1.dk 3868
