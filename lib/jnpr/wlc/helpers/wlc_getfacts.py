def wlc_getfacts(wlc, *vargs, **kvargs):
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

  # run through each of the RPC commands and copy
  # the attribute values into the return :data:

  data = {}
  for rpc in run_list:
    rsp = rpc()                   
    data.update(rsp[0].attrib)    # values are in the XML attributes

  # make a copy of the facts into the WLC object as :facts:
  # attribute.  This is a "well known" attribute for the programmers
  
  wlc.facts = dict(data)

  return data