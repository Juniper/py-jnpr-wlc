import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

vlan_vars = dict(
  number = 100,
  ports = [
    dict(port=2, tag=50),
    dict(port=3)
  ]
)

rpc = wlc.RpcMaker('set', Template='vlan_set_ports', TemplateVars=vlan_vars )

print "Settting ports on VLAN ..."
# rsp = rpc()
