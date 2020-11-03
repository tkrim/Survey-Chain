from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.forms import formset_factory
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Question, Choice, VoterSelection
from .forms import *

class IndexView(generic.ListView):
    
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    
    def get_queryset(self):
        """Return the last five published questions
           (not including those set to be published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
    
class DetailView(generic.DetailView):
    
    model = Question
    template_name = 'polls/detail.html'
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
    
class ResultsView(generic.DetailView):
    
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    
    question = get_object_or_404(Question, pk=question_id)
    user = request.user
    
    if request.user.is_anonymous:
        return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "Please login or signup to vote.",
        })
    else:
        try:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form.
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
        # check if the user voted on the question
        if VoterSelection.objects.filter(voter=user, question_id=question_id).exists():
            for choice in question.choice_set.all():
                return render(request, 'polls/detail.html', {
                    'question': question,
                    'error_message': "You already voted on this question.\
                                    Please vote on a dfferent question.",
                })
        
        else:
            VoterSelection.objects.create(choice=selected_choice, voter=user, question_id=question_id)
            selected_choice.votes += 1
            selected_choice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
            
def new_poll(request):
    
    ChoiceFormSet = formset_factory(ChoiceForm, extra=3, min_num=2, validate_min=True)
    question_form = QuestionForm() # when a url is called initially it is GET method so you have to send a instance of form first (empty form)
    choice_form = ChoiceForm()
    
    if request.method == 'POST':
        form = QuestionForm(request.POST or None)
        formset = ChoiceFormSet(request.POST or None, request.FILES)
        if form.is_valid() and formset.is_valid():
            new_poll = form.save(commit=False)
            new_poll.author = request.user
            new_poll.save()
            for inline_form in formset:
                if inline_form.cleaned_data:
                    choice = inline_form.save(commit=False)
                    choice.question = new_poll
                    choice.save()
            return redirect('/polls/')
    else:
        form = QuestionForm() # this will return the errors in your form
        formset = ChoiceFormSet()
        
    tmpl_vars = {
        'formset': formset,
        'form': form,
    }
        
    return render(request, 'polls/new.html', tmpl_vars)
