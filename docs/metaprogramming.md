
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
  <SET><VLAN-TABLE>
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
