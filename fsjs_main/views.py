from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.http import HttpResponse

from fsjs_journals.models import Journal
from fsjs_capitals.models import Capital
from fsjs_accounts.models import Account

from module.fsjs.common import getAccountTotal
from module.fsjs.common import LoginRequiredMixin


class IndexView(LoginRequiredMixin, TemplateView):

    template_name = 'fsjs_main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 会計年度
        yyyy = ''
        if 'yyyy' in self.request.GET: 
            if self.request.GET['yyyy'].isdecimal():
                 yyyy = self.request.GET['yyyy']
        context['yyyy'] = yyyy

        capitals = Capital.objects.order_by('yyyy').reverse()
        for key, capital in enumerate(capitals):
            capital.modulo3 = (key+1) % 3
            capital.modulo5 = (key+1) % 5
        context['capitals'] = capitals
        if yyyy == '':
            return context

        # 元入金(期首)
        report_bs_st = Capital.objects.filter(yyyy=yyyy)
        if report_bs_st.count() == 0:
            context['yyyy'] = ''
            return context

        # ----------------------------------
        #  損益計算書
        # ----------------------------------

        # 売上
        sql = (
               'SELECT 0 AS id, IFNULL(SUM(money),0) AS money '
               'FROM fsjs_journals WHERE yyyy = %s AND credit_account_id = 12'
              )
        report_pl_total = Journal.objects.raw(sql, [yyyy])[0].money
        context['report_pl_total'] = "{:,}".format(report_pl_total)
        
        # 経費
        sql = (
               'SELECT 0 AS id, fsjs_accounts.name, '
               '    IFNULL(SUM(fsjs_journals.money),0) AS money '
               'FROM fsjs_accounts '
               'LEFT JOIN fsjs_journals '
               '    ON fsjs_accounts.id = fsjs_journals.debit_account_id '
               '    AND fsjs_journals.yyyy = %s '
               'WHERE fsjs_accounts.expense_flg = 1  '
               'GROUP BY fsjs_accounts.name '
               'ORDER BY fsjs_accounts.sort_expense ASC '
              )
        report_pl_keihi = Account.objects.raw(sql, [yyyy])
        
        keihi_total = 0
        for item in report_pl_keihi:
            keihi_total = keihi_total + item.money
            item.money = "{:,}".format(item.money)
            
        context['report_pl_keihi'] = report_pl_keihi
        context['keihi_total'] = "{:,}".format(keihi_total)
        
        # 所得
        income = report_pl_total - keihi_total
        context['income'] = income
        context['income_comma'] = "{:,}".format(income)
        context['income_comma_65'] = "{:,}".format(income - 650000)
        
        # ----------------------------------
        #  月別売上(収入)金額及び仕入金額
        # ----------------------------------
        report_month = []
        for i in range(12):
            sql = (
                   'SELECT 0 AS id, IFNULL(SUM(money),0) AS money '
                   'FROM fsjs_journals WHERE yyyy = %s AND mm = %s '
                   '    AND credit_account_id = 12 '
                  )
            report_month.append(Journal.objects.raw(sql, [yyyy, (i+1)])[0])
            
        sale_total = 0
        for item in report_month:
            sale_total = sale_total + item.money
            item.money = "{:,}".format(item.money)
        context['report_month'] = report_month
        context['sale_total'] = "{:,}".format(sale_total)
        
        # ----------------------------------
        #  貸借対照表
        # ----------------------------------

        # 元入金(期首)
        report_bs_st = report_bs_st[0]
        context['report_bs_st'] ={
            'm1': "{:,}".format(report_bs_st.m1),
            'm2': "{:,}".format(report_bs_st.m2),
            'm3': "{:,}".format(report_bs_st.m3),
            'm4': "{:,}".format(report_bs_st.m4),
        }
        
        # 事業主貸(期末)
        sql = (
               'SELECT 0 AS id, IFNULL(SUM(money),0) AS money  '
               'FROM fsjs_journals WHERE yyyy = %s AND debit_account_id = 1'
              )
        report_bs_debit = Journal.objects.raw(sql, [yyyy])[0].money
        context['report_bs_debit'] = "{:,}".format(report_bs_debit)
        
        # 事業主借(期末)
        sql = (
               'SELECT 0 AS id, IFNULL(SUM(money),0) AS money  '
               'FROM fsjs_journals WHERE yyyy = %s AND credit_account_id = 2'
              )
        report_bs_credit = Journal.objects.raw(sql, [yyyy])[0].money
        context['report_bs_credit'] = "{:,}".format(report_bs_credit)

        # 現金(期末)
        report_bs_en_m1 = getAccountTotal(yyyy, 'm1', 3);
        context['report_bs_en_m1'] =  "{:,}".format(report_bs_en_m1)
        
        # その他の預金(期末)
        report_bs_en_m2 = getAccountTotal(yyyy, 'm2', 4);
        context['report_bs_en_m2'] =  "{:,}".format(report_bs_en_m2)

        # 前払金(期末)
        report_bs_en_m3 = getAccountTotal(yyyy, 'm3', 13);
        context['report_bs_en_m3'] =  "{:,}".format(report_bs_en_m3)
                
        # 未払金(期末)
        report_bs_en_m4 = getAccountTotal(yyyy, 'm4', 5);
        context['report_bs_en_m4'] =  "{:,}".format(report_bs_en_m4)
        
        # 合計(資産の部)
        bs_sum1 = report_bs_st.m1 + report_bs_st.m2 + report_bs_st.m3
        context['bs_sum1'] = "{:,}".format(bs_sum1)
        bs_sum2 = report_bs_en_m1 + report_bs_en_m2 + report_bs_en_m3 + \
                    report_bs_debit
        context['bs_sum2'] = "{:,}".format(bs_sum2)

        # 元入金
        capital_total = report_bs_st.m1 + report_bs_st.m2 + \
                            report_bs_st.m3 - report_bs_st.m4
        context['capital_total'] = "{:,}".format(capital_total)
        
        # 合計(負債・資本の部)
        bs_sum3 = report_bs_st.m4 + capital_total
        context['bs_sum3'] = "{:,}".format(bs_sum3)
        bs_sum4 = report_bs_en_m4 + report_bs_credit + capital_total + income
        context['bs_sum4'] = "{:,}".format(bs_sum4)
        
        # 整合性チェック
        a1 = report_bs_st.m1 + report_bs_st.m2 + report_bs_st.m3
        a2 = report_bs_en_m1 + report_bs_en_m2 + report_bs_en_m3 + \
                report_bs_debit
        b1 = report_bs_st.m4 + capital_total
        b2 = report_bs_en_m4 + report_bs_credit + capital_total + income
        
        if a1 == b1 and a2 == b2:
            context['error'] = False
        else:
            context['error'] = True
            
        return context


