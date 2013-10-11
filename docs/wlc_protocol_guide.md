# COMMAND SET

XML RPC are executed as a `TRANSACTION`.  Within the TRANSACTION there is a toplevel command element, one of:
  
  - GET
  - GET-STAT
  - ACT
  - SET

Each of these commands has associated _targets_.  The targets are defined in the XML DTD files.  For example, the GET targets are listed in the `<!ENTITY % GETTARGETS>`.  There is not a toplevel delete command.  To delete something, you need to use the ACT command enclosing the DELETE.

Here is an example of a TRANSACTION to retrieve information on vlans.  The command is GET and the target is VLAN:
````xml
<TRANSACTION tid="4">
  <SESSION/>
  <GET level="all">
    <VLAN/>
  </GET>
</TRANSACTION>
````

# TARGETS

Generally speaking, each target has identifying XML attributes.  To retrieve a _specific_ VLAN, one would set either the VLAN `name` or `number` attribute.  For example, to retrieve just the VLAN named "default":
````xml
<TRANSACTION tid="4">
  <SESSION/>
  <GET level="all">
    <VLAN name="default"/>
  </GET>
</TRANSACTION>
````

