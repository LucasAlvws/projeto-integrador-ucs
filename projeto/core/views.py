from django.shortcuts import render, redirect
from django.contrib.auth import login
from projeto.core.forms import SignUpForm

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            login(request, user)
            return redirect('/admin/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


