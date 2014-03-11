import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
from lxml.builder import E
from lxml import etree
from jinja2 import Template


wlc = WLC_login()
rpc = wlc.RpcMaker('set')


# for this example we'll build the Euclid compatible snoop filter pointing to the beta 
# portal IP address. We'll map the snoop filter to the 'default' radio profile. 

radioprofile = 'default'
euclid_ip = '23.23.125.65'


snoop_filter_j2 = Template(u"""
    <SNOOP-FILTER name="Euclid-{{ euclidtype }}" enable="YES">
      <SNOOP-OBSERVER-REF target="{{ ip }}"/>
      <SNOOP-CONDITION>
        <SNOOP-CONDITION-DIRECTION operation="EQ" direction="RECEIVE"/>
      </SNOOP-CONDITION>
      <SNOOP-CONDITION>
        <SNOOP-CONDITION-FRAME-TYPE operation="EQ" frame-type="{{ euclidtype }}"/>
      </SNOOP-CONDITION>
      <SNOOP-CONDITION>
        <SNOOP-CONDITION-TRANSMITTER-TYPE operation="NEQ" transmitter-type="MEMBER-AP"/>
      </SNOOP-CONDITION>
    </SNOOP-FILTER>
  """)
  
  
snoop_observer_j2 = Template(u"""  
  <SNOOP-OBSERVER-TABLE>
    <SNOOP-OBSERVER2 target="{{ ip }}" snap-length="0" inter-frame-gap-ms="30000" 
      transmission-mode="tzsp"/>
  </SNOOP-OBSERVER-TABLE>
""")


# we need to grab the existing radio profiles so we can add our snoop filter to it 
# without trashing existing config.
#
# Fyi, Snoop filters can also be applied to specific to radios, we use the radio profile 
# here for convenience 
# 
config = wlc.rpc.get_configuration()

# grab the radio profile we're interested in
rp = config.find(".//RADIO-PROFILE[@name='%s']" % (radioprofile))


# create the NSYSTEM object and add our snoop settings
rpc.data = E('NSYSTEM') 
filtertable = E('SNOOP-FILTER-TABLE')
for filtertype in ['PROBE', 'DATA']:
  filtertable.append(etree.XML(snoop_filter_j2.render( ip=euclid_ip, euclidtype=filtertype)))
rpc.data.append(filtertable)
rpc.data.append(etree.XML(snoop_observer_j2.render( ip=euclid_ip )))


# create the Snoop filter mapping and add it to the existing radio profile config
rp.append(E('SNOOP-FILTER-REF', {'name':'Euclid-PROBE'}))
rp.append(E('SNOOP-FILTER-REF', {'name':'Euclid-DATA'}))
rpc.data.append(rp)


r = rpc()


# we've finished creating the filter and mapping it, save config
wlc.rpc.act_write_configuration()


