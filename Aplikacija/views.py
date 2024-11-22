#* Marko Dasic 2022/0731
#* Pavle Kotlajic
#* Vladana Babic 2021/0546

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
from .forms import *

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

from datetime import datetime

User = get_user_model()

# Create your views here.


####################################### Marko ###########################################################################################

# Home page
def homePage(request):
    return render(request, 'home.html')


# Register
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('main')

    form = MyUserCreationForm()
    hobbies = Hobby.objects.all()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)      # So we can save some aditional settings
            user.username = user.username.lower()
            user.save()
            user.iduser = str(user.id)
            user.save()
            user.hobbies.set(form.cleaned_data['hobbies'])
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, 'There was an error with registration')

    return render(request, 'register.html', {'form': form})


# Login
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('main')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_admin:
                return redirect('profile_admin')
            else:
                return redirect('main')
        else:
            messages.error(request, 'Username or password is incorrect')
        
    context = {}
    return render(request, 'login.html', context)


# Logout
def logoutPage(request):
    logout(request)
    return redirect('home')


# User Profile
@login_required(login_url='login')
def profile_userPage(request, pk):
    user = User.objects.get(id=pk)
    context = {'user': user}
    return render(request, 'profile_user.html', context)


# Update user data
@login_required(login_url='login')
def update_userPage(request):
    user = request.user
    form = UpdateUserForm(instance=user)

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'update_user.html', {'form': form})


# Rating
@login_required(login_url='login')
def add_rating(request, user_id):
    rated_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            if request.user != rated_user:      # Check if logged-in user is not the same as the rated user
                rating.user = rated_user
                rating.save()
                return redirect('profile_userPage', pk=rated_user.id)
            else:
                messages.error(request, "You cannot rate yourself.")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = RatingForm()
    return render(request, 'add_rating.html', {'form': form, 'user': rated_user})



####################################### Pavle ###########################################################################################
def getreports(request):
    reports = Report.objects.all()
    return render(request, 'profile_admin.html', {'reports': reports})

    
# Admin profile
@login_required(login_url='login')
def profile_adminPage(request):

    reports = Report.objects.all()
    return render(request, 'profile_admin.html', {'reports': reports})



# Admin ban
@login_required(login_url='login')
def admin_banPage(request):
    return render(request, 'admin_ban.html')

 #Pavle Kotlajic 2021/0596 
def ban_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        if 'banovanje' in request.POST:
            user.is_suspended = True
            user.suspended_time = (timezone.now() + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S')
            user.save()
            
            # Kreiranje nove suspenzije
            Suspension.objects.create(

                idsus=str(uuid.uuid4())[:30],
                date=timezone.now().strftime('%Y-%m-%d'),
                time=timezone.now().strftime('%H:%M:%S'),
                idadmin=request.user,  # Pretpostavka da je korisnik koji banuje ulogovan
                iduser=user
            )

            return redirect('home')  # Zamijenite sa stvarnim URL imenom vaše početne strane

    return render(request, 'ban_user_template.html', {'korisnik': user})

#Pavle Kotlajic 2021/0596 
def delete_user(request, user_id):
    # Dobijanje korisnika iz baze podataka
    user = get_object_or_404(User, pk=user_id)

    # Provera dozvola (ovo je samo primer, prilagodite vašim potrebama)
    if not request.user.is_superuser:
        messages.error(request, "Nemate dozvolu za brisanje ovog korisnika.")
        return redirect('home')
    
    try:
        # Brisanje povezanih izveštaja
        Report.objects.filter(iduser1=user).delete()
        Report.objects.filter(iduser2=user).delete()

        # Brisanje povezanih poruka
        Message.objects.filter(iduser1=user).delete()
        Message.objects.filter(iduser2=user).delete()

        # Brisanje povezanih uplata
        Payment.objects.filter(iduser=user).delete()

        # Brisanje povezanih suspenzija
        Suspension.objects.filter(idadmin=user).delete()
        Suspension.objects.filter(iduser=user).delete()

        # Brisanje zapisa iz tabele Chats
        Chats.objects.filter(iduser=user).delete()

        # Brisanje korisnika iz baze
        user.delete()
        
        # Slanje poruke o uspešnom brisanju
        messages.success(request, "Korisnik je uspešno obrisan.")
    
    except IntegrityError as e:
        # Obrada greške integriteta
        messages.error(request, f"Greška prilikom brisanja korisnika: {str(e)}")
        return redirect('home')
    
    # Preusmeravanje na odgovarajuću stranicu nakon brisanja korisnika
    return redirect('home')


   


####################################### Vladana ###########################################################################################

# Main page
@login_required(login_url='login')
def mainPage(request):
    # current_user_gender = request.user.gender
    # Assuming True = Male, False = Female
    # opposite_gender = not current_user_gender
    # users = User.objects.exclude(id=request.user.id).filter(gender=opposite_gender).filter(is_superuser=0)
    # return render(request, 'main.html', {'users': users})
    # zakomentarisano - sig radi

    current_user = request.user
    current_user_gender = current_user.gender
    opposite_gender = not current_user_gender
    
    # Get the hobbies of the current user
    current_user_hobbies = current_user.hobbies.all()

    # Get all users of the opposite gender who are not superusers
    users = User.objects.exclude(id=current_user.id).filter(gender=opposite_gender, is_superuser=0)
    
    # Create feature vectors for users based on their hobbies
    user_feature_vectors = []
    for user in users:
        user_hobbies = user.hobbies.all()
        user_feature_vector = [1 if hobby in user_hobbies else 0 for hobby in current_user_hobbies]
        user_feature_vectors.append(user_feature_vector)

    # Convert current_user_hobbies to a list of hobby ids for use in the distance metric
    current_user_hobby_ids = list(current_user_hobbies.values_list('idhobby', flat=True))

    # Initialize KNN model with appropriate parameters (e.g., k value and distance metric)
    knn_model = NearestNeighbors(n_neighbors=5, metric='jaccard')
    knn_model.fit(user_feature_vectors)

    label_encoder = LabelEncoder()
    current_user_hobby_labels = label_encoder.fit_transform(current_user_hobby_ids)

    # Find the k nearest neighbors for the current user
    _, neighbor_indices = knn_model.kneighbors([current_user_hobby_labels])

    neighbor_indices_list = neighbor_indices[0].tolist()

    # Sort users based on their similarity to the current user
    sorted_users = [users[index] for index in neighbor_indices_list]

    return render(request, 'main.html', {'users': sorted_users})


####################################### Nina ###########################################################################################

# Chats page
@login_required(login_url='login')
def chatsPage(request):
    return render(request, 'chats.html')




####################################### Vladana ###########################################################################################

# Payment page
@login_required
def paymentPage(request):
    return render(request, 'payment.html')

@login_required
def update_premium_flag(request):
    if request.method == 'POST':
        # Update the is_premium flag for the current user
        request.user.is_premium = True
        request.user.save()
        return JsonResponse({'message': 'is_premium flag updated successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
# Nigde se ne prikazuje korisniku poruka Payment successful!, ako to neko sredi pre mene, samo obrisite ovaj komentar


# Delete page - zar ovo nije Pavle uradio?
@login_required(login_url='login')
def deletePage(request):
    return render(request, 'delete.html')


# Edit user profile
@login_required(login_url='login')
def edit_profilePage(request):
    return render(request, 'edit_profile.html')

# Report page
# Ako nekome bude trebalo: iduser1 je id usera koji submituje report, iduser2 je id usera koji je reportovan
# ova metoda samo dodaje u tabelu Report u bazi, admin mora da suspenduje korisnika, bazirano na prijavama
@login_required(login_url='login')
def reportPage(request, pk):
    if request.method == 'POST':
        # current time and date, converted to string, da li bi bilo bolje da u bazi ovo ne cuvamo kao varchar, nego date and time?:
        current_date = datetime.now().strftime('%Y-%m-%d')  # Format as 'YYYY-MM-DD'
        current_time = datetime.now().strftime('%H:%M:%S')  # Format as 'HH:MM:SS'
        report = Report.objects.create(
            iduser1=request.user,  # Reporting user
            iduser2=User.objects.get(id=pk),  # User being reported
            date = current_date,
            time = current_time
        )
        return redirect('home')  # Redirect to home page after reporting
    else:
        # Handle GET requests as needed ?
        pass

    return render(request, 'report.html')


# Chat (1 chat)
@login_required(login_url='login')
def chatPage(request, pk):
    user = User.objects.get(id=pk)
    context = {'user': user}
    return render(request, 'chat.html', context)


# Invite
@login_required(login_url='login')
def invitePage(request):
    return render(request, 'invite.html')

