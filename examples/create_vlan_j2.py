import demowlcutils
from demowlcutils import ppxml, WLC_login

wlc = WLC_login()

# -----------------------------------------------------------------------------

vlan_vars = {
  'name': 'Jeremy',
  'number': '100'
}

# use a template and render the vars immediately:
rpc = wlc.RpcMaker( 'SET', Template='vlan_create', TemplateVars=vlan_vars )

# alternatively you can invoke the render method if you don't provide
# TemplateVars in the constructor, for example:
# >>>
# vlan_vars['number'] = '200'
# rpc.render( vlan_vars )

print "Creating VLAN %s ..." % vlan_vars['name']

# execute the RPC and return the result
rsp = rpc()
