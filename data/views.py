from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Data
from .query import Query
import json
from datetime import date, datetime
from django.core.cache import cache


# Function
def __validate_data(data):
    '''Funzione che ritorna False nel caso i valori presenti nell'oggetto JSON sono diversi da numeri, l'oggetto JSON
    qualora i dati sono corretti.'''
    response = False
    # converto i dati da byte in stringa
    data = data.decode()
    # converto la stringa in formato JSON
    data = json.loads(data)
    # controllo se i dato sono corretti cioè i valori dell'oggetto JSON sono numeri
    if (str(type(data.get('produced_energy_in_watt'))) == "<class 'int'>" or str(type(data.get('produced_energy_in_watt'))) == "<class 'float'>") and (str(type(data.get('consumed_energy_in_watt'))) == "<class 'int'>" or str(type(data.get('consumed_energy_in_watt'))) == "<class 'float'>"):
        response = data
    return response


def __convert_format_str_date(str_date, format):
    '''Funzione che riceve in ingresso una data in formato stringa con il relativo formato e che ritorna una nuova data
    nel seguente formato (AAAAMMDD)'''
    object_date = date = datetime.strptime(str_date, format)
    date_formated = date.strftime('%Y%m%d')
    return date_formated


def set_value_transaction(value):
    '''Funzione che modifica il costo per salvare i dati sulla blockchain'''
    query.set_value_transaction(value)


# Create your views here.
def index(request):
    '''Funzione che direziona la richiesta di visualizzazione delle informazioni alla funzione che ritorna i dati in base
     al tipo di utente'''
    path = '/'
    # se l'utente non è registrato ritorna la pagina della home page altrimenti se l'utente è amministratore o utente normale
    # redireziona la richiesta alla funzione che ritorna i dati in base al tipo di utente
    if str(request.user) != 'AnonymousUser':
        # se amministratore
        if request.user.is_staff:
            path = '/data/admin'
        # se utente normale
        else:
            path = '/data/normal_user'
    return redirect(path)


@csrf_exempt
def manage_requests(request):
    response = ''
    # creo l'oggetto Query che mi permette di interagire con la blockchain in quanto i dati vengono salvati sulla blockchain
    # e non sul database
    query = Query()
    if request.method == 'GET':
        # ritorna tutti i dati memorizzati ad ecezzione del puntatore alla successiva transazione registrata
        response = {'data': query.get_specific_data('pointer')}
    elif request.method == 'POST':
        date_last_transaction = ''
        request_data = HttpRequest.read(request)
        # verifico che le informazioni siano sintatticamente corrette
        request_data = __validate_data(request_data)
        number_transactions = query.get_number_transactions()
        # memorizzo la data dell'ultima transazione salvata sulla blockchain in modo da sapere se l'utente ha già
        # registrato le informazioni giornaliere oppure no. Nel caso non le abbia ancora salvate fa partire una transazione
        if query.get_number_transactions() > 0:
            date_last_transaction = str(query.get_last_transaction().get('date'))
        # se i dati non sono validi
        if not request_data:
            response = {'Error': 'Values are not correctly'}
        elif date_last_transaction != date.today().strftime('%d %B %Y'):
            # creo oppure ottengo l'oggetto che memorizza l'hahs dell'ultima transazione svolta sulla blockchain;
            # non mi interessa salvare tutte le transazioni nel database in quanto salvo una coda di transazioni sulla
            # blockchain. Per tanto mi basta conoscere l'hash dell'ultima transazione per poter ottenere tutte le informazioni
            # di tutte le transazioni svolte
            if number_transactions > 0:
                data_database = Data.objects.all()[0]
            else:
                data_database = Data()
            hash_transaction = query.save_data_on_blockchain(request_data)
            # aggiorno il puntatore nel database cioè l'hash dell'ultima transazione memorizzata sulla blockchain
            data_database.set_hash_transaction(hash_transaction)
            response = {'hash transaction': hash_transaction}
        else:
            response = {'Error': 'Wait next day'}
    return JsonResponse(response, safe=False)


def get_admin_data(request):
    '''Funzione che ritorna i dati che devono essere visualizzati al utente amministratore. L'utente può visualizzare
     i dati di un determinato arco temporale esclusivamente se seleziona entrambe le date; verranno mostrati tutti i
     dati qualora selezioni solamente una o nessuna data'''
    if request.user.is_staff:
        # prelevo le ulteriori informazioni richieste dal amministratore
        start_date = request.GET.get('start_date')
        finish_date = request.GET.get('finish_date')
        # se l'utente ha selezionato entrambe le date allora le trasformo in intero per poter capire quali dati fare
        # visualizzare e quali no
        if start_date and finish_date:
            start_date = __convert_format_str_date(start_date, '%Y-%m-%d')
            finish_date = __convert_format_str_date(finish_date, '%Y-%m-%d')
        # prelevo tutte le informazioni salvate sulla blockchain ad eccezione del puntatore
        data = query.get_specific_data('pointer')
        # oltre alle informazioni memorizzate sulla blockchain calcolo una serie di ulteriori informazioni che devo esser
        # mostrate
        average_produced_energy = 0
        average_consumed_energy = 0
        total_produced_energy = 0
        total_consumed_energy = 0
        total_registration = 0
        data_filtered = data.copy()
        for day_transaction in data:
            if start_date and finish_date:
                date = day_transaction.get('date')
                date = __convert_format_str_date(date, '%d %B %Y')
                # se la data della transazione si trova all'interno della arco temporale richiesto
                if start_date <= date and date <= finish_date:
                    total_produced_energy += day_transaction.get('produced_energy')
                    total_consumed_energy += day_transaction.get('consumed_energy')
                    total_registration += 1
                else:
                    # altrimenti cancello il dato perchè non deve essere mostrato all'utente
                    data_filtered.remove(day_transaction)
            else:
                total_produced_energy += day_transaction.get('produced_energy')
                total_consumed_energy += day_transaction.get('consumed_energy')
                total_registration += 1
        # nel caso l'utente ha selezionato un arco temporale nel quale non sono state registrate transazioni allora
        # gestisco l'errore della divisione per zero
        try:
            average_produced_energy = total_produced_energy/total_registration
            average_consumed_energy = total_consumed_energy/total_registration
        except ZeroDivisionError:
            pass
        return render(request, 'admin_data.html', {'data': data_filtered,
                                                   'total_produced_energy': total_produced_energy,
                                                   'total_consumed_energy': total_consumed_energy,
                                                   'total_registration': total_registration,
                                                   'average_produced_energy': average_produced_energy,
                                                   'average_consumed_energy': average_consumed_energy})
    else:
        return redirect('/')


def get_normal_user_data(request):
    ''''Funzione che ritorna i dati che devono essere visualizzati da un utente non amministratore'''
    if str(request.user) != 'AnonymousUser':
        # prelevo tutte le informazioni salvate sulla blockchain ad eccezione del puntatore
        data = query.get_specific_data('pointer')
        return render(request, 'user_data.html', {'data': data})
    else:
        return redirect('/')


def get_blockchain_data(request):
    '''Funzione che ritorna i dati relativi alla blockchain e al proprio wallet'''
    if request.user.is_staff:
        informations = {
            'value': query.get_value_transaction(),
            'gas_transaction': query.get_gas_transaction(),
            'gas_price': query.get_gas_price(),
            'balance': query.get_balance(),
            'number_transaction': query.get_nonce()
        }
        return render(request, 'blockchain_data.html', informations)
    else:
        return redirect('/')


# oggetto globale utilizzato in tutte le funzioni
query = Query()
