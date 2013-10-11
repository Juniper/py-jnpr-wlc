# Simple RPC

To perform simple RPCs, use the `rpc` attribute.  

The usage format for `rpc` is as follows:

````
   resp = wlc.rpc.<cmd>_<target>( attributes )
````

Where:
  * `cmd` is one of: [get, get_stat, delete, act]
  * `target` is a known target defined by the API DTD files
  * `attributes` is a name/value pair that is used to identify a specific target.  This is optional.

The return value is the result of the RPC execution, as an lxml Element.

Here is an example of retrieving information on a specific VLAN, using the `name` attribute to identify the VLAN:
````python
resp = wlc.rpc.get_vlan( name="default" )
````

# Complex RPC

To perform complex RPcs, using the `RpcMaker` method.
