import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
from lxml.builder import E
from lxml import etree
from jinja2 import Template


wlc = WLC_login()
rpc = wlc.RpcMaker('set')


# for this example we'll set an example site location of 'SVL' for all converted APs and
# assume that we are putting all site radios into the 'default' radio profile
site = 'SVL'
radioprofile = 'default'


# create a jinja2 template for a new AP
dap_j2 = Template(u"""
  <DAP apnum="{{ apnum }}" fingerprint="{{ fp }}" model="{{ model }}" name="{{ name }}" 
      port="{{ port }}" serial-id="{{ serial }}" type="NG">
    <AP-BOOTCONFIG boot-image=""/>
    <AP-RADIO-TABLE>
      <AP-RADIO antenna-mode="DUAL-BAND-3SS" antennatype="INTERNAL" auto-config="YES" 
          channel="6" designation="INDOOR" enable="YES" external-antennas="0" 
          force-rebalance="NO" load-balance-enable="YES" load-balance-group="" 
          max-tuned-power="default" min-tx-rate="" slot="1" tx-power="21" type="NG">
        <RADIO-PROFILE-REF name="{{ radio1profile }}"/>
      </AP-RADIO>
      <AP-RADIO antenna-mode="DUAL-BAND-3SS" antennatype="INTERNAL" auto-config="YES" 
        channel="36" designation="INDOOR" enable="YES" external-antennas="0" 
        force-rebalance="NO" load-balance-enable="YES" load-balance-group="" 
        max-tuned-power="default" min-tx-rate="" slot="2" tx-power="11" type="NA">
        <RADIO-PROFILE-REF name="{{ radio2profile }}"/>
      </AP-RADIO>
    </AP-RADIO-TABLE>
    <AP-ETHERNET-TABLE/>
    <APINFO>
      <APCONTACT/>
      <APLOCATION/>
      <APDESCRIPTION/>
    </APINFO>    
    <VLAN-PROFILE-REF name=""/>
  </DAP> 
""")


# begin with a list of Auto APs from the announce status table
announce_table = wlc.rpc.get_stat_dap_announce_status_table()

# Auto APs have a special status, use this to identify our candidate APs
auto_aps = announce_table.findall(".//DAP-ANNOUNCE-STATUS[@status='AUTO']")

for ap in auto_aps:
    data = {}
    data.update(ap.attrib)
   
    rpc.data = E('DAP-TABLE')

    # load and customize the template for this AP
    rpc.data.append(etree.XML(dap_j2.render( radio1profile=radioprofile, 
        radio2profile=radioprofile, 
        serial=data['serial-id'], 
        name=site+data['dapnum'], 
        apnum=data['dapnum'], 
        model=data['model'], 
        fp=data['fingerprint'], 
        port=str(int(data['dapnum'])+2048))))

    print('Converting Auto AP: %s Site Name: %s' % (data['dapnum'], site+data['dapnum']))
        
    # execute the config operation
    r = rpc()
    
    # reboot the ap here, it should help speed up the process, but probably isn't 
    # strictly necessary
    # XXX - build a helper fn for rebooting  

# we've finished the conversion, now save the config
wlc.rpc.act_write_configuration()


