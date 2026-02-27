import json
from oggetti import *
from costanti import *

'''
Cose da salvare:
- stati
    - province
        - soldati
        - abitanti
        - riga - colonna
        - azioni
    - colore
    - soldi
    - punti_azione
    - spostamenti_truppe
- posizione, zoom camera
- colore stato principale gioco
'''

def converti_spostamento(spostamento):
    s = spostamento.copy()
    s['percorso'] = spostamento['percorso'].copy()
    for i in range(0, len(s['percorso'])):
        provincia = s['percorso'][i]
        s['percorso'][i] = (provincia.riga, provincia.colonna)
    return s

def converti_azioni(azioni):
    
    a = []

    for az in azioni:
        if az['azione'] == 'muovi':
            azione = az.copy()
            dest = azione['destinazione']
            azione['destinazione'] = (dest.riga, dest.colonna)
            a.append(azione)
        elif az['azione'] == 'arrivo truppe':
            azione = az.copy()
            azione['stato colore'] = azione['stato'].colore
            del azione['stato']
            a.append(azione)
        else:
            a.append(az)

    return a

def riconverti_spostamento(spostamento, mappa):
    for i in range(len(spostamento['percorso'])):
        riga = spostamento['percorso'][i][0]
        colonna = spostamento['percorso'][i][1]
        spostamento['percorso'][i] = mappa.province[riga][colonna]

    return spostamento

def trova_stato(stati, colore):
    for s in stati:
        if s.colore == colore:
            return s
    return None

def riconverti_azioni(stati, mappa, azioni):

    a = []

    for az in azioni:
        if az['azione'] == 'muovi':
            azione = az.copy()
            riga = azione['destinazione'][0]
            colonna = azione['destinazione'][1]
            azione['destinazione'] = mappa.province[riga][colonna]
            a.append(azione)
        elif az['azione'] == 'arrivo truppe':
            azione = az.copy()
            azione['stato'] = trova_stato(stati, azione['stato colore'])
            del azione['stato colore']
            a.append(azione)
        else:
            a.append(az)

    return a

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
                'riga': p.riga,
                'colonna': p.colonna,
                'soldati': p.soldati,
                'abitanti': p.abitanti,
                'azioni': converti_azioni(p.azioni)
            }
            province.append(provincia)

        spostamenti = []

        for sp in s.spostamenti_truppe:
            spostamenti.append(converti_spostamento(sp))

        stato = {
            'elenco_province': province,
            'colore': s.colore,
            'soldi': s.soldi,
            'punti_azione': s.punti_azione,
            'spostamenti_truppe': spostamenti
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
        spostamenti = []
        for sp in s['spostamenti_truppe']:
            spostamenti.append(riconverti_spostamento(sp, gioco.mappa))
        s['spostamenti_truppe'] = spostamenti
        gioco.stati[i].carica_dati(s, gioco.mappa)
        if gioco.stati[i].colore == dati['colore']:
            gioco.interfaccia.stato = gioco.stati[i]
            gioco.indice_truppe = i
        i += 1

    for riga in gioco.mappa.province:
        for p in riga:
            p.azioni = riconverti_azioni(gioco.stati, gioco.mappa, p.azioni)

    gioco.stati[0], gioco.stati[gioco.indice_truppe] = gioco.stati[gioco.indice_truppe], gioco.stati[0]
    
    gioco.indice_truppe = 0
    
    gioco.interfaccia.stato.renderizza_truppe()
    
    gioco.mappa.riferimento_vicine()

    file.close()
