from django.db import models
from django.core.validators import MaxLengthValidator


# ユーザー
class User(models.Model):

    class Meta:
        db_table = 'fsjs_users'
        verbose_name = 'ユーザー'

    # 名前
    name = models.CharField(verbose_name='名前', \
        max_length=50, \
        validators=[MaxLengthValidator(50)])

    # メール
    email = models.EmailField(verbose_name='メールアドレス', \
        max_length=250, unique=True, \
        validators=[MaxLengthValidator(250)])
        
    # パスワード
    password = models.CharField(verbose_name='パスワード', \
        max_length=250, \
        validators=[MaxLengthValidator(250)])
        
    # 作成日時     
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '<id=' + str(self.id) + ', name=' + self.name + '>'


