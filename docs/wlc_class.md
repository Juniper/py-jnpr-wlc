# WirelessLanController

This class is the primary object for managing a Juniper WLC, physical device or virtual server.  The class is python documented.  For the lasted information, simply do a `help(..)` on either the class or an object of the class.

# GENERAL USAGE

The first step is to create an instance of this class.  The only required parameters are:
  * user
  * host
  * password

````python
from jnpr.wlc import WirelessLanController as WLC

wlc = WLC( user='jeremy', host='192.168.56.191', password='logmein' )
````

There are number of optional parameters; refer to the builtin docs.
````python
help( wlc )
````

Once you've created an instance of this class, you must invoke the `open()` method.  
````python
wlc.open()
````
This action will validate login authentication and setup some internal bits on the object.  If an error occurs during this process, you will recieve an exception.  Most like this will be an HTTP exception resulting from invalid authorization; i.e. bad username/password.  Also during the open process, the object will attempt to ping the WLC.  If the ping fails, then you will receive a RuntimeError.  

# META RPC API

Invoking an RPC can be done by either using the `rpc` metaprogramming attribute, for example:
````python
rsp = wlc.rpc.get_vlan( name='default' )
````

Or by using the `RpcMaker` mechanism.  Both of these techniques are further described [here](metaprogramming.md).

# MANUAL RPC API

You can also manually create the complete XML transaction and execute it using the `rpc` as a callable.  For example:
````python
rpc_as_str = """
<TRANSACTION tid="4">
  <SESSION/>
  <GET level="all">
    <VLAN/>
  </GET>
</TRANSACTION>
"""

resp = wlc.rpc( rpc_as_str )
````

The XML data passed to `rpc()` can also be an lxml Element. This example is a bit contrived, but it 
illustrates the point:
````python
from lxml import etree

# use etree to convert the string to an XML element structure
rpc_as_xml = etree.XML( rpc_as_str )

resp = wlc.rpc( rpc_as_xml )
````
