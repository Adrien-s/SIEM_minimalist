import os
import win32evtlog
import xml.etree.ElementTree as ET
import ctypes
import sys

# Attention : pour utiliser ce code, vous devez avoir les droits administrateur

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print("Erreur lors de la vérification des droits admin :", e)
        return False

def logcollector(file_name):
    if is_admin():
        print("Exécution en mode admin")
        query_handle = win32evtlog.EvtQuery(file_name,
            win32evtlog.EvtQueryFilePath,
            None
        )
        schemasmc = '{http://schemas.microsoft.com/win/2004/08/events/event}'
        event_datas = []
        while True:
            events = win32evtlog.EvtNext(query_handle, 10)
            if not events:
                break
            for event in events:         
                event_xml = win32evtlog.EvtRender(event, win32evtlog.EvtRenderEventXml)
                xml = ET.fromstring(event_xml)

                print(ET.tostring(xml, encoding='unicode'))

                event_id = xml.find(f'.//{schemasmc}EventID').text
                computer = xml.find(f'.//{schemasmc}Computer').text
                channel = xml.find(f'.//{schemasmc}Channel').text
                execution = xml.find(f'.//{schemasmc}Execution')
                process_id = execution.get('ProcessID')
                thread_id = execution.get('ThreadID')
                time_created = xml.find(f'.//{schemasmc}TimeCreated').get('SystemTime')
                level = xml.find(f'.//{schemasmc}Level').text

                # Retourner un dictionnaire pour chaque événement
                event_data = {
                    "time": time_created,
                    "computer": computer,
                    "event_id": event_id,
                    "channel": channel,
                    "process_id": process_id,
                    "thread_id": thread_id,
                    "level": level
                }
                event_datas.append(event_data)
                print(event_data)
    else:    
        # Si non admin, relance le script avec les droits administrateur
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        print("Redémarrage en mode administrateur...")
        event_datas = [] 
    return event_datas



if __name__ == '__main__':
    logcollector("C:\Windows\System32\winevt\Logs\Application.evtx")