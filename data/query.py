from .models import Data
from datetime import date
from .wallet import Wallet
import json

class Query:
    '''Oggetto Query che interagisce attraverso l'oggetto Wallet per poter ottenere ed elaborare tutti i dati
    che sono stati salvati sulla blockchain'''

    def __init__(self):
        '''Istanzia l'oggetto Wallet necessario per poter interagire con la blockchian e un attributo necessario
        per accedere ai dati dell'ultima transazione svolta'''
        self._wallet = Wallet()
        # se non sono state salvate transazioni nel database allora imposto il puntatore a None in modo da sapere che
        # non sono state ancora memorizzate transazioni sulla blockchain
        data_objects = Data.objects.all()
        if data_objects:
            pointer = data_objects[0].get_hash_transaction()
        else:
            pointer = None
        # Considerando che utilizzo la blockchain come database, salvo un unica informazione necessaria per poter ottenere
        # tutti le informazioni da quest'ultima cioè un puntatore o l'hash dell'ultima transazione svolta. Grazie a esso
        # riesco a ottenere l'ultimo oggetto JSON che è stato salvato sulla blockchain che a sua volta contiene un puntatore
        # al precedente oggetto JSON salvato. Può essere visto come una pila
        self._pointer = pointer

    def save_data_on_blockchain(self, informations):
        '''Riceve in ingresso un oggetto JSON e lo salva sulla blockchain aggiornando il puntatore e ritorna
        l'hash della transazione'''
        data = {
            'pointer': self._pointer,
            'produced_energy': informations.get('produced_energy_in_watt'),
            'consumed_energy': informations.get('consumed_energy_in_watt'),
            'date': date.today().strftime('%d %B %Y')
        }
        hash_transaction = self._wallet.send_data(json.dumps(data))
        self._pointer = hash_transaction
        return hash_transaction

    def get_last_transaction(self):
        '''Ritorna un oggetto JSON relativo all'ultima transazione svolta sulla blockchain. Se non sono state ancora
        salvate transazioni ritorna False'''
        if self._pointer != None:
            response = json.loads(self._wallet.get_data(self._pointer))
        else:
            response = False
        return response

    def get_number_transactions(self):
        '''Ritorna il numero di tutte le transazioni svolte sulla blockchain'''
        return self._wallet.get_nonce()

    def get_all_data(self):
        '''Ritorna una lista contenente tutte le transazioni memorizzate sulla blockchain. È una lista contenente
        oggetti JSON'''
        continue_cycle = True
        all_data = []
        hash_transaction = self._pointer
        while continue_cycle:
            if self._pointer:
                data = json.loads(self._wallet.get_data(hash_transaction))
                data['transaction'] = hash_transaction
                all_data.append(data)
                if data.get('pointer') == None:
                    continue_cycle = False
                hash_transaction = data.get('pointer')
            else:
                continue_cycle = False
        return all_data

    def get_specific_data(self, *informations):
        '''Ritorna una lista di dizionari dove al loro interno ci sono tutte le informazioni salvate sulla blockchain
         ad eccezione di quelle passate come parametri'''
        all_data = self.get_all_data()
        essential_data = []
        for data in all_data:
            for information in informations:
                del data[information]
            essential_data.append(data)
        return essential_data

    def set_value_transaction(self, value):
        '''Funzione che imposta il costo per cui si è disposti a pagare per svolgere una transazione sulla blockchain'''
        self._wallet.set_value_transaction(value)

    def get_value_transaction(self):
        '''Funzione che ritorna il costo che si è disposti a pagare per svolgere una transazione sulla blockchain'''
        return self._wallet.get_value_transaction()

    def get_gas_transaction(self):
        '''Funzione che ritorna la quantità di gas necessaria per svolgere una transazione sulla blockchain'''
        return self._wallet.get_gas_transaction()

    def get_balance(self):
        '''Funzione che ritorna la quantità di ether che si ha a disposizione'''
        return self._wallet.get_balance()

    def get_gas_price(self):
        '''Funzione che ritorna il costo del gas'''
        return self._wallet.get_gas_price()

    def get_nonce(self):
        '''Funzione che ritorna il numero di transazioni svolte sulla blockchian'''
        return self._wallet.get_nonce()
