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

  data = {}
  for rpc in run_list:
    rsp = rpc()                   
    data.update(rsp[0].attrib)    # values are in the XML attributes

  # make a copy of the facts into the WLC object
  wlc.facts = dict(data)

  return data