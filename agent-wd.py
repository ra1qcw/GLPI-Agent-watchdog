#-------------------------------------------------------------------------------
# Name:        glpi-agent-watchdog
# Purpose:
#
# Author:      ra1qcw
#
# Created:     27.09.2023
# Copyright:   (c) ra1qcw 2023
# Licence:
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()
    import requests
    import os
    import winreg
    import psutil


    def getService(name):

        service = None
        try:
            service = psutil.win_service_get(name)
            service = service.as_dict()
        except Exception as ex:
            print(str(ex))
        return service

    service = getService('GLPI-Agent')

    if (not service):
        print("Service not found. Exit.")
        os._exit(0)

    print(service['name'] + ' status: '+service['status'])

    access_registry = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)
    #access_key = winreg.OpenKey(access_registry,r"SOFTWARE\Microsoft\Windows\CurrentVersion")
    try:
     access_key = winreg.OpenKey(access_registry,r"SOFTWARE\GLPI-agent")
    except:
     access_key = winreg.OpenKey(access_registry,r"SOFTWARE\GLPI-agent", access=winreg.KEY_READ | winreg.KEY_WOW64_64KEY)

    glpi = winreg.QueryValueEx(access_key,"server")
    srv = glpi[0]

    if (srv.strip()==''):
     print("No server addres. Exit.");
     os._exit(0)

    print("Server: "+srv)

    agentPort = winreg.QueryValueEx(access_key,"httpd-port")
    agentPort = agentPort[0]
    if (agentPort.strip()==''):
     print("No agent port. Exit.");
     os._exit(0)
    print("Agent port: "+agentPort)

    from urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    try:
     response = requests.get('http://localhost:'+agentPort, verify=False, timeout=(3,5))
    except:
     resAgent = -1
    else:
     resAgent = response.status_code
    print('Agent answer: '+ ('OK' if resAgent==200 else 'Error'))
    if resAgent == 200:
     print('Exit.')
     os._exit(0)

    # Try again
    try:
     response = requests.get('http://localhost:62354', verify=False, timeout=(3,5))
    except:
     resAgent = -1
    else:
     resAgent = response.status_code
    print('Second Agent answer: '+('OK' if resAgent==200 else 'Error'))
    if resAgent == 200:
     print('OK. Exit.')
     os._exit(0)

    try:
     response = requests.get(srv, verify=False, timeout=(3,5))
    except:
     resSrv = -1
    else:
     resSrv = response.status_code
    print('Server answer: '+'OK' if resSrv==200 else 'Error')
    if resSrv != 200:
     os._exit(0)

    os.system('net stop GLPI-agent')
    os.system('net start GLPI-agent')
    
