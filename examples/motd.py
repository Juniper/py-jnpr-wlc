import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

### just let the user play around with the wlc object
### from the python interpreter

rpc = wlc.RpcMaker('set')
rpc.data = 'MOTD'
rpc.data.text = "This is a new message, yo!"


