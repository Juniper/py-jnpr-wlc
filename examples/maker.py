import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
from jnprwlc.builder import RpcMaker

wlc = WLC_login()
r = RpcMaker( wlc )

