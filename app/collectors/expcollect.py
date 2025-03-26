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
        # Ouvre le fichier d'événements
        query_handle = win32evtlog.EvtQuery(file_name,
            win32evtlog.EvtQueryFilePath,
            None  # Vous pouvez ajouter un filtre ici si nécessaire
        )
        # xml namespace, root element has a xmlns definition, so we have to use the namespace
        schemasmc = '{http://schemas.microsoft.com/win/2004/08/events/event}'

        while True:
            # Récupère 10 événements à la fois
            events = win32evtlog.EvtNext(query_handle,10)

            if not events:
                break

            for event in events:         
                # Convertit l'événement en XML pour l'affichage
                event_xml = win32evtlog.EvtRender(event, win32evtlog.EvtRenderEventXml)
                xml = ET.fromstring(event_xml)
                #substatus = xml[1][7].text  ????   
                event_id = xml.find(f'.//{schemasmc}EventID').text
                computer = xml.find(f'.//{schemasmc}Computer').text
                channel = xml.find(f'.//{schemasmc}Channel').text
                execution = xml.find(f'.//{schemasmc}Execution')
                process_id = execution.get('ProcessID')
                thread_id = execution.get('ThreadID')
                time_created = xml.find(f'.//{schemasmc}TimeCreated').get('SystemTime')

                event_data = f'Time: {time_created}, Computer: {computer}, Event Id: {event_id}, Channel: {channel}, Process Id: {process_id}, Thread Id: {thread_id}'
                print(event_data)
                #break

    else:
        # Si pas admin, relance le script avec les droits admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        print("Redémarrage en mode administrateur...")
    return "End of logcollector"


if __name__ == '__main__':
    logcollector("C:\Windows\System32\winevt\Logs\Application.evtx")