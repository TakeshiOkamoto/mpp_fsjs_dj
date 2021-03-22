from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.views.generic import View

from .models import User

from module.common import trim


class LoginView(View):

    def dispatch(self, request, *args, **kwargs):
        
        if (request.method == 'POST'):
            email = trim(request.POST['email'])
            password = trim(request.POST['password'])

            # バリデーション
            users = User.objects.filter(email=email)
            if users.count() == 1:
                if check_password(password, users[0].password):
                    request.session['name']  = users[0].name 
                    request.session['email'] = users[0].email
                    messages.success(request, "ログインしました。")
                    return redirect('fsjs_main:index') 

            messages.error(request, \
                    "メールアドレスまたはパスワードが一致しません。")
            return redirect('fsjs_login:login')

        if (request.method == 'GET'):
            if 'name' in request.session:
                return redirect('fsjs_main:index') 
            return render(request, 'fsjs_login/index.html')
            
        return super().dispatch(request, *args, **kwargs)


class LoguotView(View):

    def dispatch(self, request, *args, **kwargs):
    
        if (request.method == 'GET'):
            if 'name' in request.session:
                del request.session['name']
            if 'email' in request.session:
                del request.session['email']
            return redirect('fsjs_login:login')
            
        return super().dispatch(request, *args, **kwargs)


