from django.db import models
from django.core.validators import MaxLengthValidator
from django.core.validators import MinValueValidator, MaxValueValidator

# 元入金
# ※1/1(期首)の元入金。最低限必要な項目のみ
class Capital(models.Model):

    class Meta:
        db_table = 'fsjs_capitals'
        verbose_name = '元入金'

    # 西暦(年)
    yyyy = models.IntegerField(verbose_name='年', \
        unique=True, \
        validators=[ MinValueValidator(1989), \
            MaxValueValidator(2099)])
    
    # 現金
    m1 = models.IntegerField(verbose_name='現金', \
        default=0, \
        validators= [MinValueValidator(0), \
            MaxValueValidator(1000000000)])
        
    # その他の預金
    m2 = models.IntegerField(verbose_name='その他の預金', \
        default=0, \
        validators= [MinValueValidator(0), \
            MaxValueValidator(1000000000)])
            
    # 前払金
    m3 = models.IntegerField(verbose_name='前払金', \
        default=0, \
        validators= [MinValueValidator(0), \
            MaxValueValidator(1000000000)])
            
    # 未払金
    m4 = models.IntegerField(verbose_name='未払金', \
        default=0, \
        validators= [MinValueValidator(0), \
            MaxValueValidator(1000000000)])

    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '<id=' + str(self.id) + ', yyyy=' + str(self.yyyy) + '>'

