# OVERVIEW

The WL solution utilizes an XML over HTTPS protocol to communicate with WLC and WLA devices. The protocol is based on a set of transactions where the transaction syntax is defined by a DTD. The DTD can be found here [tim: add reference]. A list of transactions such as GET, SET, DELETE, and ACTION are supported by the WLC and are used to configure and monitor both the WLC WLAN controllers as well as the WLA Access Points (by proxy through the WLC).

Some basic rules of the WLC transactions:

  - A transaction can contain 1 or more operations (set, get, action).
  - Delete actions must follow all set operations in the same transaction.
  - If any operation fails the whole transaction is failed and the device is not expected to perform the rest of a transaction. So, if an action or get operation follows an operation that fails, the action or get will not be performed.
  - If the DTD specifies a certain element is REPLACE-CHILDREN-ON-SET, that means, if there are changes to its children, whether the children is created, deleted, or modified,  the entire element should be sent down as SET.


### GET Operation

GET operation is used by retrieving or querying a list of information for example configuration data, device status and statistics. For example, the following request is sent to a device for querying of a boot status of a system.

````xml
<TRANSACTION tid="2">
        <SESSION/>
        <GET level="ALL">
            <SYSINFO>
                <BOOTSTATUS/>
            </SYSINFO>
        </GET>
    </TRANSACTION>
````

### SET Operation

SET operation is used to perform modifying attributes of an object, or creating an object. If the SET target does not exist, the operation is assumed to be a “create” operation. For example, the following transaction creates a RADIUS-SERVER-GROUP on the device.

````xml
    <TRANSACTION tid="32">
        <SESSION/>
        <SET>
            <AAA>
                <RADIUS>
                    <RADIUS-DEFAULT timeout="5" retransmit="3" deadtime="0" key="" author-password="11" radius-client-src=""/>
                    <RADIUS-SERVERS/>
                    <RADIUS-SERVER-GROUPS>
                        <RADIUS-SERVER-GROUP name="dd" load-balance="NO"/>
                    </RADIUS-SERVER-GROUPS>
                </RADIUS>
            </AAA>
        </SET>
    </TRANSACTION>
````

### DELETE Operation

There is no implicit deletes. Any DELETES need to be included in a transaction. For example,

````xml
<TRANSACTION tid="32">
  <SESSION/>
  <ACT>
    <DELETE>
      <AAA>
        <USERDB>
          <USER-TABLE>
            <NAMED-USER name="test-user1"/>
          </USER-TABLE>
        </USERDB>
      </AAA>
    </DELETE>
  </ACT>
</TRANSACTION>
````

### ACTION Operation

ACTION Operation is used to perform one time action on the device, and it does not persist in the configuration data on the device. For example, reboot a device, reboot an AP, finding a client are all possible one time action performed on the device.

````xml
<TRANSACTION tid="1">
  <ACT>
    <BOOT>
     <BOOT-DP></BOOT-DP>
    </BOOT>
  </ACT>
</TRANSACTION>
````

#COMMAND SET

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

### TARGETS

Generally speaking, each target has identifying XML attributes.  To retrieve a _specific_ VLAN, one would set either the VLAN `name` or `number` attribute.  For example, to retrieve just the VLAN named "default":
````xml
<TRANSACTION tid="4">
  <SESSION/>
  <GET level="all">
    <VLAN name="default"/>
  </GET>
</TRANSACTION>
````
### Simple vs Complex RPC

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




