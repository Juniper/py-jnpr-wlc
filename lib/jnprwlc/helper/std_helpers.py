
def _wlc_getfacts(wlc, *vargs, **kvargs):
  """
    return a merged dict of the following:
    - BOOTSTATUS 
    - SYSTEMSTATUS
    - SYSTEMGLOBAL

    wlc: WLC object
  """

  run_list = [ wlc.rpc.get_bootstatus,
               wlc.rpc.get_systemstatus,
               wlc.rpc.get_systemglobal ]

  data = {}
  for rpc in run_list:
    rsp = rpc()                   
    data.update(rsp[0].attrib)    # values are in the XML attributes

  return data

## anything included in the 'std_rpc_helpers' will automatically
## be added to the WLC 'ez' attribute when the WLC object is
## initially created. 

std_rpc_helpers = {
  'facts': _wlc_getfacts
}
