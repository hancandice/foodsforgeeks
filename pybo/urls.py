from django.urls import path

from .views import base_views, question_views, answer_views, comment_views, vote_views

app_name = 'pybo'
urlpatterns = [
    path('', base_views.index, name="index"),
    path('<int:questionId>/', base_views.detail, name="detail"),
    path('answer/create/<int:questionId>/',
         answer_views.answerCreate, name="answer_create"),
    path("question/create/", question_views.questionCreate, name="question_create"),
    path("question/modify/<int:question_id>/",
         question_views.questionModify, name="question_modify"),
    path('question/delete/<int:questionId>/',
         question_views.questionDelete, name="question_delete"),
    path('answer/modify/<int:answerId>/',
         answer_views.answerModify, name="answer_modify"),
    path('answer/delete/<int:answerId>/',
         answer_views.answerDelete, name="answer_delete"),
    path('comment/create/question/<int:questionId>/',
         comment_views.commentCreateQuestion, name="comment_create_question"),
    path('comment/modify/question/<int:commentId>/',
         comment_views.commentModifyQuestion, name="comment_modify_question"),
    path('comment/delete/question/<int:commentId>/',
         comment_views.commentDeleteQuestion, name="comment_delete_question"),
    path('comment/create/answer/<int:answerId>/',
         comment_views.commentCreateAnswer, name='comment_create_answer'),
    path('comment/modify/answer/<int:commentId>/',
         comment_views.commentModifyAnswer, name='comment_modify_answer'),
    path('comment/delete/answer/<int:commentId>/',
         comment_views.commentDeleteAnswer, name='comment_delete_answer'),
    path('vote/question/<int:questionId>/',
         vote_views.voteQuestion, name="vote_question"),
    path('vote/answer/<int:answerId>/',
         vote_views.voteAnswer, name="vote_answer"),
]
