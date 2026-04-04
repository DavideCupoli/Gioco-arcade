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
            if v != None and v.stato != p.stato:
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

def provincia_vicina(provincia, province):
    vicina = province[0]
    lunghezza = len(trova_percorso(provincia, vicina))

    for p in province[1:]:
        l = len(trova_percorso(provincia, p))
        if l < lunghezza:
            vicina = p
            lunghezza = l
    return vicina

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

        if (random.random() < 1/100 and
            stato.guerra == {} and
            len(gioco.stati) > 2):
            stati_vicini = stato.stati_vicini(False)
            indice = random.randint(0, len(stati_vicini) - 1)
            stato.dichiara_guerra(stati_vicini[indice])

        confini = riordina_province(stato.ottieni_confini(True, True))
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

            for provincia in confini:
                soldati = stato.massimo_soldati(provincia)
                if soldati > provincia.soldati and stato.punti_azione > 0:
                    stato.arruola_soldati(soldati, provincia)
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
        
        if gioco.interfaccia.stato in stato.guerra and len(gioco.interfaccia.stato.elenco_province) == 0:
            stato.guerra.pop(gioco.interfaccia.stato, None)

        gioco.nuovo_turno(stato)
