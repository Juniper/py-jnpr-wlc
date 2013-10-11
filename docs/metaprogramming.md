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

To perform complex RPcs, using the `RpcMaker` method.  The usage format for `RpcMaker` is as follows:
````
   rpc = wlc.RpcMaker( <cmd>, [<target>], [**kvargs] )
````
Where:
   * `cmd` is one of ['set','get','get-stat','act','delete']
   * `target` is a known target defined by the API DTD files
   * ``**kvargs`` are option key/value arguments

There are two _well known_ kvargs:
   * `Template` idendifies a template file to use
   * `TemplateVars` is a dictionary of variables to render into the Template (optional)

Any other kvargs are considered attributes to the `target` element.

The return value is an RpcMaker opject.  The rpc is callable; and in doing so will invite the RPC and return the result as an lxml Element.  See Examples below.

## RpcMaker Properties

An rpc object has the following properties you can access:
   * `cmd`
   * `target`
   * `args`
   * `data`
   * `to_xml`

#### cmd

#### target

#### args

#### data

#### to_xml

