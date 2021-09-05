# SISWRAPPER

![Siswrapper](https://github.com/mario33881/siswrapper/workflows/Siswrapper/badge.svg)

Siswrapper e' un **wrapper per [SIS](https://jackhack96.github.io/logic-synthesis/sis.html)**, lo strumento di sintesi e ottimizzazione di circuiti sequenziali.

Siswrapper permette agli sviluppatori di scrivere codice che integra SIS.

> Read this README in:
>
> |[English](../README.md)|[Italiano](readmes/README.it.md)|
> |-|-|

<p align="center">
    <img height="150px" alt="logo" src="../images/logo.svg">
</p>

<br>

<br>


> **Attenzione:**
>
> Non sono affiliato con gli sviluppatori di SIS in alcun modo.
>
> L'obiettivo di questa libreria e' permettere agli sviluppatori di utilizzare SIS attraverso il linguaggio di programmazione Python.

## Indice
* [Descrizione](#descrizione)
* [Requisiti](#requisiti)
* [Installazione](#installazione)
* [Guida all'uso](#guida-alluso)
* [Changelog](#changelog)
* [Autore](#autore)

## Descrizione ![](https://i.imgur.com/wMdaLI0.png)
Questa libreria permette agli sviluppatori di
**controllare SIS via Python** utilizzando una istanza della classe ```siswrapper.Siswrapper```.

Questo e' possibile grazie a **pexpect**,
libreria Python che permette facilmente di controllare shell interattive
attraverso un processo eseguito in background.

[Torna all'indice](#indice)

## Requisiti ![](https://i.imgur.com/H3oBumq.png)
* Sistema operativo Unix-like
    > pexpect non possiede tutte le funzionalita' necessarie su Windows 
    > e SIS funziona al 100% su linux
* Python 3
* la libreria pexpect per Python: permette di controllare shell interattive attraverso Python
* SIS, impostato nelle variabili di ambiente (eseguibile con il comando ```sis```): lo strumento per la sintesi e l'ottimizzazione di circuiti sequenziali
    > E' possibile [scaricarlo da questa pagina](https://jackhack96.github.io/logic-synthesis/sis.html)

[Torna all'indice](#indice)

## Installazione
Puoi installare questa libreria nei seguenti modi:

* (Metodo piu' semplice) Eseguendo il comando pip qui sotto:

    ```
    pip install siswrapper
    ```

* Eseguire la build della wheel python utilizzando il comando seguente:

    ```
    python3 setup.py bdist_wheel
    ```

    E installare la wheel eseguendo questo comando:

    ```
    pip install siswrapper-<version>-py3-none-any.whl
    ```
    > ```<version>``` dipende dalla versione di siswrapper

[Torna all'indice](#indice)

## Guida all'uso
Dopo aver installato siswrapper puoi importare siswrapper
all'interno di uno script o dall' interprete.

```python
import siswrapper
```

Adesso puoi istanziare un oggetto dalla classe ```siswrapper.Siswrapper()```:

```python
sis = siswrapper.Siswrapper()
```
Questa istruzione esegue un processo in background utilizzando pexpect
e prepara variabili di stato dell'oggetto.

Da ora in poi e' possibile eseguire comandi SIS utilizzando Python:

```python
sis.stop()  # ferma la sessione di SIS

sis.start() # crea una nuova sessione di SIS
            # > operazione eseguita automaticamente durante la creazione della instanza 
            # > ( utile dopo la esecuzione di sis.stop() )

path = "file.blif"
sis.read_blif(path)  # leggi il file blif

sis.simulate("010010") # esegue una simulazione
                       # > Non c'e' bisogno di mettere spazi tra ogni input come su SIS!!

# ottimizza un circuito con lo script rugged
sis.script_rugged()

# exec() esegue un comando che non e' attualmente supportato
# da questa libreria
sis.exec("help write_blif")

# prova ad eseguire un comando ed effettuare il parsing dell'output
# senza chiamare direttamente il metodo corretto
# > se il comando non viene riconosciuto viene eseguito da exec()
sis.parsed_exec("simulate 00 10 11")  # chiamera' sis.simulate()

# salva il circuito in un nuovo file blif
sis.write_blif("ottimizzato.blif")

# se necessario e' possibile interagire con la shell di SIS
sis.interact()
```

Tutti i metodi restituiscono un dizionario con:
* uno stato di uscita di successo del comando (che puo' essere False o True)
* lista di errori (vuota se non ci sono errori)
* lista di warning (vuota se non ci sono warning, presente solo per quei comandi che possono restituire warning)
* stdout del comando (None se il comando non restituisce niente)
* output del comando SI (solo per i comandi che restituiscono dati)

[Torna all'indice](#indice)

## Changelog ![](https://i.imgur.com/SDKHpak.png)
**2021-09-05 1.2.2:** <br>
### Fixes
* I comandi che mostrano l'output su piu' pagine non vanno piu' in timeout
    > Un esempio di comando che andava in timeout era ```help read_blif```.
* Il metodo ```exec()``` non memorizzava gli errori del metodo ```wait_end_command()``` correttamente

**2021-03-16 1.2.1:** <br>
### Fix
* Il comando ```print_stats``` falliva il parsing dell'output del comando print_stats quando il circuito aveva piu' di 10000 letterali/stati

**2021-03-16 1.2.0:** <br>
### Funzionalita' aggiunte
* Aggiunto il comando ```bsis_script``` command. I suoi parametri sono:
    * ```fsm_autoencoding_area```, utile per le FSM: minimizza gli stati, assegna automaticamente la codifica degli stati, ottimizza l'area e mappa il circuito per area (libreria synch)
        > Esegue ```state_minimize stamina```, ```state_assign jedi```, ```source script.rugged```, ```read_library synch.genlib```, ```map -m 0 -W -s```
    * ```fsm_autoencoding_delay```, utile per le FSM: minimizza gli stati, assegna automaticamente la codifica degli stati, ottimizza il ritardo e mappa il circuito per ritardo (libreria synch)
        > Esegue ```state_minimize stamina```, ```state_assign jedi```, ```reduce_depth```, ```source script.rugged```, ```read_library synch.genlib```, ```map -n 1 -W -s```
    * ```fsm_area```, utile per le FSM: minimizza gli stati, usa la codifica manuale degli stati, ottimizza l'area e mappa il circuito per area (libreria synch)
        > Esegue ```state_minimize stamina```, ```stg_to_network```, ```source script.rugged```, ```read_library synch.genlib```, ```map -m 0 -W -s```
    * ```fsm_delay```, utile per le FSM: minimizza gli stati, usa la codifica manuale degli stati, ottimizza il ritardo e mappa il circuito per ritardo (libreria synch)
        > Esegue ```state_minimize stamina```, ```stg_to_network```, ```reduce_depth```, ```source script.rugged```, ```read_library synch.genlib```, ```map -n 1 -W -s```
    * ```lgate_area_mcnc```, utile per i circuiti combinatori: ottimizza l'area e mappa il circuito per area (libreria mcnc)
        > Esegue ```source script.rugged```, ```read_library mcnc.genlib```, ```map -m 0 -W -s```
    * ```lgate_delay_mcnc```, utile per i circuiti combinatori: ottimizza il ritardo e mappa il circuito per ritardo (libreria mcnc)
        > Esegue ```reduce_depth```, ```source script.rugged```, ```read_library mcnc.genlib```, ```map -n 1 -W -s```
    * ```lgate_area_synch```, utile per i circuiti combinatori: ottimizza l'area e mappa il circuito per area (libreria synch)
        > Esegue ```source script.rugged```, ```read_library synch.genlib```, ```map -m 0 -W -s```
    * ```lgate_delay_synch```, utile per i circuiti combinatori: ottimizza il ritardo e mappa il circuito per ritardo (libreria synch)
        > Esegue ```reduce_depth```, ```source script.rugged```, ```read_library synch.genlib```, ```map -n 1 -W -s```
    * ```fsmd_area```, utile per le FSMD (circuiti che includono datapath e FSM): ottimizza l'area e mappa il circuito per area (libreria synch)
        > Esegue ```source script.rugged```, ```read_library synch.genlib```, ```map -m 0 -W -s```
    * ```fsmd_delay```, utile per le FSMD (circuiti che includono datapath e FSM): ottimizza il ritardo e mappa il circuito per ritardo (libreria synch)
        > Esegue ```reduce_depth```, ```source script.rugged```, ```read_library synch.genlib```, ```map -n 1 -W -s```

    > Il comando visualizza anche i comandi eseguiti e le statistiche dopo i comandi che eseguono modifiche importanti ai circuiti

    > I risultati parziali e completi dei comandi vengono scritti su nuovi file BLIF.

    > ATTENZIONE! L'esecuzione di questi comandi in questo ordine non garantisce il risultato migliore: la minimizzazione multilivello non e' esatta!
    > per ottenere risultati migliori si e' invitati ad eseguire manualmente i comandi in ordine sparso (ed eventualmente eseguire gli stessi comandi piu' volte)
* Adesso questa libreria verifica se il comando stg_to_network ha successo

### Fix
* Adesso il metodo ```write_eqn``` viene eseguito quando il comando ```write_eqn``` viene passato al metodo ```parsed_output()```.
    > Prima veniva eseguito il metodo ```write_blif```
* Richiamando il metodo ```write_eqn``` e ```write_blif``` senza parametri non restituisce piu' il comando nell'output.
* Quando SIS non e' installato sul computer il messaggio di errore mostra esattamente quale e' il problema
* Non e' possibile eseguire lo script rugged se non sono stati letti file con un comando read
* Quando si esegue un comando read, viene richiamato il metodo ```reset``` per terminare la sessione di SIS attuale e avviarne
  una nuova all'interno della cartella del file in input
    > In questo modo si "risolve" l'errore ".search x file not found" quando si cerca di leggere un file che si trova in un'altra cartella e che usa la keyword .search.
    >
    > Questo errore era normale ma non intuitivo (perche' il file era presente nella cartella del file in input ma non nella cartella corrente).
    > Era il comportamento di SIS.

**2021-01-09 1.1.1:** <br>
### Fix/funzionalita' aggiuntive
* ```simulate()``` e' eseguito dal metodo ```parsed_output()```
anche quando viene inserito un input non valido (caratteri diversi da "0" e/o "1")
e quando viene eseguito il comando ```sim```
* ```simulate()``` e ```print_stats()``` puo' gestire correttamente gli output delle FSM (fix:```TypeError: 'NoneType' object is not subscriptable```)

### Bug noti
* Il comando ```write_blif``` viene eseguito quando si passa il comando ```write_eqn``` al metodo ```parsed_output()```.
* Quando SIS non e' installato sul computer il messaggio di errore e' incompleto (quindi non facile da capire per l'utente finale)

**2021-01-04 1.1.0:** <br>
### Funzionalita' aggiunte
* Aggiunto il metodo ```parsed_output()```:
  legge un comando e chiama automaticamente il metodo migliore 
  per fare il parsing dell'output del comando stesso.
  
  Se il comando non viene riconosciuto verra' eseguito dal metodo ```exec()```.

### Cambiamenti
* Il metodo ```simulate()``` adesso restituisce una stringa con gli output (senza spazi tra ogni bit di output):
    > non c'era motivo di effettuare calcoli con l'output di simulate
    > quindi il tipo stringa ha piu' senso

### Fix
* Adesso il metodo ```exec()``` sa come gestire i comandi ```quit``` 
  e ```exit``` senza lanciare Exception.
  
**2020-11-14 1.0.0:** <br>
Primo commit

[Torna all'indice](#indice)

## Autore ![](https://i.imgur.com/ej4EVF6.png)
[Stefano Zenaro (mario33881)](https://github.com/mario33881)
