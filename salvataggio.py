import json
from oggetti import *
from costanti import *

# converte gli spostamenti delle truppe per poterli salvare nel file
def converti_spostamento(spostamento):
    s = spostamento.copy()
    s['percorso'] = spostamento['percorso'].copy()
    for i in range(0, len(s['percorso'])):
        provincia = s['percorso'][i]
        s['percorso'][i] = (provincia.riga, provincia.colonna)
    return s

# riconverte gli spostamenti per poter essere usati nel gioco
def riconverti_spostamento(spostamento, mappa):
    for i in range(len(spostamento['percorso'])):
        riga = spostamento['percorso'][i][0]
        colonna = spostamento['percorso'][i][1]
        spostamento['percorso'][i] = mappa.province[riga][colonna]

    return spostamento

def converti_azioni(azioni):
    azioni2 = {}

    for p, az2 in azioni.items():
        a = []
        for az in az2:
            if az['azione'] == 'muovi':
                azione = az.copy()
                dest = azione['destinazione']
                azione['destinazione'] = (dest.riga, dest.colonna)
                a.append(azione)
            else:
                a.append(az.copy())
        azioni2[str(p.riga) + ',' + str(p.colonna)] = a

    return azioni2

def riconverti_azioni(azioni, mappa):
    azioni2 = {}

    for p, az2 in azioni.items():
        a = []
        for az in az2:
            if az['azione'] == 'muovi':
                azione = az.copy()
                riga = azione['destinazione'][0]
                colonna = azione['destinazione'][1]
                azione['destinazione'] = mappa.province[riga][colonna]
                a.append(azione)
            else:
                a.append(az.copy())
        riga, colonna = p.split(',')
        provincia = mappa.province[int(riga)][int(colonna)]
        azioni2[provincia] = a

    return azioni2

# trasforma un colore da tuple (es. (255, 255, 255)) a esadecimale (es. 0xff0xff0xff)
def converti_colore(colore):
    return f'{hex(colore[0])},{hex(colore[1])},{hex(colore[2])}'

# identifica gli stati in guerra con dei colori e le province con riga e colonna
def converti_guerra(guerra):
    guerra2 = {}
    for k, i in guerra.items():
        i2 = i.copy()
        lista = []
        for p in i2['province_conquistate']:
            lista.append((p.riga, p.colonna))
        i2['province_conquistate'] = lista
        guerra2[converti_colore(k.colore)] = i2
    
    return guerra2

def riconverti_guerra(guerra, mappa, stati, dati):
    guerra2 = {}
    for k, i in guerra.items():
        i2 = i.copy()
        lista = []
        for p in i2['province_conquistate']:
            riga = p[0]
            colonna = p[1]
            lista.append(mappa.province[riga][colonna])
        i2['province_conquistate'] = lista
        guerra2[trova_stato(stati, dati, k)] = i2
    
    return guerra2

# trova uno stato in base al colore
def trova_stato(stati, dati, colore):
    for i, s in enumerate(dati):
        if converti_colore(s['colore']) == colore:
            return stati[i]

# salva tutti i dati del gioco nel file .json
'''
Struttura del dizionario:
- stati
    - stati in guerra
    - province
        - soldati
        - abitanti
        - riga
        - colonna
    - colore
    - soldi
    - punti_azione
    - spostamenti_truppe
    - azioni
- posizione, zoom camera
- colore stato principale gioco
'''

def salva_dati(gioco): 
    dati = {
        'righe': gioco.mappa.num_righe,
        'colonne': gioco.mappa.num_colonne,
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
                'abitanti': p.abitanti
            }
            province.append(provincia)

        spostamenti = []

        for sp in s.spostamenti_truppe:
            spostamenti.append(converti_spostamento(sp))

        stato = {
            'elenco_province': province,
            'guerra': converti_guerra(s.guerra),
            'colore': s.colore,
            'soldi': s.soldi,
            'punti_azione': s.punti_azione,
            'spostamenti_truppe': spostamenti,
            'azioni': converti_azioni(s.azioni)
        }
        dati['stati'].append(stato)

    file = open(NOME_FILE, 'w')

    testo = json.dumps(dati)
    file.write(testo)

    file.close()

# carica i dati presenti nel file json
def carica_dati(gioco):

    file = open(NOME_FILE, 'r')

    testo = file.read()
    
    dati = json.loads(testo)

    gioco.camera.position = dati['camera']['posizione']
    gioco.camera.zoom = dati['camera']['zoom']

    gioco.mappa = Mappa(dati['righe'], dati['colonne'], RAGGIO)
    gioco.mappa.crea_province()
    
    gioco.stati.clear()
    for s in dati['stati']:
        gioco.stati.append(Stato())
    for i, s in enumerate(dati['stati']):
        spostamenti = []
        for sp in s['spostamenti_truppe']:
            spostamenti.append(riconverti_spostamento(sp, gioco.mappa))
        s['azioni'] = riconverti_azioni(s['azioni'], gioco.mappa)
        s['spostamenti_truppe'] = spostamenti
        s['guerra'] = riconverti_guerra(s['guerra'], gioco.mappa, gioco.stati, dati['stati'])
        stato = gioco.stati[i]
        stato.carica_dati(s, gioco.mappa)
        if stato.colore == dati['colore']:
            gioco.interfaccia.stato = stato
            gioco.indice_truppe = i

    gioco.stati[0], gioco.stati[gioco.indice_truppe] = gioco.stati[gioco.indice_truppe], gioco.stati[0]
    
    gioco.indice_truppe = 0
    
    gioco.interfaccia.stato.renderizza_truppe()
    
    gioco.mappa.riferimento_vicine()

    file.close()
