import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

# sometimes you need to set a configuration element that has a text value,
# rather than element attributes.  this example shows you a technique for
# doing this; the equivalent of:
#
#> set banner motd "text"

rpc = wlc.RpcMaker('set')
rpc.data = 'MOTD'
rpc.data.text = "This is a new message, yo!"

# if you want to clear the MOTD, you need to set the :text: to None

rsp = rpc()
