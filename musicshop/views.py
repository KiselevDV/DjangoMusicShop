from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View, DetailView

from .forms import LoginForm, RegistrationsForm
from .models import Artist, Album, Customer


class LoginView(View):
    """Вход на сайт"""

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'musicshop/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'musicshop/login.html', context)


class RegistrationView(View):
    """Регистрация нового пользователя"""

    def get(self, request, *args, **kwargs):
        form = RegistrationsForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'musicshop/registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationsForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()

            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            login(request, user)
            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'musicshop/registration.html', context)


class BaseView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'musicshop/base.html', {})


class ArtistDetailView(DetailView):
    model = Artist
    template_name = 'musicshop/artist/artist_detail.html'
    slug_url_kwarg = 'artist_slug'
    context_object_name = 'artist'


class AlbumDetailView(DetailView):
    model = Album
    template_name = 'musicshop/album/album_detail.html'
    slug_url_kwarg = 'album_slug'
    context_object_name = 'album'
