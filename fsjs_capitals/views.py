from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView
from django.views.generic import UpdateView, View
from django.http import HttpResponse

from .models import Capital

from module.common import trim
from module.fsjs.common import LoginRequiredMixin


class CapitalListView(LoginRequiredMixin, ListView):

    model = Capital
    context_object_name = 'items'
    template_name = 'fsjs_capitals/index.html'
    
    # 初期処理
    def dispatch(self, request, *args, **kwargs):
        
        # ページネーション
        if 'page' in self.request.GET: 
            if self.request.GET['page'].isdecimal():
                self.current_page = int(self.request.GET['page'])
            else:
                return redirect('fsjs_capitals:index')
        else:
            self.current_page = 1
        
        return super().dispatch(request, *args, **kwargs)

    # QuerySet
    def get_queryset(self):
        
        # メイン
        items = Capital.objects.order_by('yyyy').reverse()
        for item in items:
            item.m1 = "{:,}".format(item.m1)
            item.m2 = "{:,}".format(item.m2)
            item.m3 = "{:,}".format(item.m3)
            item.m4 = "{:,}".format(item.m4)
            
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
        context['message'] = self.message
        return context


class CapitalCreateView(LoginRequiredMixin, CreateView):

    model = Capital
    fields = ['yyyy', 'm1', 'm2', 'm3', 'm4']
    template_name = 'fsjs_capitals/create.html'
    
    # バリデーションの成功
    def form_valid(self, form):
        try:
            with transaction.atomic(): 
                form.save()
                messages.success(self.request, "登録しました。")
        except Exception as e:
            messages.error(self.request, \
                "エラーが発生しました。管理者に問い合わせてください。")

        return redirect(to='fsjs_capitals:index')
        
    # バリデーションの失敗
    def form_invalid(self, form):
        messages.error(self.request, "エラーをご確認ください。")
        return super().form_invalid(form)


class CapitalUpdateView(LoginRequiredMixin, UpdateView):

    model = Capital
    fields = ['yyyy', 'm1', 'm2', 'm3', 'm4']
    template_name = 'fsjs_capitals/edit.html'
    
    # バリデーションの成功
    def form_valid(self, form):
        try:
            with transaction.atomic(): 
                form.save()
                messages.success(self.request, "更新しました。")
        except Exception as e:
            messages.error(self.request, \
                "エラーが発生しました。管理者に問い合わせてください。")

        return redirect(to='fsjs_capitals:index')
        
    # バリデーションの失敗
    def form_invalid(self, form):
        messages.error(self.request, "エラーをご確認ください。")
        return super().form_invalid(form)


class CapitalDeleteView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if (request.method == 'DELETE'):
            try:
                capital = Capital.objects.get(id=kwargs['pk'])
                with transaction.atomic(): 
                    capital.delete()
                    
                    # --------------------------------------------------
                    #  必要であれば、該当年度の仕訳帳も削除して下さい。
                    # --------------------------------------------------
                    
                    messages.error(request, "削除しました。")
                return HttpResponse('')
            except Exception as e:
                messages.error(request, \
                    "エラーが発生しました。管理者に問い合わせてください。")
        return super().dispatch(request, *args, **kwargs)


