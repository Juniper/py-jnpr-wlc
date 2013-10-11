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
The transaction id value (tid attribute) is simply an incrementing number used by the application and simply echo'd back in the transaction response.
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
# Simple vs Complex RPC

A _simple_ RPC is one that contains only a target element and associated attributes.  For example, retrieveing information on a specific VLAN is considered a simple RPC:
````xml
<TRANSACTION tid="4">
  <SESSION/>
  <GET level="all">
    <VLAN name="default"/>
  </GET>
</TRANSACTION>
````

A _complex_ RPC is one that contains further XML nodes within the target.  This is very common for "set" or "delete" type commands.  Here is an example of adding two ports to a VLAN:
````xml
<TRANSACTION tid="4">
  <SESSION/>
  <SET>
    <VLAN-TABLE>
      <VLAN number="100">
        <VLAN-MEMBER-TABLE>
          <VLAN-MEMBER enable-tagging="YES" vlan-tag="50" forward-igmp="NO" multicast-router="NO">
            <PORT-REF type="PORT">
              <PHYS-PORT-REF module="1" port="2"/>
            </PORT-REF>
          </VLAN-MEMBER>
          <VLAN-MEMBER enable-tagging="NO" vlan-tag="0" forward-igmp="NO" multicast-router="NO">
            <PORT-REF type="PORT">
              <PHYS-PORT-REF module="1" port="3"/>
            </PORT-REF>
          </VLAN-MEMBER>
        </VLAN-MEMBER-TABLE>
      </VLAN>
    </VLAN-TABLE>
  </SET>
</TRANSACTION>
````

