# myauth/views.py

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, ProfileUpdateForm
from .models import Profile


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about_me')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        Profile.objects.get_or_create(user=user)
        login(self.request, user)
        return redirect(self.success_url)


class AboutMeView(LoginRequiredMixin, UpdateView):
    """Страница текущего пользователя с возможностью сменить аватар"""
    model = Profile
    fields = ('avatar',)
    template_name = 'myauth/about_me.html'
    success_url = reverse_lazy('myauth:about_me')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О пользователе'
        context['profile'] = self.request.user.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Обновление профиля (только staff или владелец)"""
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'myauth/profile_update.html'

    def test_func(self):
        profile = self.get_object()
        user = self.request.user
        return user.is_staff or profile.user == user

    def get_success_url(self):
        return reverse('myauth:user_detail', kwargs={'pk': self.object.user.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление профиля: {self.object.user.username}'
        return context


class UserListView(ListView):
    """Список всех пользователей"""
    model = User
    template_name = 'myauth/user_list.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Пользователи'
        return context


class UserDetailView(TemplateView):
    """Детали пользователя"""
    template_name = 'myauth/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        context['title'] = f'Пользователь: {user.username}'
        context['profile_user'] = user
        context['profile'] = user.profile
        context['can_edit'] = (
            self.request.user.is_staff or
            self.request.user == user
        )
        return context


# Cookies и сессии
def set_cookie_view(request):
    response = render(request, 'myauth/cookie_set.html', {
        'title': 'Установка cookie',
        'message': 'Cookie установлена!',
    })
    response.set_cookie('username', request.user.username, max_age=3600)
    response.set_cookie('favorite_color', 'blue', max_age=86400)
    return response


def get_cookie_view(request):
    username = request.COOKIES.get('username', 'Значение не установлено')
    favorite_color = request.COOKIES.get('favorite_color', 'Значение не установлено')
    return render(request, 'myauth/cookie_get.html', {
        'title': 'Чтение cookie',
        'username': username,
        'favorite_color': favorite_color,
    })


def set_session_view(request):
    request.session['user_prefs'] = {'theme': 'dark', 'language': 'ru'}
    request.session['last_visit'] = datetime.now().strftime('%d.%m.%Y %H:%M')
    return render(request, 'myauth/session_set.html', {
        'title': 'Установка сессии',
        'message': 'Данные в сессию сохранены!',
    })


def get_session_view(request):
    user_prefs = request.session.get('user_prefs', 'Значение не установлено')
    last_visit = request.session.get('last_visit', 'Значение не установлено')
    return render(request, 'myauth/session_get.html', {
        'title': 'Чтение сессии',
        'user_prefs': user_prefs,
        'last_visit': last_visit,
    })