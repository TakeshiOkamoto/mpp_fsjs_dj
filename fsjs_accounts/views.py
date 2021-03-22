from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic import UpdateView, View
from django.utils.http import urlencode
from django.core.paginator import Paginator
from django.http import HttpResponse

from .forms import FindForm
from .models import Account

from module.common import trim
from module.fsjs.common import LoginRequiredMixin


# コンボボックス用
combo_types = [
    {'id' : 1, 'name' : '借方'},
    {'id' : 2, 'name' : '貸方'},
    {'id' : 3, 'name' : '借方 + 貸方'},
]

# idから名称を取得する
def get_type_name(id):
    for item in combo_types:
        if item['id'] == id:
            return item['name']
    return '無効'


class AccountListView(LoginRequiredMixin, ListView):

    # モデル
    model = Account
    
    # テンプレート用のオブジェクト名
    # ※デフォルトはobject_list 
    context_object_name = 'items'

    # テンプレート名
    template_name = 'fsjs_accounts/index.html'
    
    # 初期処理
    def dispatch(self, request, *args, **kwargs):
        
        # ページネーション
        if 'page' in self.request.GET: 
            if self.request.GET['page'].isdecimal():
                self.current_page = int(self.request.GET['page'])
            else:
                return redirect('fsjs_accounts:index')
        else:
            self.current_page = 1
        
        return super().dispatch(request, *args, **kwargs)
        
    # QuerySet
    def get_queryset(self):
    
        # 検索
        items = Account.objects.all()
        if 'name' in self.request.GET:
        
            # フォームの生成
            name = trim(self.request.GET['name'])
            data = {
                'name' : name,
            }    
            self.form = FindForm(data)

            # 複数キーワード
            if name != '':
                arr = name.split(' ')
                for val in arr:
                    if val != '':
                        items = items.filter(name__icontains=val)
            
            # 検索用
            self.search_param = '&' + urlencode({'name': name})
        else:
            self.form = FindForm() 
            self.search_param = ''
        items = items.order_by('sort_list')
        
        # 種類名を取得する
        for item in items:
            item.types = get_type_name(item.types)
            
        # ページネーション
        per_page = 25 # ページ毎に表示するアイテム数
        paginator = Paginator(items, per_page)
        items = paginator.get_page(self.current_page)
        if items.paginator.count > 0:
            self.message = '全%s件中 %s - %s件' \
                    '<span class="pc">のデータ</span>が表示されています。' % \
               ( items.paginator.count, \
                  ( self.current_page -1) * per_page + 1, \
                  ((self.current_page -1) * per_page + 1)  + \
                   (len(items) -1) \
               )
        else:
            self.message = 'データがありません。'

        return items
    
    # テンプレート用のオブジェクトの設定
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['search_param'] = self.search_param
        context['message'] = self.message
        return context


class AccountCreateView(LoginRequiredMixin, CreateView):

    model = Account
    fields = ['name', 'types', 'expense_flg', 'sort_list', 'sort_expense']
    template_name = 'fsjs_accounts/create.html'
    
    # テンプレート用のオブジェクトの設定
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combo_types'] = combo_types
        return context
            
    # バリデーションの成功
    def form_valid(self, form):
        try:
            with transaction.atomic(): 
                form.save()
                messages.success(self.request, "登録しました。")
        except Exception as e:
            messages.error(self.request, \
                "エラーが発生しました。管理者に問い合わせてください。")

        return redirect(to='fsjs_accounts:index')
        
    # バリデーションの失敗
    def form_invalid(self, form):
        messages.error(self.request, "エラーをご確認ください。")
        return super().form_invalid(form)


class AccountDetailView(LoginRequiredMixin, DetailView):

    model = Account
    context_object_name = 'item'
    template_name = 'fsjs_accounts/show.html'

    # テンプレート用のオブジェクトの設定
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'].types = get_type_name(context['item'].types)
        return context


class AccountUpdateView(LoginRequiredMixin, UpdateView):

    model = Account
    fields = ['name', 'types', 'expense_flg', 'sort_list', 'sort_expense']
    template_name = 'fsjs_accounts/edit.html'
    
    # テンプレート用のオブジェクトの設定
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combo_types'] = combo_types
        return context
            
    # バリデーションの成功
    def form_valid(self, form):
        try:
            with transaction.atomic(): 
                form.save()               
                messages.success(self.request, "更新しました。")
                
        except Exception as e:
            messages.error(self.request, \
                "1エラーが発生しました。管理者に問い合わせてください。")

        return redirect(to='fsjs_accounts:index')
        
    # バリデーションの失敗
    def form_invalid(self, form):
        messages.error(self.request, "エラーをご確認ください。")
        return super().form_invalid(form)


class AccountDeleteView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):

        if (request.method == 'DELETE'):
            try:
                account = Account.objects.get(id=kwargs['pk'])
                with transaction.atomic(): 
                    account.delete()
                    messages.error(request, "削除しました。")
                return HttpResponse('')
            except Exception as e:
                messages.error(request, \
                    "エラーが発生しました。管理者に問い合わせてください。")
        return super().dispatch(request, *args, **kwargs)


