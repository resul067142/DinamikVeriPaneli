from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .views import log_user_activity

def user_register(request):
    """
    Kullanıcı kayıt sayfası
    """
    if request.user.is_authenticated:
        return redirect('veri_yonetimi:veri_listesi')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Hesabınız başarıyla oluşturuldu!')
            return redirect('veri_yonetimi:veri_listesi')
        else:
            messages.error(request, 'Kayıt sırasında hata oluştu. Lütfen kontrol edin.')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
        'is_register': True,
    }
    return render(request, 'veri_yonetimi/auth_form.html', context)

def user_login(request):
    """
    Kullanıcı giriş sayfası
    """
    if request.user.is_authenticated:
        return redirect('veri_yonetimi:veri_listesi')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Giriş logunu kaydet
                log_user_activity(
                    user=user,
                    islem_yapan=user,
                    islem_tipi='giris_yapildi',
                    aciklama=f'{user.username} kullanıcısı sisteme giriş yaptı',
                    request=request
                )
                
                messages.success(request, f'Hos geldiniz, {username}!')
                return redirect('veri_yonetimi:veri_listesi')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'is_register': False,
    }
    return render(request, 'veri_yonetimi/login.html', context)

@login_required
def user_logout(request):
    """
    Kullanıcı çıkış
    """
    # Çıkış logunu kaydet (logout'tan önce)
    log_user_activity(
        user=request.user,
        islem_yapan=request.user,
        islem_tipi='cikis_yapildi',
        aciklama=f'{request.user.username} kullanıcısı sistemden çıkış yaptı',
        request=request
    )
    
    logout(request)
    messages.info(request, 'Başarıyla çıkış yapıldı.')
    return redirect('veri_yonetimi:user_login')
