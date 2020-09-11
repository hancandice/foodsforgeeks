from django.db import models
from django.conf import settings


class Question(models.Model):
    # 제목처럼 글자수의 길이가 제한된 텍스트는 CharField를 사용해야 한다.
    subject = models.CharField(max_length=200)
    content = models.TextField()
    # 내용(content)처럼 글자수를 제한할 수 없는 텍스트는 위처럼 TextField를 사용해야 한다.
    createDate = models.DateTimeField()
    # 작성일시처럼 날짜와 시간에 관계된 속성은 DateTimeField를 사용해야 한다.
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE, related_name="author_question")
    modifyDate = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="voter_question")
    # 이렇게 하면 이제 특정 사용자가 작성한 질문을 얻기 위해서는 current_user.author_question.all() 처럼 사용할 수 있다. 마찬가지로 특정 사용자가 투표한 질문을 얻기 위해서는 current_user.voter_question.all() 처럼 사용할 수 있다. (current_user는 특정 사용자를 의미한다.)

    def __str__(self):
        return self.subject
    # ※ 모델에 메서드가 추가될 경우에는 makemigrations와 migrate 를 수행할 필요는 없다. migrate가 필요한 경우는 모델의 속성이 변경되었을 때뿐이다.


class Answer(models.Model):
    # 기존 모델을 속성으로 가져갈 경우 ForeignKey를 이용해야 한다. ForeignKey는 다른 모델과의 연결을 의미한다. on_delete=models.CASCADE의 의미는 이 답변과 연결된 질문(Question)이 삭제될 경우 답변(Answer)도 함께 삭제된다는 의미이다.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author_answer")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # Question과 Answer는 서로 연결되어 있기 때문에 answer_set을 사용하면 질문과 연결된 답변을 가져올 수 있다. Answer모델에서 ForignKey로 Question을 연결해 주었기 때문에 answer_set이 가능해진 것이다.
    content = models.TextField()
    createDate = models.DateTimeField()
    modifyDate = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="voter_answer")
    # null=True의 의미는 modify_date를 데이터베이스에 저장할때 null이 허용된다는 의미이다. blank=True의 의미는 입력 폼 데이터 체크시(form.is_valid()) 값이 없어도 오류를 내지 않는다는 의미이다. 즉, null=True, blank=True을 사용하면 어떤 조건으로든 값을 비워둘수 있음을 의미한다. 수정일시는 수정이 발생할 경우에만 생성되는 데이터이므로 null=True, blank=True 속성을 지정하였다.

# 이제 작성한 모델을 이용하여 테이블들을 생성해 보자. 테이블 생성을 위해 가장 먼저 해야 할 일은 pybo앱을 config/settings.py 파일의 INSTALLED_APPS 항목에 추가하는 일이다.


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    createDate = models.DateTimeField()
    modifyDate = models.DateTimeField(null=True, blank=True)
    question = models.ForeignKey(
        Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(
        Answer, null=True, blank=True, on_delete=models.CASCADE)
