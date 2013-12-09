
import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
from lxml.builder import E
from jnprwlc import WirelessLanController as WLC


wlc = WLC_login()

mac = '10:40:f3:e6:fc:26'
#mac = '88:53:95:2a:d4:37'


##### -------------------------------------------------------------------------
####  add the 'find_client' as an "ez" helper function
##### -------------------------------------------------------------------------

def find_client( wlc, *vargs, **kvargs ):
    """
        create a single dictionary containing information
        about specific stations. Filter can be username, mac or ip.

        sessions on a WLC can be found by any combination of mac, ip or 
        username, this fn only uses the most specific attr.
    """
    if 'macaddress' in kvargs:
        rsp = wlc.rpc.act_findclient( macaddress = kvargs['macaddress'] )
    elif 'ipaddress' in kvargs:
        rsp = wlc.rpc.act_findclient( ipaddress = kvargs['ipaddress'] )
    elif 'username' in kvargs: 
        rsp = wlc.rpc.act_findclient( username = kvargs['username'] )
    else:    
        raise ValueError("You must provide a mac, ip or username")

    ret_data = {}     # empty dictionary

    # It is possible for a find client request to return a session which 
    # is not on the same WLC that we initiated the request to. The WLC 
    # will use the Mobility Domain plumbing to locate sessions on other
    # WLCs. This fn will attempt to connect to the alternate WLC to get
    # session stats.
    for session in rsp.findall('.//FINDCLIENT-ENTRY'):                        
        dp = session.get('dp-system-ip')
        sessionid = session.get('session-id')

        if wlc.facts['ip-addr'] != session.get('dp-system-ip'):
            print('### session on different WLC, connect to new WLC using existing credentials ###')
            altwlc = WLC( user=wlc._user, host=dp, password=wlc._password )
            altwlc.open()
            rpc = altwlc.RpcMaker('get-stat')
        else:
            rpc = wlc.RpcMaker('get-stat')

        rpc.data = E('USER-SESSION-STATUS')
        rpc.data.set('session-id', sessionid)

        sessstats = rpc()
        sessstat = sessstats.find('.//USER-SESSION-STATUS')
        locstat = sessstats.find('.//USER-LOCATION-MEMBER')

        ret_data[sessstat.get('mac-addr')] = dict(sessstat.attrib)   # copy the attributes into a dictionary
        ret_data[sessstat.get('mac-addr')].update(locstat.attrib) 

    return ret_data


def clear_client( wlc, *vargs, **kvargs ):
    """
        clear client sessions from the WLC
    """
    if 'sessionid' not in kvargs:
        raise ValueError("You must provide a session id to clear")

    rpc = wlc.RpcMaker('act')
    rpc.data = E('CLEARSESSION') 
    rpc.data.set('session-id', kvargs['sessionid']) 

    if 'blacklist' in kvargs:
        rpc.data.set('blacklist', kvargs['blacklist']) 

    return rpc()


def get_clients( wlc, *vargs, **kvargs ):
    """
        create a single dictionary containing information
        about all associated stations. 
    """
    rsp = wlc.rpc.get_stat_user_session_status()

    ret_data = {}  
    for session in rsp.findall('.//USER-SESSION-STATUS'):                        
        locstat = session.find('.//USER-LOCATION-MEMBER')

        ret_data[session.get('mac-addr')] = dict(session.attrib)   # copy the attributes into a dictionary
        ret_data[session.get('mac-addr')].update(locstat.attrib) 

    return ret_data
  

##### -------------------------------------------------------------------------
##### MAIN BLOCK
##### -------------------------------------------------------------------------

# add new routines to the WLC "ez" section.
wlc.ez( helper=find_client)
wlc.ez( helper=clear_client)
wlc.ez( helper=get_clients)

# now call the service by mac
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

# Execute the clear client function against the session id we discovered in the find.
# The Blacklist flag will terminate the user session and add the mac to the dynamic
# rfedetect blacklist table.
print "Clearing session id..."
wlc.ez.clear_client( sessionid = client[mac]['session-id'], blacklist = 'NO' )
print "Done"

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


