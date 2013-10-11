import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

# setup an RPC to edit the DAP-TABLE.  We set the :data: attribute rather than the 
# :target: attribute in this case as we are going to be making appends 
# (child elements) to :data.  Using *new* feature that checks the type of 
# the :data: on setattr.  If it's a string, then the RpcMaker will create the
# XML element; thus you don't need to import lxml.buildier anymore

rpc = wlc.RpcMaker('set')
rpc.data = 'DAP-TABLE'

# retrieve the DAP template

dap_template = wlc.Template('dap')

# assume that we are putting all site radios into the 'default' radio profile

radioprofile = 'default'

# create a list of AP data dictionaries; we're going to feed these through the
# template and append into the RPC.

ap_data = [
  dict(
    radio1profile=radioprofile, 
    radio2profile=radioprofile, 
    serial='SN12345', 
    name='AP-JEREMY',
    apnum='12',
    model='MODEL-123',
    fp='FingerPrint1',
    port=2048
  ),
  dict(
    radio1profile=radioprofile, 
    radio2profile=radioprofile, 
    serial='SN5678', 
    name='AP-TIM',
    apnum='32',
    model='MODEL-123',
    fp='FingerPrint2',
    port=2148
  )
]

# here using a *new* method called 'data_append' that takes XML as string
# and appends it to the :data: attribute.  this seems like a common enough
# task, so that's why it was added

for each in ap_data:
  rpc.data_append( dap_template.render( each ))

# now we have a complete DAP-TABLE transaction and we can push this to the WLC
# using:
# >>>
# r = rpc()

# then you can save it using:
# >>>
# wlc.ez.save_config()    
