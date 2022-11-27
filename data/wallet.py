from web3 import Web3

class Wallet:
    '''Oggetto Wallet che memorizza l'url per connettersi alla blockchain, la chiave pubblica,
    la chiave privata e l'indirizzo dove inviare la transazione'''
    _URL_GANACHE = 'http://127.0.0.1:7545'
    _SENDER_ADDRESS = '0x69daffE87e0fDc91718B7D213eD0a299eE07614e'
    _RECEIVER_ADDRESS = '0x65F41f60969c1375d67541cB587242CA56f3A322'
    _PRIVATE_KEY = 'fbddea1f4de6b0768d7638d6647971ae04d4cb4bf841a2f2eb7eb77f99103fce'

    def __init__(self):
        '''Quando istanzio l'oggetto Wallet instauro la connessione con la blockchain'''
        self.connection = Web3(Web3.HTTPProvider(Wallet._URL_GANACHE))
        self.gas = 4712400
        self.value = 1

    def send_data(self, data):
        '''Riceve i dati in formato JSON e ritorno l'hash della transazione convertito in esadecimale'''
        transaction = {
            'from': Wallet._SENDER_ADDRESS,
            'to': Wallet._RECEIVER_ADDRESS,
            'nonce': self.connection.eth.get_transaction_count(Wallet._SENDER_ADDRESS),
            'value': self.value,
            'gas': self.gas,
            'gasPrice': self.connection.eth.gas_price,
            'data': data.encode()
        }
        signed_transaction = self.connection.eth.account.sign_transaction(transaction, Wallet._PRIVATE_KEY)
        hash_transaction = self.connection.eth.send_raw_transaction(signed_transaction.rawTransaction)
        return self.connection.toHex(hash_transaction)

    def get_data(self, transaction):
        '''Riceve in ingresso l'hash di una transazoine in formato esadecimale e ritorno un oggetto JSON contenente i dati
        da elaborare'''
        informations = self.connection.eth.get_transaction(transaction)
        data = informations.get('input')
        return self.connection.toText(data)

    def get_nonce(self):
        '''Funzione che ritorna il numero di transazioni svolte sulla blockchian'''
        return self.connection.eth.get_transaction_count(Wallet._SENDER_ADDRESS)

    def get_gas_price(self):
        '''Funzione che ritorna il costo del gas'''
        return f'{self.connection.eth.gas_price} ether'

    def get_balance(self):
        '''Funzione che ritorna la quantità di ether che si ha a disposizione'''
        wei_balance = self.connection.eth.get_balance(Wallet._SENDER_ADDRESS)
        ether_balance = self.connection.fromWei(wei_balance, 'ether')
        return f'{ether_balance} ether'

    def get_gas_transaction(self):
        '''Funzione che ritorna la quantità di gas necessaria per svolgere una transazione sulla blockchain'''
        return self.gas

    def get_value_transaction(self):
        '''Funzione che ritorna il costo che si è disposti a pagare per svolgere una transazione sulla blockchain'''
        return self.value

    def set_value_transaction(self, value):
        '''Funzione che imposta il costo per cui si è disposti a pagare per svolgere una transazione sulla blockchain'''
        self.value = value


if __name__ == '__main__':
    pass
