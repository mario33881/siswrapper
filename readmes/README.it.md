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

1. Eseguendo il comando pip qui sotto:

    ```
    pip install siswrapper
    ```

2. Eseguire la build della wheel python utilizzando il comando seguente:

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

**2021-01-09 1.1.1:** <br>
### Fix/funzionalita' aggiuntive
* ```simulate()``` e' eseguito dal metodo ```parsed_output()```
anche quando viene inserito un input non valido (caratteri diversi da "0" e/o "1")
e quando viene eseguito il comando ```sim```
* ```simulate()``` e ```print_stats()``` puo' gestire correttamente gli output delle FSM (fix:```TypeError: 'NoneType' object is not subscriptable```)

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
