#!/usr/bin/env python
# Copyright (c) 2017 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
"""
IntfReactor.py

The purpose of this utility is to react to interface changes. This can be done with the built in event-handler 
feature in EOS, but each interface has to be defined individually. With this SDK based script, you can provide a
list of interfaces in which you can execute a script and pass the interface and status as variables.

The executed script when an interface changes status, must NOT be blocking.

Add the following configuration snippets to change the default behavior. For the list
of IPs to check, separate with a comma.

daemon IntfReactor
   exec /mnt/flash/IntfReactor.py
   option interfacelist value 'Ethernet1/1,Ethernet2/1'
   option script2execute value "/mnt/flash/gorun.sh"
   no shutdown

Note that with recent versions of EOS you need a SysdbMountProfile in /usr/lib/SysdbMountProfile that has the same name
as your SDK application (in this case InfReactor.py).

"""
#************************************************************************************
# Change log
# ----------
# Version 1.0.0  - 05/24/2017 - Jeremy Georges -- jgeorges@arista.com --  Initial Version
# Version 1.0.1  - 10/11/2017 - Jeremy Georges -- jgeorges@arista.com --  Updated comments on SysdbMountProfiles 
#
#*************************************************************************************
#
#
#****************************
#*     MODULES              *
#****************************
#
import sys
import syslog
import eossdk
import re
import subprocess

#***************************
#*     FUNCTIONS           *
#***************************

class intfReactor(eossdk.AgentHandler,eossdk.IntfHandler):
   def __init__(self, sdk, agentMgr, intfMgr):
      self.agentMgr = sdk.get_agent_mgr()
      self.tracer = eossdk.Tracer("intfReactorPythonAgent")
      eossdk.AgentHandler.__init__(self, self.agentMgr)
      eossdk.IntfHandler.__init__(self, intfMgr)
      syslog.syslog("IntReactor Python Agent - init")
      self.tracer.trace0("Python agent constructed")
      self.intfMgr_ = intfMgr
      self.agentMgr_ = agentMgr


   def on_initialized(self):
      self.tracer.trace0("Initialized")
      syslog.syslog("IntReactor Python Agent Initialized")
      self.agentMgr.status_set("Status:", "Administratively Up")
      INTERFACELIST = self.agentMgr.agent_option("interfacelist")
      if not INTERFACELIST:
         # No Interface list set
         self.agentMgr.status_set("Monitoring Interfaces:", "None")
      else:
         # Handle the initial state
         self.on_agent_option("interfacelist", INTERFACELIST)

      #Lets check the extra parameters and see if we should override the defaults
      ACTIONSCRIPT = self.agentMgr.agent_option("script2execute")
      if not ACTIONSCRIPT:
          # We have no script defined yet. We'll set status output to None
          self.agentMgr.status_set("script2execute", "None")
      else:
          #Set to initial config
          self.agentMgr.status_set("script2execute", ACTIONSCRIPT)
      #Lets watch all interfaces and we'll use our handler to check whether we care
      #about this interface or not.  Probably a better way to do this, but its easier
      #to handle configuration changes this way. We'll look at self.agentMgr.agent_option("interfacelist")
      #each time our handler gets called, that way we have the latest and greatest
      #list of interfaces.
      self.watch_all_intfs(True)


   def on_agent_option(self, optionName, value):
      #options are a key/value pair
      if optionName == "interfacelist":
         if not value:
            self.tracer.trace3("Interface List Deleted")
            self.agentMgr.status_set("Monitoring Interfaces:", "None")
         else:
            self.tracer.trace3("Adding Interface %s to list" % value)
            self.agentMgr.status_set("Monitoring Interfaces:", "%s" % value)
      if optionName == "script2execute":
         if not value:
            self.tracer.trace3("Script to Execute is deleted")
            self.agentMgr.status_set("script2execute:", "None")
         else:
            self.tracer.trace3("Adding script2execute %s" % value)
            self.agentMgr.status_set("script2execute:", "%s" % value)

   def on_agent_enabled(self, enabled):
      #When shutdown set status and then shutdown
      if not enabled:
         self.tracer.trace0("Shutting down")
         self.agentMgr.status_del("Status:")
         self.agentMgr.status_set("Status:", "Administratively Down")
         self.agentMgr.agent_shutdown_complete_is(True)
      else:
         self.tracer.trace0("Starting")
         self.agentMgr.status_del("Status:")
         self.agentMgr.status_set("Status:", "Administratively Up")
         self.agentMgr.agent_shutdown_complete_is(False)

   def on_oper_status(self, intfId, operState):
      """ Callback provided by IntfHandler when an interface's
      configuration changes """
      intfState = 'up' if operState == eossdk.INTF_OPER_UP else 'down'
      self.tracer.trace5("The state of " + intfId.to_string() +
                         " is now " + intfState)
      #Lets look at our options each time we get a callback, that way we have the
      #latest configuration settings

      IntList = self.agentMgr.agent_option("interfacelist")
      EachInterface = IntList.strip("'").split(',')

      for currentint in EachInterface:
          if re.search(r'\b{0}\b'.format(intfId.to_string()), currentint):
              syslog.syslog("The state of %s is now %s" % (intfId.to_string(),intfState) )
              SCRIPTNAME=self.agentMgr.agent_option("script2execute")
              #Run script
              if SCRIPTNAME:
                  syslog.syslog("Running Script %s passing %s and %s as arguments" % (SCRIPTNAME, intfId.to_string(), intfState))
                  #Execute the script. Lets just concatenate the full CLI and arguments
                  FULLCLI=SCRIPTNAME+' '+intfId.to_string()+' ' + intfState
                  try:
                      subprocess.call(FULLCLI, shell=True)
                  except:
                      syslog.syslog("Error executing %s " % FULLCLI)
              else:
                  syslog.syslog("No script name specified in config. Just alerting in syslog")


#=============================================
# MAIN
#=============================================
def main():
    syslog.openlog(ident="INTF-ALERT-AGENT",logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL0)
    sdk = eossdk.Sdk()
    _ = intfReactor(sdk, sdk.get_agent_mgr(), sdk.get_intf_mgr())
    sdk.main_loop(sys.argv)
    # Run the agent until terminated by a signal


if __name__ == "__main__":
    main()
