#!/usr/bin/env python3
"""Script che implementa un Server per la gestione dei messaggi
   all'interno di una chatroom di gruppo."""

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import signal
import time

""" Funzione che accetta le connessioni dei client in entrata.
    Per ogni connessione in entrata, questa funzione effettua l'operazione di fork,
    lanciando un thread separato per ogni client connesso."""
def accept_connections():
    while True:
        # Se il server chiude la connessione, cattura l'eccezione corrispondente e termina l'esecuzione.
        try:
            client, client_address = SERVER.accept()
        except OSError:
            break
        
        # Gestisce la connessione in entrata avviando il thread separato.
        print("%s:%s has connected to the server." % client_address)
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

""" Funzione che gestisce la connessione di un singolo client.
    Il parametro di ingresso è il socket assegnato al client. """
def handle_client(client):
    # Richiede al client l'inserimento del nome.
    # Per evitare nomi duplicati, verifica la validità del nome inserito,
    # ed eventualmente ne richiede nuovamente l'inserimento.
    client.send(bytes("Salve! Digita il tuo Nome seguito dal tasto Invio!", "utf8"))
    try:
        name = client.recv(BUFFSIZE).decode("utf8")
        while not valid_name(name):
            invalid_name = "Il nome scelto è già assegnato, inserire un nome diverso:"
            client.send(bytes(invalid_name, "utf8"))
            name = client.recv(BUFFSIZE).decode("utf8")
        # Se l'utente esce durante la scelta del nome, chiude la connessione.
        if name == "{quit}":
            close_client_connection(client)
            return 0

        names.append(name)
        greetings = 'Benvenuto %s! Se vuoi lasciare la Chat, scrivi {quit} per uscire.' % name
        client.send(bytes(greetings, "utf8"))
        # Avvisa tutti gli utenti connessi che un nuovo utente si è unito alla chat
        msg = "%s si è unito alla chat!" % name
        broadcast(bytes(msg, "utf8"))
        
    # Si mette in ascolto del thread del singolo client e ne gestisce l'invio dei messaggi o l'uscita dalla Chat.
    # La ricezione del messaggio {quit} provoca la chiusura della connessione con il client.
        while True:
            msg = client.recv(BUFFSIZE)
            if msg != bytes("{quit}", "utf8"):
                broadcast(msg, name+": ")
            else:
                close_client_connection(client)
                # Avvisa tutti gli utenti connessi che il client ha lasciato la chat.
                broadcast(bytes("%s ha abbandonato la Chat." % name, "utf8"))
                names.remove(name)
                break
    # Se il server interrompe la connessione, termina l'esecuzione del thread.
    except OSError:
        pass

""" Funzione che gestisce la chiusura della connessione con il client.
    Dopo aver chiuso la connessione, stampa sul terminale un messaggio di avviso."""
def close_client_connection(client):
    client.close()
    print("%s:%s has left the server." % addresses[client])
    del addresses[client]

""" Verifica se il nome passato in input è valido."""
def valid_name(name):
    return name != None and name not in names

""" Questa funzione invia un messaggio in broadcast a tutti i client.
    Il parametro msg contiene i byte del messaggio da inviare,
    mentre il secondo parametro è una stringa che contiene il nome dell'utente che invia il messaggio."""
def broadcast(msg, prefix=""):
    for client in addresses:
        client.send(bytes(prefix, "utf8")+msg)

""" Questa funzione gestisce la chiusura del server nel caso venga ricevuto un segnale di interruzione
    da tastiera (CTRL+C) """
def close_server(signal, frame):
    print("CTRL+C pressed. Closing the server...")    
    # Invia a tutti i client il messaggio di fine connessione
    msg = "{end_conn}"
    broadcast(bytes(msg, "utf8"))
    # Dealloca le risorse occupate dalle socket, provocando anche la terminazione dei thread
    for client in addresses:
        client.close()
    SERVER.close()

""" Funzione necessaria per intercettare i segnali da tastiera.
    Ad ogni ciclo, attende per un tempo stabilito prima di controllare se è stato ricevuto
    un segnale di interruzione (SIGINT).
    La condizione di uscita è la terminazione del thread di accettazione delle richieste. """
def wait_signal(wait_interval):
    while ACCEPT_THREAD.is_alive():
        time.sleep(wait_interval)
    
#Gestisce la chiusura del server quando viene premuto CTRL+C.
signal.signal(signal.SIGINT, close_server)

# Dizionario usato per tenere traccia dei client connessi al server.
addresses = {}
# Lista usata per tenere traccia dei nomi scelti, in modo da evitare ripetizioni.
names = []

HOST = ''
PORT = 53000
BUFFSIZE = 1024
ADDR = (HOST, PORT)

# Crea la socket del server selezionando il protocollo TCP.
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connections...")
    ACCEPT_THREAD = Thread(target=accept_connections)
    ACCEPT_THREAD.start()
    wait_signal(1)
    ACCEPT_THREAD.join()
    print("Server succesfully closed.")
