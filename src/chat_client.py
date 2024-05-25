#!/usr/bin/env python3
"""Applicazione client che consente all'utente di scambiare messaggi
   nella chat di gruppo."""

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tkt
import time

"""Funzione che gestisce la ricezione dei messaggi.
   L'esecuzione può essere interrotta dalla ricezione del messaggio di chiusura connessione
   inviato dal server oppure dalla chiusura del socket da parte dell'applicazione."""
def receive():
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            # Se viene ricevuto il messaggio di fine connessione, chiude la socket ed esce dall'applicazione
            if msg == "{end_conn}":
                msg = SERVER_DISCONNECTED
                msg_list.insert(tkt.END, msg)
                msg = "La finestra si chiuderà tra 5 secondi."
                msg_list.insert(tkt.END, msg)
                time.sleep(5)
                close_app()
            # Aggiunge il messaggio ricevuto alla lista dei messaggi presenti a schermo.
            msg_list.insert(tkt.END, msg)
            # Se il client chiude il socket, uscendo dalla chat, viene generata un'eccezione
            # che provoca la chiusura di questo thread.
        except OSError:  
            break

"""Funzione responsabile della gestione dell'invio dei messaggi.
   Chiude l'applicazione se l'utente digita il messaggio {quit} """
def send(event=None):
    #Legge il messaggio dalla casella di inserimento e la libera.
    msg = my_msg.get()
    my_msg.set("")
    # Prova ad inviare il messaggio al server.
    # Se si verifica un errore di connessione, avvisa l'utente con un apposito messaggio d'errore.
    try:
        client_socket.send(bytes(msg, "utf8"))
    except OSError:
        msg_list.insert(tkt.END, SERVER_ERROR)
        msg_list.insert(tkt.END, RESTART_APPLICATION)
    if msg == "{quit}":
        close_app()

"""La funzione che segue viene invocata quando viene chiusa la finestra della chat."""
def on_closing(event=None):
    my_msg.set("{quit}")
    send()
    
"""Quando invocata, questa funzione chiude la socket ed esce dall'applicazione chiudendo la finestra."""
def close_app():
    client_socket.close()
    window.destroy()
    
# CONNESSIONE AL SERVER:

HOST = input('Inserire il Server host: ')
PORT = input('Inserire la porta del server host: ')
if not PORT:
    PORT = 53000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

# CREAZIONE GUI:
    
window = tkt.Tk()
window.title("Chat")

# Crea il Frame per contenere i messaggi
messages_frame = tkt.Frame(window)
# I messaggi dell'utente vengono inseriti in una variabile stringa.
my_msg = tkt.StringVar()
my_msg.set("Scrivi qui i tuoi messaggi.")
# Crea una scrollbar per navigare tra i messaggi precedenti.
scrollbar = tkt.Scrollbar(messages_frame)

# La parte seguente contiene i messaggi.
msg_list = tkt.Listbox(messages_frame, height=30, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
msg_list.pack()
messages_frame.pack()

# Crea il campo di input, associandolo alla variabile stringa che contiene il messaggio.
entry_field = tkt.Entry(window, textvariable=my_msg, width=50)
# Imposta il tasto Invio o Return come comando per l'invio dei messaggi.
entry_field.bind("<Return>", send)
entry_field.pack()

# Crea il tasto che consente l'invio di messaggi dalla GUI.
send_button = tkt.Button(window, text="Invio", command=send)
send_button.pack()

# Specifichiamo la procedura che dev'essere svolta alla chiusura della finestra.
window.protocol("WM_DELETE_WINDOW", on_closing)

# Messaggi di errore in caso di disconnessione del server.
SERVER_DISCONNECTED = "Il server si è disconnesso."
SERVER_ERROR = "ERRORE: Si è verificato un errore di connessione con il server."
RESTART_APPLICATION = "Riavviare l'applicazione per connetersi ad un altro server."

# AVVIO DELL'APPLICAZIONE:

# Avvia il thread di gestione della ricezione dei messaggi.
receive_thread = Thread(target=receive)
receive_thread.start()
# Avvia l'esecuzione della Finestra Chat.
tkt.mainloop()
