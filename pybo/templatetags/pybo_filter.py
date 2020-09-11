import markdown
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def sub(value, arg):
    return value-arg

# 위처럼 sub 함수에 @register.filter 라는 어노테이션을 적용하면 템플릿에서 해당 함수를 필터로 사용할 수 있게 된다. sub 함수는 기존 값(value)에서 입력으로 받은 값(arg)을 빼서 리턴하는 필터이다.

# 마크다운으로 작성한 문서를 HTML문서로 변환하기 위해서는 템플릿에서 사용할 마크다운 필터를 작성해야 한다. 이전에 sub 필터를 작성한 pybo_filter.py 파일에 다음처럼 mark 함수를 추가하자.


@register.filter
def mark(value):
    extensions = ["nl2br", "fenced_code"]
    return mark_safe(markdown.markdown(value, extensions=extensions))
