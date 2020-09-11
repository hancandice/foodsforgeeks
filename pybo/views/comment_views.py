from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone
from django.core.paginator import Paginator
# from django.http import HttpResponse
from ..models import Question, Answer, Comment
from ..forms import QuestionForm, AnswerForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.


@login_required(login_url='account_login')
def commentCreateQuestion(request, questionId):
    question = get_object_or_404(Question, pk=questionId)
    if request.method == "GET":
        form = CommentForm()
        context = {'form': form}
        return render(request, 'pybo/comment_form.html', context)
    else:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.createDate = timezone.now()
            comment.question = question
            comment.save()
            return redirect('{}#comment_{}'.format(resolve_url('pybo:detail', questionId=comment.question.id), comment.id))
        else:
            return render(request, 'pybo/comment_form.html', {'form': form})


@login_required(login_url='account_login')
def commentModifyQuestion(request, commentId):
    comment = get_object_or_404(Comment, pk=commentId)
    if request.user != comment.author:
        messages.warning(request, "Not authorized to modify")
        return redirect('pybo:detail', questionId=comment.question.id)
    else:
        if request.method == "GET":
            form = CommentForm(instance=comment)
            context = {'form': form}
            return render(request, 'pybo/comment_form.html', context)
        else:
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.modifyDate = timezone.now()
                comment.save()
                return redirect('{}#comment_{}'.format(resolve_url('pybo:detail', questionId=comment.question.id), comment.id))
            else:
                context = {'form': form}
                return render(request, 'pybo/comment_form.html', context)


@login_required(login_url='account_login')
def commentDeleteQuestion(request, commentId):
    comment = get_object_or_404(Comment, pk=commentId)
    if request.user != comment.author:
        messages.warning(request, 'Not authorized to delete')
        return redirect('pybo:detail', questionId=comment.question.id)
    else:
        comment.delete()
        messages.info(request, 'Successfully deleted your comment.')

        return redirect('pybo:detail', questionId=comment.question.id)


@login_required(login_url='account_login')
def commentCreateAnswer(request, answerId):
    answer = get_object_or_404(Answer, pk=answerId)
    if request.method == "GET":
        form = CommentForm()
        context = {'form': form}
        return render(request, 'pybo/comment_form.html', context)
    else:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.createDate = timezone.now()
            comment.answer = answer
            comment.save()
            return redirect('{}#comment_{}'.format(resolve_url('pybo:detail', questionId=comment.answer.question.id), comment.id))
        else:
            return render(request, 'pybo/comment_form.html', {'form': form})


@login_required(login_url='account_login')
def commentModifyAnswer(request, commentId):
    comment = get_object_or_404(Comment, pk=commentId)
    if request.user != comment.author:
        messages.warning(request, "Not authorized to modify")
        return redirect('pybo:detail', questionId=comment.answer.question.id)
    else:
        if request.method == "GET":
            form = CommentForm(instance=comment)
            context = {'form': form}
            return render(request, 'pybo/comment_form.html', context)
        else:
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.modifyDate = timezone.now()
                comment.save()
                return redirect('{}#comment_{}'.format(resolve_url('pybo:detail', questionId=comment.answer.question.id), comment.id))
            else:
                context = {'form': form}
                return render(request, 'pybo/comment_form.html', context)


@login_required(login_url='account_login')
def commentDeleteAnswer(request, commentId):
    comment = get_object_or_404(Comment, pk=commentId)
    if request.user != comment.author:
        messages.warning(request, 'Not authorized to delete')
        return redirect('pybo:detail', questionId=comment.answer.question.id)
    else:
        comment.delete()
        messages.info(request, 'Successfully deleted your comment.')
        return redirect('pybo:detail', questionId=comment.answer.question.id)
