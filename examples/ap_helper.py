
import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
import jinja2
from lxml import etree
from lxml.builder import E

wlc = WLC_login()

   
def show_ap( wlc, *vargs, **kvargs ):
    rsp = wlc.rpc.get_stat_ap_radio_status()
    ap_list = rsp.findall('.//DAP')
    data = {}
    
    for ap in ap_list:
        data[ap.get('apnum')] = {}
        data[ap.get('apnum')].update(ap.attrib)
      
    return data
  
    
def boot_ap( wlc, *vargs, **kvargs ):
    # XXX - add a filter for booting AP by name or serial
    rpc = wlc.RpcMaker('act')
    
    rpc.data = E('BOOT', E('BOOT-DAP', E('DAP-REF')))

    if 'apnum' in kvargs:
        dapref = rpc.data.find('.//DAP-REF')
        dapref.set('dap-id', kvargs['apnum'])
        
        r = rpc()
    else:
        raise ValueError("You must provide an AP number")

    return True


# bind the helper to the WLC
wlc.ez( helper=show_ap )
wlc.ez( helper=boot_ap )

