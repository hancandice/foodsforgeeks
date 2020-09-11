from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator
# from django.http import HttpResponse
from ..models import Question, Answer, Comment
from ..forms import QuestionForm, AnswerForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.db.models import Q, Count
# Create your views here.


def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    so = request.GET.get('so', 'recent')

    if so == "recommend":
        questionList = Question.objects.annotate(
            numVoter=Count('voter')).order_by('-numVoter', '-createDate')
    elif so == "popular":
        questionList = Question.objects.annotate(numAnswer=Count(
            'answer')).order_by('-numAnswer', '-createDate')
    else:
        questionList = Question.objects.order_by('-createDate')
    # page = request.GET.get('page', '1') 은 다음처럼 GET방식으로 요청한 URL에서 page의 값을 가져올때 사용한다. http://localhost:8000/pybo/?page=1
    # 만약 http://localhost:8000/pybo/ 처럼 page값이 없을 경우에는 디폴트로 1이라는 값을 설정한다.

    if kw:
        questionList = questionList.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이검색
            Q(answer__author__username__icontains=kw) |  # 답변 글쓴이검색
            Q(answer__content__icontains=kw)
        ).distinct()

    paginator = Paginator(questionList, 10)
    pageObj = paginator.get_page(page)
    context = {'questionList': pageObj, 'page': page, 'kw': kw, 'so': so}
    return render(request, 'pybo/question_list.html', context)
    # A context is a variable name -> variable value mapping that is passed to a template. Context processors let you specify a number of variables that get set in each context automatically – without you having to specify the variables in each render() call.


def detail(request, questionId):
    # question = Question.objects.get(id=questionId)
    question = get_object_or_404(Question, pk=questionId)
    context = {'question': question}
    return render(request, 'pybo/question_detail.html', context)
