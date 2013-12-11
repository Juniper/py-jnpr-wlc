
import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
from lxml.builder import E
from jnpr.wlc import WirelessLanController as WLC
from client_helper import find_client, clear_client, get_clients

wlc = WLC_login()

# add client routines to the WLC "ez" section.
# XXX - this seems wrong? shouldn't this get loaded automatically?
wlc.ez( helper=find_client)
wlc.ez( helper=clear_client)
wlc.ez( helper=get_clients)


# mac address for testing, should be a current session
#mac = '10:40:f3:e6:fc:26'
#mac = '88:53:95:2a:d4:37'
mac = 'bc:67:78:08:25:bb'


##### -------------------------------------------------------------------------
####  run the find client routine, searching for active sessions by mac, ip 
####  and name. This command does not have an equivalent CLI command.
##### -------------------------------------------------------------------------

# call the service by mac
print "Finding user session by mac..."
client = wlc.ez.find_client( macaddress = mac )

# show the info:
pp(client)

print "Finding user session by ip..."
client = wlc.ez.find_client( ipaddress = client[mac]['ip-addr'] )

# show the info:
pp(client)

print "Finding user session by name..."
client = wlc.ez.find_client( username = client[mac]['user-name'] )

# show the info:
pp(client)


##### -------------------------------------------------------------------------
####  run the clear client routine. This is the same as the 'clear session' 
####  CLI command except that we have an option to also add the client to the
####  dynamic blacklist.
##### -------------------------------------------------------------------------

# Execute the clear client function against the session id we discovered in the find.
# The Blacklist flag will terminate the user session and add the mac to the dynamic
# rfedetect blacklist table.
print "Clearing session id..."
wlc.ez.clear_client( sessionid = client[mac]['session-id'], blacklist = 'NO' )
print "Done"


##### -------------------------------------------------------------------------
####  run the get sessions command. This is the same as the 'show sessions' 
####  CLI command.
##### -------------------------------------------------------------------------

# get the complete list of active sesisons and print out a summary line for each 
print "Get current sessions..."
clients = wlc.ez.get_clients()

print "User Name             SessID  Type  Address              VLAN            AP/Rdo"
print "--------------------- ------  ----- -------------------- --------------  -------"

for client in clients:
    print('%-21s %-6s  %-5s %-20s %-14s  %-s/%-s' % (
        clients[client]['user-name'][:20], 
        clients[client]['local-id'],
        clients[client]['access-type'][-5:],
        clients[client]['ip-addr'],
        clients[client]['vlan-name'],
        clients[client]['dap'],
        clients[client]['ap-radio'] ))


