from datetime import datetime

from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic import UpdateView, View
from django.utils.http import urlencode
from django.core.paginator import Paginator
from django.http import HttpResponse

from .models import Journal
from fsjs_capitals.models import Capital
from fsjs_accounts.models import Account

from module.common import url
from module.fsjs.common import getAccountTotal
from module.fsjs.common import LoginRequiredMixin


#-----------------------------------------------------------------------------
# 内部関数
#-----------------------------------------------------------------------------

# 借方のリストを取得する 
def getDebitList(keihi):

    debits = Account.objects.exclude(types=2).order_by('sort_list')
    for debit in debits:
        if debit.expense_flg == True and keihi == True:
            debit.name = '[経費]' +  debit.name
    return debits
    
# 貸方のリストを取得する 
def getCreditList():

    return Account.objects.exclude(types=1).order_by('sort_list')

# 借方/貸方の名前を設定する
def setAccountName(item, debit_list, credit_list):
    
    # 借方
    item.debit = '不明'
    for debit in debit_list:
        if debit.id == item.debit_account_id:
            item.debit = debit.name
    
    # 貸方 
    item.credit = '不明'
    for credit in credit_list:
        if credit.id == item.credit_account_id:
            item.credit = credit.name


#-----------------------------------------------------------------------------
# バリデーション
#-----------------------------------------------------------------------------

# 対象科目の合計金額を取得する
def getTargetTotal(i, obj, target_id, edit_id):

    if not (i.credit_account_id == target_id or  \
            i.debit_account_id  == target_id):
        return 0
    
    # 元入金
    capital = Capital.objects.filter(yyyy=i.yyyy)

    # 編集
    if edit_id !=  '':
        # 借方
        sql = (
               'SELECT 0 AS id, IFNULL(SUM(money),0) AS money '
               'FROM fsjs_journals '
               'WHERE yyyy = %s AND debit_account_id = %s AND id <> %s'
              )
        debit = Journal.objects.raw(sql, [i.yyyy, target_id, edit_id])

        # 貸方
        sql = (
               'SELECT 0 AS id, IFNULL(SUM(money),0) AS money '
               'FROM fsjs_journals '
               'WHERE yyyy = %s AND credit_account_id = %s AND id <> %s'
              )
        credit = Journal.objects.raw(sql, [i.yyyy, target_id, edit_id])
    # 新規
    else:
        # 借方
        sql = (
               'SELECT 0 AS id, IFNULL(SUM(money),0) AS money '
               'FROM fsjs_journals '
               'WHERE yyyy = %s AND debit_account_id = %s'
              )
        debit = Journal.objects.raw(sql, [i.yyyy, target_id])
        
        # 貸方
        sql = (
               'SELECT 0 AS id, IFNULL(SUM(money),0) AS money '
               'FROM fsjs_journals '
               'WHERE yyyy = %s AND credit_account_id = %s'
              )
        credit = Journal.objects.raw(sql, [i.yyyy, target_id])
    
    # 未払金
    if target_id == 5:
        # 借方
        if i.debit_account_id == target_id:
            total = (debit[0].money + i.money) - \
                    (getattr(capital[0], obj) + credit[0].money)
        # 貸方  
        else:
            total = (debit[0].money) - \
                    (getattr(capital[0], obj) + credit[0].money + i.money)
    # 現金、その他の預金、前払金 
    else:
        # 借方
        if (i.debit_account_id == target_id):
            total = (getattr(capital[0], obj) + debit[0].money + i.money) - \
                     credit[0].money
        else:
            total = (getattr(capital[0], obj) + debit[0].money) - \
                     credit[0].money - i.money
    return  total

# 現金、その他の預金、前払金、未払金の整合性チェック
def money_check(instance, id):

    # 仕訳帳は1/1から順番に記帳しないと矛盾が生じてエラーが多発しやすいです。
    # エラーチェックを解除したい場合は次のコードを有効にして下さい。
    
    # return ''
    
    # 現金
    total = getTargetTotal(instance, 'm1', 3, id)
    if total < 0:
        return (
                "現金の合計が%s円になります。"
                "この仕訳の前に「借方」に現金を追加して下さい。 "
                "例)借方(現金) 貸方(事業主借)"
                % "{:,}".format(total)
               )

    # その他の預金
    total = getTargetTotal(instance, 'm2', 4, id)
    if total < 0:
        return (
                "その他の預金の合計が%s円になります。"
                "※他の仕訳の「その他の預金」を確認して下さい。 "
                % "{:,}".format(total)
               )

    # 前払金
    total = getTargetTotal(instance, 'm3', 13, id)
    if total < 0:
        return (
                "前払金の合計が%s円になります。"
                "※他の仕訳の「前払金」を確認して下さい。 "
                % "{:,}".format(total)
               )

    # 未払金
    total = getTargetTotal(instance, 'm4', 5, id)
    if total > 0:
        return (
                "このままだと未払金を支払い過ぎます。(%s円多い) "
                "※他の仕訳の「未払金」を確認して下さい。 "
                % "{:,}".format(total)
               )
    return ''

#-----------------------------------------------------------------------------
# 通常処理
#-----------------------------------------------------------------------------

class JournalListView(LoginRequiredMixin, ListView):

    model = Journal
    context_object_name = 'items'
    template_name = 'fsjs_journals/index.html'

    # 初期処理
    def dispatch(self, request, *args, **kwargs):
        
        # 会計年度
        yyyy = ''
        if 'yyyy' in self.request.GET: 
            if self.request.GET['yyyy'].isdecimal():
                 yyyy = self.request.GET['yyyy']
        if yyyy == '':
            return redirect('fsjs_capitals:index')
        self.yyyy = yyyy
        
        # 元入金
        capital = Capital.objects.filter(yyyy=self.yyyy)
        if capital.count() == 0:
            return redirect('fsjs_capitals:index')
        self.capital ={
            'm1' : "{:,}".format(capital[0].m1),
            'm2' : "{:,}".format(capital[0].m2),
            'm3' : "{:,}".format(capital[0].m3),
            'm4' : "{:,}".format(capital[0].m4),
        }
        
        # ページネーション
        if 'page' in self.request.GET: 
            if self.request.GET['page'].isdecimal():
                self.current_page = int(self.request.GET['page'])
            else:
                return redirect(url('fsjs_journals:index', yyyy=self.yyyy))
        else:
            self.current_page = 1
        
        return super().dispatch(request, *args, **kwargs)
        
    # QuerySet
    def get_queryset(self):
        
        # メイン
        items = Journal.objects.filter(yyyy=self.yyyy) \
                .order_by('-mm', '-dd', 'summary', 'debit_account_id')

        # ページネーション
        per_page = 50 # ページ毎に表示するアイテム数
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

        # アイテム操作
        debit_list  = getDebitList(False)
        credit_list = getCreditList()
        for item in items:
            # 借方/貸方の名前を設定
            setAccountName(item, debit_list, credit_list)
            # 3桁カンマ
            item.money = "{:,}".format(item.money)
            # mm/dd
            dt = datetime(int(self.yyyy), int(item.mm), int(item.dd))
            item.mmdd = dt.strftime('%m') + '/' + dt.strftime('%d')
        
        # 12/31(期末)
        money = getAccountTotal(self.yyyy, 'm1', 3)            # 現金
        deposit = getAccountTotal(self.yyyy, 'm2', 4)          # その他の預金
        advance_payment = getAccountTotal(self.yyyy, 'm3', 13) # 前払金
        accounts_payable = getAccountTotal(self.yyyy, 'm4', 5) # 未払金
        
        sql =( 
              'SELECT 0 AS id,IFNULL(SUM(money),0) AS money  '
              'FROM fsjs_journals WHERE yyyy = %s AND credit_account_id = %s'
             )
        sales = Journal.objects.raw(sql, [self.yyyy, 12])
        sales = sales[0].money # 売上
        
        self.term_end ={ 
            'money' : "{:,}".format(money),
            'deposit' : "{:,}".format(deposit),
            'advance_payment' : "{:,}".format(advance_payment),
            'accounts_payable' : "{:,}".format(accounts_payable),
            'sales' : "{:,}".format(sales),
        }

        return items
    
    # テンプレート用のオブジェクトの設定
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['yyyy'] = self.yyyy
        context['capital'] = self.capital
        context['search_param'] = '&' + urlencode({'yyyy': self.yyyy})
        context['message'] = self.message
        context['term_end'] = self.term_end
        return context


class JournalCreateView(LoginRequiredMixin, CreateView):

    model = Journal
    fields = ['yyyy', 'mm', 'dd', 'debit_account_id', 'credit_account_id', \
              'money', 'summary']
    template_name = 'fsjs_journals/create.html'
    
    # 初期処理
    def dispatch(self, request, *args, **kwargs):
        
        # 会計年度
        yyyy = ''
        if 'yyyy' in self.request.GET: 
            yyyy = self.request.GET['yyyy']
        if 'yyyy' in self.request.POST: 
            yyyy = self.request.POST['yyyy']
        if yyyy == '':
            return redirect('fsjs_capitals:index')
            
        if not yyyy.isdecimal():
            return redirect('fsjs_capitals:index')
        
        capital = Capital.objects.filter(yyyy=yyyy)
        if capital.count() == 0:
            return redirect('fsjs_capitals:index')
        self.yyyy = yyyy
        
        return super().dispatch(request, *args, **kwargs)
    
    # フォームの初期値の設定
    def get_initial(self):
        initial = super().get_initial()
        initial['yyyy'] = self.yyyy
        return initial
        
    # テンプレート用のオブジェクトの設定
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combo_debit']  = getDebitList(True)
        context['combo_credit'] = getCreditList() 
        return context
            
    # バリデーションの成功
    def form_valid(self, form):
    
        # カスタムバリデーション1
        if form.instance.debit_account_id == form.instance.credit_account_id:
            form.add_error('debit_account_id',  \
                '借方と貸方に同一科目は登録できません。')
            form.add_error('credit_account_id', \
                '借方と貸方に同一科目は登録できません。')
            return self.form_invalid(form)

        # カスタムバリデーション2
        result = money_check(form.instance, '')
        if result != '':
            form.add_error('money', result)
            return self.form_invalid(form)

        try:
            with transaction.atomic(): 
                form.save()
                messages.success(self.request, "登録しました。")
        except Exception as e:
            messages.error(self.request, \
                "エラーが発生しました。管理者に問い合わせてください。")

        return redirect(url('fsjs_journals:index', yyyy=form.instance.yyyy))
        
    # バリデーションの失敗
    def form_invalid(self, form):
        messages.error(self.request, "エラーをご確認ください。")
        return super().form_invalid(form)


class JournalDetailView(LoginRequiredMixin, DetailView):

    model = Journal
    context_object_name = 'item'
    template_name = 'fsjs_journals/show.html'

    # テンプレート用のオブジェクトの設定
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 借方/貸方の名前を設定
        debit_list  = getDebitList(False)
        credit_list = getCreditList()
        setAccountName(context['item'], debit_list, credit_list)
        
        # 3桁カンマ
        context['item'].money = "{:,}".format(context['item'].money)
        
        # 日付
        dt = datetime(int(context['item'].yyyy), \
                int(context['item'].mm), int(context['item'].dd))
        context['item'].ymd = dt.strftime('%Y/%m/%d')

        return context


class JournalUpdateView(LoginRequiredMixin, UpdateView):

    model = Journal
    fields = ['yyyy', 'mm', 'dd', 'debit_account_id', 'credit_account_id', \
              'money', 'summary']
    template_name = 'fsjs_journals/edit.html'
    
    # テンプレート用のオブジェクトの設定
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combo_debit']  = getDebitList(True)
        context['combo_credit'] = getCreditList() 
        return context
            
    # バリデーションの成功
    def form_valid(self, form):
    
        # カスタムバリデーション1
        if form.instance.debit_account_id == form.instance.credit_account_id:
            form.add_error('debit_account_id',  \
                '借方と貸方に同一科目は登録できません。')
            form.add_error('credit_account_id', \
                '借方と貸方に同一科目は登録できません。')
            return self.form_invalid(form)

        # カスタムバリデーション2
        result = money_check(form.instance, form.instance.pk)
        if result != '':
            form.add_error('money', result)
            return self.form_invalid(form)

        try:
            with transaction.atomic(): 
                form.save()
                messages.success(self.request, "登録しました。")
        except Exception as e:
            messages.error(self.request, \
                "エラーが発生しました。管理者に問い合わせてください。")

        return redirect(url('fsjs_journals:index', yyyy=form.instance.yyyy))

    # バリデーションの失敗
    def form_invalid(self, form):
        messages.error(self.request, "エラーをご確認ください。")
        return super().form_invalid(form)


class JournalDeleteView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if (request.method == 'DELETE'):
            try:
                journal = Journal.objects.get(id=kwargs['pk'])
                with transaction.atomic(): 
                    journal.delete()                   
                    messages.error(request, "削除しました。")
                return HttpResponse('')
            except Exception as e:
                messages.error(request, \
                    "エラーが発生しました。管理者に問い合わせてください。")
        return super().dispatch(request, *args, **kwargs)


