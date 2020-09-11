from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator
# from django.http import HttpResponse
from ..models import Question, Answer, Comment
from ..forms import QuestionForm, AnswerForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url="account_login")
def questionCreate(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.createDate = timezone.now()
            question.save()
            return redirect("pybo:index")
        else:
            return render(request, "pybo/question_form.html", {'form': form})
    else:
        form = QuestionForm()
        return render(request, "pybo/question_form.html", {'form': form})


@login_required(login_url="account_login")
def questionModify(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.warning(request, 'Not authorized to modify')
        return redirect('pybo:detail', questionId=question_id)
    else:
        if request.method == "GET":
            form = QuestionForm(instance=question)
            context = {'form': form}
            return render(request, 'pybo/question_form.html', context)
        else:
            form = QuestionForm(request.POST, instance=question)
            if form.is_valid():
                question = form.save(commit=False)
                question.author = request.user
                question.modifyDate = timezone.now()
                question.save()
                return redirect('pybo:detail', questionId=question.id)
            else:
                return render(request, 'pybo/question_form.html', {'form': form})


# @login_required(login_url='account_login')
# def questionDelete(request, questionId):
#     question = get_object_or_404(Question, pk=questionId)
#     if request.user != question.author:
#         messages.warning(request, 'Not authorized to delete')
#         return redirect('pybo:detail', questionId=question.id)
#     question.delete()
#     return redirect('pybo:index')

@login_required(login_url='account_login')
def questionDelete(request, questionId):
    question = get_object_or_404(Question, pk=questionId)
    if request.user != question.author:
        messages.warning(request, 'Not authorized to delete')
        return redirect('pybo:detail', questionId=question.id)
    else:
        if (question.answer_set.count() > 0):
            messages.warning(
                request, "Question with answer(s) cannot be deleted")
            return redirect('pybo:detail', questionId=question.id)
        else:
            question.delete()
            messages.info(request, 'Successfully deleted your question.')
            return redirect('pybo:index')
