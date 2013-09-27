import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

##### -------------------------------------------------------------------------
##### =========================================================================
#####
#####                               MAIN SCRIPT
#####
##### =========================================================================
##### -------------------------------------------------------------------------

file_name = "myshowtech"

wlc = WLC_login()

print "Saving 'tech-support' data to file: %s" % file_name

wlc.rpc.act_save_tech_support( file_name=file_name )

print "Retriveing file listing and displaying 'user' directory"

def show_dir():
  file_dir = wlc.rpc.act_dir()
  user_dir = file_dir.xpath('DIR-RESP[@directory = "user"]')[0]

  for file_e in user_dir.xpath('DIR-ENTRY'):
    print("\t{file}: size={size} date={date}".format(
      file=file_e.attrib['name'],
      size=file_e.attrib['size'],
      date=file_e.attrib['date'] ))

show_dir()

print "\nNow removing the tech-support file"
wlc.rpc.act_filedel( path=file_name+".gz" )       # gz is added by WLC OS

print "Now showing the 'user' directory again"
show_dir()