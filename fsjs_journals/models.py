from django.db import models
from django.core.validators import MaxLengthValidator
from django.core.validators import MinValueValidator, MaxValueValidator

# 仕訳帳
class Journal(models.Model):

    class Meta:
        db_table = 'fsjs_journals'
        verbose_name = '仕訳帳'
        
    # 年
    yyyy = models.IntegerField(verbose_name='年', \
        db_index=True, \
        validators=[ MinValueValidator(1989), \
            MaxValueValidator(2099)])
    
    # 月
    mm = models.IntegerField(verbose_name='月', \
        db_index=True, \
        validators=[ MinValueValidator(1), \
            MaxValueValidator(12)])
    # 日
    dd = models.IntegerField(verbose_name='日', \
        db_index=True, \
        validators=[ MinValueValidator(1), \
            MaxValueValidator(31)])
            
    # 科目コード(借方)
    debit_account_id = models.IntegerField(verbose_name='科目コード(借方)')
    
    # 科目コード(貸方)
    credit_account_id = models.IntegerField(verbose_name='科目コード(貸方)')
    
    # 金額
    money = models.IntegerField(verbose_name='金額', \
        validators= [MinValueValidator(1), \
            MaxValueValidator(1000000000)])
            
    # 摘要
    summary = models.CharField(verbose_name='摘要', \
        max_length=50, default='', \
        validators=[MaxLengthValidator(50)])

    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '<id=' + str(self.id) + ', date=' \
                    + str(self.yyyy) + '/' \
                    + str(self.mm) + '/' \
                    + str(self.dd) + \
                '>'

