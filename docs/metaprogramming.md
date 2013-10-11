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

Here is an example that is the same as the "save configuration" command:
````python
wlc.rpc.act_write_configuration()
````

# Complex RPC

To perform complex RPcs, using the `RpcMaker` method.  The usage format for `RpcMaker` is as follows:
````
   rpc = wlc.RpcMaker( <cmd>, [<target>], [**kvargs] )
````
Where:
   * `cmd` is one of ['set','get','get-stat','act','delete']
   * `target` is a known target defined by the API DTD files
   * ``**kvargs`` are option key/value arguments that become the attributes to the target

There are two _well known_ kvargs:
   * `Template` idendifies a template file to use
   * `TemplateVars` is a dictionary of variables to render into the Template (optional)

For example:
````python
vlan_vars = dict(
  number = 100,
  ports = [
    dict(port=2, tag=50),
    dict(port=3)
  ]
)

rpc = wlc.RpcMaker('set', Template='vlan_set_ports', TemplateVars=vlan_vars )

print "Settting ports on VLAN ..."
rsp = rpc()
````

The return value is an RpcMaker opject.  As you can see from the above example, the rpc object is callable; and in doing so will execute the RPC and return the result as an lxml Element.  See Examples below.

## RpcMaker Properties

An rpc object has the following properties you can access:
   * `cmd` is one of ['set','get','get-stat','act','delete']
   * `target` is a known target defined by the API DTD files
   * `args` is a dictionary of attributes applied to target
   * `data` is an lxml Element structure of XML
   * `to_xml` is a property that returns the rpc object as a complete RPC etree XML

#### cmd

You can change the command on the fly by setting this property:
````python
rpc.cmd = 'set'
# ...
# do something that creates and object

rsp = rpc()

# now let's delete that same thing ...

rpc.cmd = 'delete'
rsp = rpc()

````
#### target
The `target` property is actually optional.  It is generally used to define the toplevel XML element
for a given structure.  Sometime this is not necessary.  You can change the target by simply assigning
a new string value.  The rpc object will upcase the string for you, so 'vlan' and 'VLAN' is the same thing.
````python

# assign the target after the rpc was instantiated
rpc.target = 'vlan'
````
#### args
The `args` property is a dictionary type that controls the attributes defined within the `target` element.
It can be handy to change the args on the fly.  For example, if you wanted to do something for one vlan named
'Jeremy' and then again to another vlan named 'Bob', you could do:
````python

rpc.args['name'] = "Jeremy"

rsp = rpc()

# now change the vlan name to "Bob" and execute the RPC again

rpc.args['name'] = "Bob"
rsp = rpc()
````

#### data

#### to_xml

