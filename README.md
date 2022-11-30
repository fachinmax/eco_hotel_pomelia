# Eco hotel Pomelia
Questo progetto permette di salvare sulla blockchain i dati inerenti l'energia prodotta e consumanta da un
impianto energetico, garantendo che le informazioni inviate verranno salvate per sempre rimanendo immutabili. Inoltre
offre un sistema di autenticazione e di registrazione in modo che gli utenti autenticati possano visualizzare in maniera
semplice e immediata le informazioni salvate sulla blockchain.
Esso a differenza di altri progetti memorizza i dati solamente sulla blockchain in quanto è un database distribuito
e pubblico e per tanto non risulta la necessità di memorizzare i dati in un altro database, permettendo di essere utilizzato
anche da sistemi che hanno poca memoria.
## Funzionalità
Questa web-app riceve, attraverso una richiesta HTTPS, un oggetto JSON, es:
```python
{
    "produced_energy_in_watt": 23412424324,
    "consumed_energy_in_watt": 98097689879
}
```
all'API: "local/data" e memorizza i dati sulla propria blockchain.
Inoltre all'API "local/data" ritorna una lista di oggetti JSON con i relativi dati memorizzati sulla blockchain.
La web-app ha un sistema di autenticazione che permette di mostrare determinati dati e permette maggiori funzionalità
agli utenti amministratori e di mostrare altre informazioni agli altri utenti non amministratori.
Offre una pagina dove l'utente può modificare i dati del proprio account e di aumentare la priorità per l'esecuzine di
una transazione sulla blockchain (questa seconda funzionalità è possibile solamente per gli utenti amministratori).
Un ulteriore funzionalità è quella di mostrare un messaggio che informa l'utente amministratore se è diverso dall'ultimo
amministratore autenticato.
Ogni utente autenticato può visualizzare sia i dati salvati sulla blockchain (l'hash della transazione, la data,
l'energia prodotta e conumata e una pagina) sia i dati relativi alla blockchain (quantità di denaro, costo per una
transazione, l'ultimo blocco minato, ...).

## Blockchain come database
Come scritto nel capitolo precedente, invece di salvare i dati nel database, utilizzo la blockchain come database.
Salvo ogni transazione come se fosse un nodo di una coda: ogni nodo che salvo contiene un puntatore cioè l'hash della 
precedente transazione. In questo modo posso con un unico dato: l'hash dell'ultima transazione ottenere tutte le
transazioni salvate sulla blockchain.

## Installazione
Per poter eseguire il programma bisogna installare Redis e avviare il server:
```python
pip install django-redis
redis-server
```
