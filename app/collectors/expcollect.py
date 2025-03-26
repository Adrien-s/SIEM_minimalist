import os
import win32evtlog
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
                #print(event_xml.find(f'.//{schemasmc}EventID').text)
                print(event_xml)
                break  # On ne traite qu'un événement pour le moment

    else:
        # Si pas admin, relance le script avec les droits admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        print("Redémarrage en mode administrateur...")
    return "End of logcollector"


if __name__ == '__main__':
    logcollector("C:\Windows\System32\winevt\Logs\Application.evtx")