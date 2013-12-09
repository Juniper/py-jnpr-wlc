# Juniper WLC Protocol Guide

The WL solution utilizes an XML over HTTPS protocol to communicate with WLC and WLA devices. The protocol is based on a set of transactions where the transaction syntax is defined by a DTD. The DTD can be found in a seperate repo at the Juniper Networks GitHub site. A list of transactions such as GET, SET, DELETE, and ACTION are supported by the WLC and are used to configure and monitor both the WLC WLAN controllers as well as the WLA Access Points (by proxy through the WLC).

[add intro text about who uses the interface and why]

## Connecting to the WLC

[https port 8889, link to config guide, basic auth, usernames/passwords, config logging on WLC, tracing, etc]

[should probably use the system IP although not strictly required]

-admin certificates


## Transactions

[more intro to transactions]

Some basic rules of the WLC transactions:

  - A transaction can contain 1 or more operations (set, get, action).
  - Delete actions must follow all set operations in the same transaction.
  - If any operation fails the whole transaction is failed and the device is not expected to perform the rest of a transaction. So, if an action or get operation follows an operation that fails, the action or get will not be performed.
  - If the DTD specifies a certain element is REPLACE-CHILDREN-ON-SET, that means, if there are changes to its children, whether the children is created, deleted, or modified,  the entire element should be sent down as SET.



### GET Operations

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

### GET-STAT Operations

GET-STAT operations are a speccial case of GET operations used for collecting device statistics. 


### SET Operations

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

### DELETE Operations

There is no implicit deletes. Any DELETES need to be included in an `ACTION` transaction. For example,

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

### ACTION Operations

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

## COMMAND SET

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


## Sample Transactions

The following are sample transactions which illustrate the basic usage of the XML API.


1\. Get the system location

Request:

````xml
<!DOCTYPE TRANSACTION >
<TRANSACTION tid="1">
  <GET> 
    <SYSLOCATION/> 
  </GET>
  <GET> 
    <MOTD/> 
  </GET>
</TRANSACTION>
````

Response:

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP >
<TRANSACTION-RESP pvers="0.1" nerrors="0" generation="1" tid="1">
  <GET-RESP>
    <SYSLOCATION>In a maze of twisty, little passages
    </SYSLOCATION>
  </GET-RESP>
  <GET-RESP>
    <MOTD>The message of the day
    </MOTD>
  </GET-RESP>
</TRANSACTION-RESP>
````

2\. Select the particular VLAN-MEMBER with tagging disabled:

Request:

````xml
<!DOCTYPE TRANSACTION >
<TRANSACTION tid="1" >
  <GET>
    <VLAN number="1" >
      <VLAN-MEMBER-TABLE>
        <VLAN-MEMBER enable-tagging="NO"/>
      </VLAN-MEMBER-TABLE>
    </VLAN>
  </GET>
</TRANSACTION>
````

Response:

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP >
<TRANSACTION-RESP pvers="0.1" nerrors="0" generation="17" tid="1">
  <GET-RESP>
    <VLAN number="1" mtu="1500" >
      <VLAN-MEMBER-TABLE>
        <VLAN-MEMBER enable-tagging="NO" >
          <PORT-REF  type="PORT">
            <PHYS-PORT-REF  module="1" port="1"/>
          </PORT-REF>
        </VLAN-MEMBER>
      </VLAN-MEMBER-TABLE>
    </VLAN>
  </GET-RESP>
</TRANSACTION-RESP>
````

3\.  Select VLAN, with number="1"

Request:

````xml
<!DOCTYPE TRANSACTION >
<TRANSACTION tid="1" >
  <GET>
    <VLAN number="1" />
  </GET>
</TRANSACTION>
````

Response:

````xml
<!DOCTYPE TRANSACTION-RESP >
<TRANSACTION-RESP pvers="0.1" nerrors="0" generation="17" tid="1">
  <GET-RESP>
    <VLAN number="1" mtu="1500" >
      <VLAN-MEMBER-TABLE>
        <VLAN-MEMBER  enable-tagging="NO">
          <PORT-REF  type="PORT">
            <PHYS-PORT-REF  module="0" port="0"/>
          </PORT-REF>
        </VLAN-MEMBER>
      </VLAN-MEMBER-TABLE>
      <VLAN-IP  vrouter="local">
        <VLAN-IP-IF  primary="YES" enabled="YES"
                        address="172.16.20.8" netmask="255.255.255.0"/>
      </VLAN-IP>
      <VLAN-FDB >
        <VLAN-FDB-TABLE/>
      </VLAN-FDB>
    </VLAN>
  </GET-RESP>
</TRANSACTION-RESP>
````

4\.  Set an IP ALIAS entry

Request:

````xml
<!DOCTYPE TRANSACTION >
<TRANSACTION tid="1" >
  <SET>
    <VR-IP-ALIAS-ENTRY name="tkolar-pc" address="192.168.1.63"/>
  </SET>
</TRANSACTION>
````

Response:

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP>
<TRANSACTION-RESP pvers="0.1" nerrors="0" generation="26" tid="1">
  <SET-RESP/>
</TRANSACTION-RESP>
````

5\.  Setting and verifying the MOTD

Request:

````xml
<!DOCTYPE TRANSACTION >
<TRANSACTION tid="1" >
  <SET><MOTD>Welcome to Trapeze Networks</MOTD> </SET>
  <GET><MOTD/> </GET>
</TRANSACTION>
````

Response:

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP>
<TRANSACTION-RESP pvers="0.1" nerrors="0" generation="25" tid="1">
  <SET-RESP/>
  <GET-RESP>
    <MOTD>Welcome to Trapeze Networks</MOTD>
  </GET-RESP>
</TRANSACTION-RESP>
````

6\.  Error response (when glob matches too many elements):

Request:

````xml
<!DOCTYPE TRANSACTION >
<TRANSACTION tid="1" >
  <SET>
    <VR-IP-ALIAS-ENTRY name="to*" address="1.1.1.1"/>
  </SET>
</TRANSACTION>
````

Response:

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP>
<TRANSACTION-RESP pvers="0.1" nerrors="1" generation="27" tid="1">
  <ERROR-RESP>
    <ERROR>More than 1 elements matched in set.
    </ERROR>
  </ERROR-RESP>
</TRANSACTION-RESP>
````

7\.  Doing a set based on a complex object, an element whose key is specified by a child element:

Request:

````xml
<!DOCTYPE TRANSACTION >
<TRANSACTION tid="1" >
  <SET>
    <SYSINFO vlantagtype="ISL"/>
  </SET>
  <SET>
    <VLAN-MEMBER enable-tagging="YES" vlan-tag="34">
      <PORT-REF type="PORT">
        <PHYS-PORT-REF module="1" port="1"/>
      </PORT-REF>
    </VLAN-MEMBER>
  </SET>
</TRANSACTION>
````

Response:

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP>
<TRANSACTION-RESP pvers="0.1" nerrors="1" generation="27" tid="1">
  <SET-RESP/>
</TRANSACTION-RESP>
````

8\.  Changing a child element, where the key is in the parent:
   (in this case I am changing from half duplex to full duplex.)

Request:

````xml
<!DOCTYPE TRANSACTION >
<TRANSACTION tid="1" >
  <SET>
    <DP-PHYS-MODULE number="1">
      <DP-PHYS-PORT name="tap0" number="1"
                          enabled="YES" snmp-link-trap="YES" type="100BT">
        <DP-PHYS-PORT-100BT duplex="HALF" speed="100"
                            sendpause="OFF" recvpause="ON"/>
      </DP-PHYS-PORT>
    </DP-PHYS-MODULE>
  </SET>
</TRANSACTION>
````

Response:

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP>
<TRANSACTION-RESP pvers="0.1" nerrors="0" generation="113" tid="1">
  <SET-RESP/>
</TRANSACTION-RESP>
````

9\.  Change of port information:

Request:

````xml
<!DOCTYPE TRANSACTION>
<TRANSACTION tid="5">
  <SET>
    <DP-PHYS-MODULE number="1">
      <DP-PHYS-PORT number="2" type="100BT" name="" enabled="NO"
			  snmp-link-trap="NO" auth-control="AUTO">
        <DP-PHYS-PORT-100BT sendpause="ON" receivepause="ON"
			  speed="AUTO" duplex="FULL"/>
      </DP-PHYS-PORT>
    </DP-PHYS-MODULE>
  </SET>
</TRANSACTION>
````

10\.  Delete an IP alias

Request

````xml
<!DOCTYPE TRANSACTION>
<TRANSACTION tid="5">
  <ACT>
    <DELETE>
      <VR-IP-ALIAS-ENTRY name="foo" />
    </DELETE>
  </ACT>
</TRANSACTION>
````

Response

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP>
<TRANSACTION-RESP pvers="0.1" nerrors="0" generation="20" tid="1">
  <ACT-RESP/>
</TRANSACTION-RESP>
````

11\.  Delete an non-existant IP alias (repeat 10.1 about)

Request

````xml
<!DOCTYPE TRANSACTION>
<TRANSACTION tid="5">
  <ACT>
    <DELETE>
      <VR-IP-ALIAS-ENTRY name="foo" />
    </DELETE>
  </ACT>
</TRANSACTION>
````

Response

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP>
<TRANSACTION-RESP pvers="0.1" nerrors="1" generation="21" tid="1">
<ERROR-RESP>
<ERROR>Element not found.</ERROR>
</ERROR-RESP>
</TRANSACTION-RESP>
````

12\.  Attempt a set when the WLC won't allow it (test phase fails)

Request

````xml
<!DOCTYPE TRANSACTION>
<TRANSACTION tid="5">
<SET>
<TRACE-ENTRY area="fubar" />
</SET>
</TRANSACTION>
````

Response

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP>
<TRANSACTION-RESP pvers="0.1" nerrors="1" generation="21" tid="1">
  <ERROR-RESP>
    <ERROR>Set failed, case 2.</ERROR>
  </ERROR-RESP>
</TRANSACTION-RESP>
````

13\.  Perform a simple ACT, in this case a DIR command.

Request

````xml
<!DOCTYPE TRANSACTION>
<TRANSACTION tid="5">
  <ACT>
    <DIR />
  </ACT>
</TRANSACTION>
````

Response

````xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE TRANSACTION-RESP>
<TRANSACTION-RESP pvers="0.1" nerrors="0" generation="21" tid="5">
  <ACT-RESP>
    <DIR-RESP nbytes="5219782" nfiles="8" directory="/">
      <DIR-ENTRY date="" size="512" name="bin"/>
      <DIR-ENTRY date="" size="512" name="lib"/>
      <DIR-ENTRY date="" size="512" name="httpd"/>
      <DIR-ENTRY date="" size="512" name="store"/>
      <DIR-ENTRY date="" size="512" name="etc"/>
      <DIR-ENTRY date="" size="112" name="build_details"/>
      <DIR-ENTRY date="" size="5214208" name="loader.core"/>
      <DIR-ENTRY date="" size="2902" name="foo"/>
    </DIR-RESP>
  </ACT-RESP>
</TRANSACTION-RESP>
````
