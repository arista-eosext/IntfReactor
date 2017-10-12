# IntfReactor.py

The purpose of this utility is to react to interface changes. This can be done with the built in event-handler  
feature in EOS, but each interface has to be defined individually. 

Example:
```
event-handler TEST
   trigger on-intf Ethernet1 operstatus  <---currently forces us to select one interface
   action bash script
```
On the other hand, with this SDK based script, you can provide a list of interfaces in which you can execute
a script and pass the interface and status as variables.

# Author
Jeremy Georges - Arista Networks   - jgeorges@arista.com

# Description
IntfReactor

The purpose of this utility is to react to interface changes. This can be done with the built in AEM
feature in EOS, but each interface has to be defined individually. With this SDK based script, you can provide a
list of interfaces in which you can execute a script and pass the interface and status as variables.

The executed script when an interface changes status, must NOT be blocking.

Add the following configuration snippets to change the default behavior. For the list
of Interfaces to check, separate with a comma.
```
daemon IntfReactor
   exec /usr/local/bin/IntfReactor
   option interfacelist value 'Ethernet1,Ethernet2'
   option script2execute value "/mnt/flash/gorun.sh"
   no shutdown
```
This requires the EOS SDK extension installed if its < EOS 4.17.0 release.
All new EOS releases include the SDK.

## Example

### Output of 'show daemon' command
```
router1#show daemon IntfReactor 
Agent: IntfReactor (shutdown)
Configuration:
Option               Value                  
-------------------- ---------------------- 
interfacelist        'Ethernet1,Ethernet2'  
script2execute       "/mnt/flash/gotest.sh" 

Status:
Data                         Value                  
---------------------------- ---------------------- 
Monitoring Interfaces:       'Ethernet1,Ethernet2'  
Status:                      Administratively Down  
script2execute               "/mnt/flash/gotest.sh" 

```

### Syslog Messages
```
May 24 20:18:13 router1 INTF-ALERT-AGENT[5696]: IntReactor Python Agent Initialized
May 24 20:18:19 router1 Ebra: %LINEPROTO-5-UPDOWN: Line protocol on Interface Ethernet1, changed state to down
May 24 20:18:19 router1 INTF-ALERT-AGENT[5696]: The state of Ethernet1 is now down
May 24 20:18:19 router1 INTF-ALERT-AGENT[5696]: Running Script "/mnt/flash/gotest.sh" passing Ethernet1 and down as arguments
May 24 20:18:20 router1 Ebra: %LINEPROTO-5-UPDOWN: Line protocol on Interface Ethernet1, changed state to up
May 24 20:18:20 router1 INTF-ALERT-AGENT[5696]: The state of Ethernet1 is now up
May 24 20:18:20 router1 INTF-ALERT-AGENT[5696]: Running Script "/mnt/flash/gotest.sh" passing Ethernet1 and up as arguments
```



# INSTALLATION:
Copy to the /mnt/flash directory of each Arista switch that you want to use IntReactor.py on.
Ideally, use the RPM to install this as a package. If you do so, it will install the python executable
file in /usr/local/bin. Addtionally, with newer versions of EOS, a SysdbMountProfile is required. This file 
must be placed in the /usr/lib/SysdbMountProfiles directory. It must also be named the same as the filename
of the SDK application. The RPM will handle all of this, so its the preferred method of distribution.



License
=======
BSD-3, See LICENSE file
