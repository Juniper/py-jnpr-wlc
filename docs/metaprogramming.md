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

The return value is an RpcMaker opject.  As you can see from the above example, the rpc object is callable; and in doing so will execute the RPC and return the result as an lxml Element.

## RpcMaker Properties

An rpc object has the following properties you can access:
   * `cmd` is one of ['set','get','get-stat','act','delete']
   * `target` is a known target defined by the API DTD files
   * `args` is a dictionary of attributes applied to target
   * `data` is an lxml Element structure of XML
   * `template` is a name of a jinja2 template file
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

The `data` property allows you direct access to any XML body content.  If you've set the `target` property, then the data is within the target.  If you haven't set `target` then data is everything under the specific command.

The `data` property is natively managed as an lxml Element.  So you can make assignements to it directly using
standard lxml mechanism.  This includes using lxml.builder ElementMaker, for example.

If you want to use `data` as a container of a list of things, you can setup data initially and then append items into is.  For an example of this technique, please see [this](../examples/ap_convert_auto_2.py) script.

Another common task is to append things to the `data` property.  This would be common if you were creating a table of
something, like a VLAN-TABLE or a DAP-TABLE.  In this case you can use the `data_append()` method.  This is different
from simply using the native XML append() method.  The `data_append()` will take the provided data and convert it from a string-XML to an Element before appending it to the `data`.  This technique is also illustrated in the same example.

#### template

You can use the `template` property to assign either a template file-name or a jinja2 Template instance to the RPC.  When the template is rendered, the value is assigned (over-writes) the `data` property.  So this way you can
create a single rpc and render the _innerds_ multiple times on different data sets. yo!

Here is a simple example of using the `template` property:
````python
vlan_vars = dict(
  number = 100,
  ports = [
    dict(port=2, tag=50),
    dict(port=3)
  ]
)

rpc = wlc.RpcMaker('set')
rpc.template = 'vlan_set_ports'           # example assignment based on file-name
rpc.render( vlan_vars )

# execute command
rsp = rpc()

````

#### to_xml

When you use the `to_xml` property, the rpc object will construct the complete RPC tranaction and return an lxml Element structure.  At the time of generation the TRANSACTION tid value is incremented.  So if you make three invcations to `to_xml` you will get three different tid values.

Here's an example on how to "pretty print" an rpc manually:

````python
from lxml import etree

rpc = wlc.RpcMaker(...)
# more stuff to setup the rpc object ...

etree.tostring( rpc.to_xml, pretty_print=True )
````

However, the RpcMaker class also defines `__repr__` so you can just as easily do:
````python
print rpc
````
... and get the same results :-)

## General Purpose Usage

Sometime you need to create an RPC of general purpose, and `RpcMaker` is handy for those cases as well.  Let's say you want to change the login banner Message of the Day (MOTD).  That script would look like:
````python
rpc = wlc.RpcMaker('set')
rpc.data = 'MOTD'
rpc.data.text = "This is your login message, yo!"

# execute the RPC
rsp = rpc()
````

_Neato!_
