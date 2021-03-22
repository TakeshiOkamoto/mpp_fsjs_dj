# ------------------
#  固有の共通処理
# ------------------
from django.shortcuts import redirect

from fsjs_journals.models import Journal
from fsjs_capitals.models import Capital


# ログインのリダイレクト用 ※ミックスイン
class LoginRequiredMixin():

    def dispatch(self, request, *args, **kwargs):
        if not 'name' in request.session:
            return redirect('fsjs_login:login')
        return super().dispatch(request, *args, **kwargs)


# 対象科目の合計金額を取得する
def getAccountTotal(yyyy, obj, target_id):
    
    # 元入金
    capital = Capital.objects.filter(yyyy=yyyy)
    if capital.count() == 0:
        return 0
    
    # 借方
    sql = (
           'SELECT 0 AS id, IFNULL(SUM(money),0) AS money FROM fsjs_journals '
           'WHERE yyyy = %s AND debit_account_id = %s'
          )
    debit = Journal.objects.raw(sql, [yyyy, target_id])

    # 貸方
    sql = (
           'SELECT 0 AS id, IFNULL(SUM(money),0) AS money FROM fsjs_journals '
           'WHERE yyyy = %s AND credit_account_id = %s'
          )
    credit = Journal.objects.raw(sql, [yyyy, target_id])

    if obj == 'm4':
        # 未払金
        total = getattr(capital[0], obj) + credit[0].money - debit[0].money
    else:
        # 現金、その他の預金、前払金
        total = getattr(capital[0], obj) + debit[0].money - credit[0].money
    return total


