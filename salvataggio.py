import json
from oggetti import *
from costanti import *

'''
Cose da salvare:
- stati
    - province
        - soldati
        - abitanti
        - riga
        - colonna
        - x
        - y
        - azioni
    - colore
    - soldi
    - punti_azione
    - spostamenti_truppe
- posizione, zoom camera
- colore stato principale gioco
'''

def salva_dati(gioco):
    dati = {
        'stati': [],
        'camera': {
            'posizione': gioco.camera.position,
            'zoom': gioco.camera.zoom
        },
        'colore': gioco.interfaccia.stato.colore
    }
    for s in gioco.stati:
        province = []
        for p in s.elenco_province:
            provincia = {
                'x': p.x,
                'y': p.y,
                'riga': p.riga,
                'colonna': p.colonna,
                'soldati': p.soldati,
                'abitanti': p.abitanti,
                'azioni': p.azioni
            }
            province.append(provincia)
        stato = {
            'elenco_province': province,
            'colore': s.colore,
            'soldi': s.soldi,
            'punti_azione': s.punti_azione,
            'spostamenti_truppe': s.spostamenti_truppe
        }
        dati['stati'].append(stato)

    file = open(NOME_FILE, 'w')

    testo = json.dumps(dati)
    file.write(testo)

    file.close()

def carica_dati(gioco):

    file = open(NOME_FILE, 'r')

    testo = file.read()
    
    dati = json.loads(testo)

    gioco.camera.position = dati['camera']['posizione']
    gioco.camera.zoom = dati['camera']['zoom']
    
    i = 0
    for s in dati['stati']:
        gioco.stati[i].carica_dati(s, gioco.mappa)
        if gioco.stati[i].colore == dati['colore']:
            gioco.interfaccia.stato = gioco.stati[i]
            gioco.indice_truppe = i
        i += 1

    gioco.stati[0], gioco.stati[gioco.indice_truppe] = gioco.stati[gioco.indice_truppe], gioco.stati[0]
    
    gioco.indice_truppe = 0
    
    gioco.interfaccia.stato.renderizza_truppe()
    
    gioco.mappa.riferimento_vicine()

    file.close()
