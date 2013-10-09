
import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
import jinja2
from lxml import etree
from lxml.builder import E

wlc = WLC_login()

   
def show_ap( wlc, *vargs, **kvargs ):
    # XXX - fix this to add ap statistics elements to the dict
    # XXX - add a filter for displaying ap details for an AP by name or serial
    run_list = [ wlc.rpc.get_stat_ap_radio_status ]

    data = {}
    for rpc in run_list:
        rsp = rpc()    
        ap_list = rsp.findall('.//DAP')
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

