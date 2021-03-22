from django.db import models
from django.core.validators import MaxLengthValidator
from django.core.validators import MinValueValidator, MaxValueValidator

# 勘定科目
class Account(models.Model):

    class Meta:
        db_table = 'fsjs_accounts'
        verbose_name = '勘定科目'
        
    # 名前
    name = models.CharField(verbose_name='名前', \
        max_length=20, unique=True, default='', \
        validators=[MaxLengthValidator(20)])
        
    # 種類(1:借方 2:貸方 3:両方)
    types = models.IntegerField(verbose_name='種類', \
        db_index=True, \
        validators=[ \
            MinValueValidator(1), \
            MaxValueValidator(3)])
            
    #  経費フラグ(true:経費 false:経費以外)
    expense_flg = models.BooleanField(verbose_name='経費フラグ', \
         default=False, db_index=True,)
    
    # 表示順序(リスト用)
    sort_list = models.IntegerField(verbose_name='表示順序(リスト用)', \
        validators=[MaxValueValidator(1000)])
        
    # 表示順序(経費用) ※損益計算書で使用する経費以外は-1
    sort_expense = models.IntegerField(verbose_name='表示順序(経費用)', \
        validators=[MaxValueValidator(1000)])

    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '<id=' + str(self.id) + ', name=' + self.name + '>'

