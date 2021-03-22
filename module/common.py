# ------------------
#  共通モジュール
# ------------------
from django.urls import reverse
from django.utils.http import urlencode
from django.core.validators import ValidationError


# 1. 全角スペースを半角へ
# 2. 文字前後の半角/全角+制御文字(改行など)を削除する
def trim(s):
    return s.replace('　',' ').strip()


# リダイレクト用のURLを生成する
def url(viewname, **kwargs):
    view = reverse(viewname)
    if len(kwargs) == 0:
        return view
    else:
        params = urlencode(kwargs)
        return f'{view}?{params}'


# クライアントのIPアドレスを取得する
def get_ip_address(request):
    obj = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if obj:
        ip = obj.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


#----------------------
# バリデーション 
#----------------------

# 禁止用語 
# ※各自で追加して下さい
NG_WORDS =[
  'カジノ',
  'ギャンブル',
]

# NGワード
def NgWord(value):
    for ng in NG_WORDS:
        if value.find(ng) != -1:
            raise ValidationError('禁止用語が含まれています。')


