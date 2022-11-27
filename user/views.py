from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import authenticate
from .models import User
from django.core.mail import send_mail
from django.contrib import messages
from .forms import LoginUserForm, DataUserForm, AccountForm
from data.views import set_value_transaction
from django.core.cache import cache

# Create your views here.
def home_page(request):
    '''Funzione che ritorna la pagina della home page all'utente'''
    # da alla pagina alcune informazioni necessarie per visualizzare i dati in base se l'utente è loggato o meno
    return render(request, 'home_page.html')


def login_page(request):
    '''Funzione che permette di autenticare un utente e di rinderizzarlo alla home page'''
    if request.method == 'POST':
        # creo l'oggetto form per ottenere le informazioni
        form = LoginUserForm(request, data=request.POST)
        # se l'autenticazione è andata a buon fine cioè l'utente è registrato
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            # salvo o incremento il numero di accessi effettuati dall'utente su redis
            if cache.get(str(user)):
                number_access = cache.get(str(user))
                cache.set(str(user), number_access+1)
            else:
                cache.set(str(user), 1)
            # memorizzo l'indirizzo IP dell'utente
            ip = request.META['REMOTE_ADDR']
            # se è amministratore
            if user.is_staff:
                # verifico che l'ultimo utente che si è autenticato non sia l'attuale utente, nel caso siano due utenti
                # diversi mostro un messaggio dell'ultimo utente amministratore che si è autenticato. Ipotizzo che un
                # utente amministratore non abbia un univoco indirizzo IP in quanto può accedere da più reti.
                last_admin_user = User.objects.all().filter(is_staff=True).order_by('-login_date')[0]
                if user.get_username() != last_admin_user.get_username():
                    messages.add_message(request, messages.INFO, f'The last access have was by {last_admin_user.get_username()} '
                                                                 f'with IP address: {last_admin_user.get_ip_address()}!')
            user.set_ip_address(ip)
            return redirect('/')
        else:
            # controllo il motivo perchè l'autenticazione non è andata a buon fine
            username = form.cleaned_data.get('username')
            user = User.objects.filter(username=username)
            if user:
                msg = "Password isn't correct."
            else:
                msg = "User doesn't exist. Check the insert data or create new user."
            messages.add_message(request, messages.ERROR, msg)
    # nel caso l'utente deve autenticarsi invio un form con in campi necessari
    form = LoginUserForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    '''Funzione che permette di creare un nuovo utente non amministratore, loggarlo e reinderizzarlo alla home page'''
    form = DataUserForm(request.POST or None)
    # se l'utente ha inserito i dati necessari a creare un nuovo utente
    if request.method == 'POST':
        if form.is_valid():
            # una volta che ho memorizzato il nuovo utente invio un email per informarlo che la registrazione è completata
            name = form.cleaned_data.get('first_name').capitalize()
            last_name = form.cleaned_data.get('last_name').capitalize()
            user = form.save()
            if name and last_name:
                name = f'{name} {last_name}'
            else:
                name = user.get_username().capitalize()
            user.set_ip_address(request.META['REMOTE_ADDR'])
            send_mail('Welcome to Pomelia hotel', f'{name} your authentication was success.', 'noreply@hotelPomelia.com',
                      ['maxfachin98@gmail.com'])
            messages.add_message(request, messages.SUCCESS, 'The account was created successfully')
            login(request, user)
            # salvo l'accesso svolto dall'utente su redis
            cache.set(str(user), 1)
            return redirect('/')
    # nel caso l'utente vuole registrarsi sul sito invio un form per poter essere compilato
    return render(request, 'register.html', {'form': form})


def logout_page(request):
    '''Funzione che chiude la sessione di login e reinderizza alla home page'''
    logout(request)
    return redirect('/')

def account(request):
    '''Funzione che permette all'utente di modificare i suoi dati'''
    # se l'utente ha inviato i le informazioni che devono essere cambiate allora capisco quali son dati che devono
    # essere modificati (modifico solamente i dati nei quali l'utente ha inserito le informazioni, nel caso ha
    # lasciato dei campi vuoti allora quelli li considero che non devono essere modificati
    if request.method == 'POST':
        form = AccountForm(request.POST)
        user = request.user
        # variabile dove memorizzo il messaggio da mostrare all'utente
        msg = ''
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if user.is_staff:
                value = request.POST.get('value_transaction')
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if email:
                user.email = email
            if password1 and password2:
                user.set_password(password1)
            elif not password1 and password2 or password1 and not password2:
                msg = 'For update your password you have to insert both passwords!'
            if user.is_staff:
                set_value_transaction(value)
            if user.is_staff:
                if not first_name and not last_name and not email and not password1 and not password2 and not value:
                    msg = 'For update your data you have to fill the fields!'
            else:
                if not first_name and not last_name and not email and not password1 and not password2:
                    msg = 'For update your data you have to fill the fields!'
            user.save()
            if msg:
                if msg == 'For update your data you have to fill the fields!':
                    messages.add_message(request, messages.INFO, msg)
                else:
                    messages.add_message(request, messages.ERROR, msg)
            else:
                messages.add_message(request, messages.SUCCESS,'Your account was update.')
    # nel caso l'utente voglia modificare i dati allora invio il form nel quale potrà indicare i dati con le relative
    # informazioni che devono essere modificate
    return render(request, 'account.html', {'form': AccountForm(), 'access': cache.get(str(request.user))})


def remove_account(request):
    '''Funzione che elimina un account'''
    request.user.delete()
    logout(request)
    messages.add_message(request, messages.SUCCESS, 'Your account was delete')
    return render(request, 'home_page.html')
