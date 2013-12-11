
import demowlcutils
from demowlcutils import ppxml, WLC_login
import client_helper
from client_helper import find_client
from pprint import pprint as pp 
from lxml.builder import E



##### -------------------------------------------------------------------------
####  add the 'find_client' as an "ez" helper function
##### -------------------------------------------------------------------------


  

##### -------------------------------------------------------------------------
##### MAIN BLOCK
##### -------------------------------------------------------------------------


cli_args = _parse_args()
print(cli_args)

# add new routines to the WLC "ez" section.
# wlc.ez( helper=find_client)
# wlc.ez( helper=clear_client)
# wlc.ez( helper=get_clients)

# # now call the service by mac
# print "Finding user session by mac..."
# client = wlc.ez.find_client( macaddress = mac )

# # show the info:
# pp(client)

# print "Finding user session by ip..."
# client = wlc.ez.find_client( ipaddress = client[mac]['ip-addr'] )

# # show the info:
# pp(client)

# print "Finding user session by name..."
# client = wlc.ez.find_client( username = client[mac]['user-name'] )

# # show the info:
# pp(client)

# # Execute the clear client function against the session id we discovered in the find.
# # The Blacklist flag will terminate the user session and add the mac to the dynamic
# # rfedetect blacklist table.
# print "Clearing session id..."
# wlc.ez.clear_client( sessionid = client[mac]['session-id'], blacklist = 'NO' )
# print "Done"

# print "Get current sessions..."
# clients = wlc.ez.get_clients()

# print "User Name             SessID  Type  Address              VLAN            AP/Rdo"
# print "--------------------- ------  ----- -------------------- --------------  -------"

# for client in clients:
#     print('%-21s %-6s  %-5s %-20s %-14s  %-s/%-s' % (
#         clients[client]['user-name'][:20], 
#         clients[client]['local-id'],
#         clients[client]['access-type'][-5:],
#         clients[client]['ip-addr'],
#         clients[client]['vlan-name'],
#         clients[client]['dap'],
#         clients[client]['ap-radio'] ))


