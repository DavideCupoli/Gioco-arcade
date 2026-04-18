import random
from matematica import *
from costanti import *

# GESTIONE BOT

# riordina province in base a quante province nemiche confinanti hanno in ordine decrescente
def riordina_province(province):
    lista = []
    for i in range(len(province)):
        p = province[i]
        nemiche = 0
        for v in p.province_vicine().copy():
            if v != None and v.stato != p.stato and v.stato in p.stato.guerra:
                nemiche += 1
        
        elemento = {
            'provincia': p,
            'nemiche': nemiche
        }

        if lista == []:
            lista.append(elemento)
        else:
            pos = len(lista)
            for j in range(len(lista)):
                if lista[j]['nemiche'] > nemiche:
                    pos = j
                    break
            lista.insert(pos, elemento)
    province_riordinate = []
    for e in lista:
        province_riordinate.append(e['provincia'])
    return province_riordinate

# resistuisce le n truppe con il numero maggiore di soldati, in ordine crescente
def truppe_maggiori(province, numero, confini):

    tm = [None] * numero

    for t in province:
        if not t in confini and t.soldati > 0:
            indice = -1
            for i in range(numero):
                if tm[i] != None and t.soldati < tm[i].soldati:
                    break
                indice = i
            if indice != -1:
                tm.insert(indice + 1, t)
                tm.pop(0)

    while None in tm:
        tm.remove(None)

    return tm

# trova la provincia più vicina
def provincia_vicina(provincia, province):
    vicina = province[0]
    lunghezza = len(trova_percorso(provincia, vicina))

    for p in province[1:]:
        l = len(trova_percorso(provincia, p))
        if l < lunghezza:
            vicina = p
            lunghezza = l
    return vicina

# il bot arruola quanti pù soldati può nelle province dove ce ne sono pochi, finché non finiscono i punti azione
def arruola_soldati(stato, province, p2=[]):
    p = []
    for provincia in province:
        if not provincia in p2:
            soldati = stato.massimo_soldati(provincia)
            if soldati > provincia.soldati and stato.punti_azione > 0:
                stato.arruola_soldati(soldati, provincia)
                p.append(provincia)
    return p

# muove i soldati lungo il confine dello Stato
def muovi_soldati_confine(stato, confini):
    for p in confini:
        if p.soldati > 0:
            vicine = p.province_vicine()
            prov_confinanti = []
            for v in vicine:
                if v != None and v.stato != stato and v.stato in stato.guerra:
                    prov_confinanti.append(v)
            soldati = p.soldati // len(prov_confinanti)
            if soldati > 0:
                for c in prov_confinanti:
                    if stato.punti_azione > 0:
                        stato.aggiungi_spostamento(soldati, p, c)
                    else:
                        break

# muove i soldati interni verso il confine dello Stato
def muovi_soldati_interni(stato, confini):
    if len(confini) != 0:

        for i, t in enumerate(
            truppe_maggiori(
                stato.elenco_province,
                3 - (PUNTI_AZIONE - stato.punti_azione),
                confini
            )
        ):
            stato.aggiungi_spostamento(
                t.soldati,
                t,
                provincia_vicina(t, confini)
            )

# dichiara guerra a uno Stato casuale in momenti casuali
def dichiara_guerra(gioco, stato):
    if (random.random() < 1/100 and
        stato.guerra == {} and
        len(gioco.stati) > 2):
        stati_vicini = stato.stati_vicini(False)
        indice = random.randint(0, len(stati_vicini) - 1)
        stato.dichiara_guerra(stati_vicini[indice])

def sciogli(stato):
    for p in stato.elenco_province:
        if p.soldati > 0:
            stato.sciogli_soldati(p.soldati, p)

# algoritmo del bot
def gestisci_bot(gioco):
    if len(gioco.stati) == 1:
        gioco.turno_stato = 0
        return
    while gioco.turno_stato != 0:
        stato = gioco.stati[gioco.turno_stato]

        if len(stato.elenco_province) == 0:
            gioco.rimuovi_stato(stato)
            gioco.turno_stato -= 1
            gioco.indice_truppe = 0
            gioco.nuovo_turno(stato)
            return
        
        if stato.guerra == {}:
            sciogli(stato)

        dichiara_guerra(gioco, stato)

        confini = riordina_province(stato.ottieni_confini(True, True))

        muovi_soldati_interni(stato, confini)

        province = arruola_soldati(stato, confini)
        muovi_soldati_confine(stato, confini)
        arruola_soldati(stato, confini, province)

        if gioco.interfaccia.stato in stato.guerra and len(gioco.interfaccia.stato.elenco_province) == 0:
            stato.guerra.pop(gioco.interfaccia.stato, None)
            gioco.interfaccia.stato.guerra.pop(stato, None)

        gioco.nuovo_turno(stato)
