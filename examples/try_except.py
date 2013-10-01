import pdb
import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

from jnprwlc.exception import RpcError as WLCError

wlc = WLC_login()

# try to deleete a VLAN that doesn't exist
# you can example err.cmd, err.rsp, and err.errors

try:
   wlc.rpc.delete_vlan( number='200' )
except WLCError as err:
  pp(err.errors)


