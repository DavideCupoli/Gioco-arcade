<h1 align="center">The Age of Conquests</h1>
<p>
The Age of Conquests è un gioco di strategia militare a turni. E' stato realizzato in python con la libreria arcade. Lo scopo del gioco è guidare uno Stato e invadere tutti gli altri Stati.
La mappa è costituita da diverse province, i cui confini hanno una forma esagonale. Ogni provincia appartiene a uno Stato. Il giocatore comanda uno Stato,
mentre gli altri sono controllati da BOT.
</p>
<p>
Uno Stato può conquistare la provincia di uno Stato nemico spostandovi il proprio esercito:
se il numero di soldati è maggiore rispetto a quello dell'esercito avversario, il controllo della provincia viene trasferito
 all'altro Stato. giocatori possono effettuare un numero di azioni indicato dalla freccia verde. Le azioni vengono poi
  soddisfatte quando si passa al turno successivo.
Gli Stati sono tenuti a gestire quanti soldi hanno e il loro bilancio (indicato dalla bilancia). Questi valori possono essere negativi nel caso in cui le spese superino le entrate.
</p>

**COMANDI PRINCIPALI**

FRECCETTE IN BASSO: movimento della visuale
<br>
<br>
TASTI PIU' e MENO: zoom
<br>
<br>
TASTO I: salvataggio del file .json
<br>
<br>
TASTO O: caricamento del file .json
<br>
<br>
BOTTONE ARRUOLA: permette di arruolare dei soldati nelle province selezionate appartenenti al tuo Stato. Seleziona la provincia in cui desideri arruolare i soldati e, dopo aver cliccato il bottone, apparirà una barra progressiva che permette di selezionare quante truppe devono essere arruolate; successivamente, clicca INVIO per confermare l'azione. Apparirà un numero verde, che indica quante truppe sono state arruolate.
<br>
<br>
BOTTONE MUOVI: permette di spostare delle truppe a un'altra provincia appartenente al tuo Stato o a uno Stato nemico. Seleziona la provincia della truppa che vuoi spostare; dopo aver cliccato il bottone muovi seleziona quanti soldati spostare; successivamente, seleziona la provincia di destinazione. Apparirà un numero rosso nella provincia di destinazione, che indica quante truppe arriveranno nel prossimo turno.
<br>
<br>
BOTTONE DICHIARA GUERRA: permette di dichiarare guerra allo Stato della provincia selezionata.
<br>
<br>
BOTTONE SCIOGLI: permette di sciogliere una truppa nel caso in cui si debba abbassare il costo di mantenimento dell'esercito. Il procedimento è lo stesso del comando arruola.
<br>
<br>
SPAZIO: permette di passare al turno successivo.