from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


from django.utils.html import escape
from datetime import datetime

# from .models import Question
# from .models import Arcade
from .models import History, Plan, Arcade, Subject, Question, Option

# Create your views here.
class CustomLoginView(LoginView):
	template_name='base/login.html'
	fields='__all__'
	redirect_authenticated_user = True

	def get_success_url(self):
		return reverse_lazy('home')

class RegisterPage(FormView):
	template_name='base/register.html'
	form_class = UserCreationForm
	redirect_authenticated_user = True
	success_url=reverse_lazy('home')

	def form_valid(self, form):
		user = form.save()
		if user is not None:
			login(self.request, user)
		return super(RegisterPage,self).form_valid(form)

	def get(self,*args, **kwargs):
		if self.request.user.is_authenticated:
			return redirect('home')
		return super(RegisterPage,self).get(*args, **kwargs)

class HomeView(LoginRequiredMixin,ListView):
	model=History
	template_name='base/home.html'
	context_object_name='quiz_history'

	def get_context_data(self, **kwargs):
		context=super().get_context_data(**kwargs)
		context['quiz_history'] = context['quiz_history'].filter(user=self.request.user).order_by("complete","created")
		context['count'] = context['quiz_history'].filter(complete=False).count()
		context['plans'] = Plan.objects.all()
		context['subjects'] = Subject.objects.all()

		search_input = self.request.GET.get('search-area') or ''
		if search_input:
			context['quiz_history'] = context['quiz_history'].filter(subject__name__icontains=search_input)
		context['search_input'] = search_input
		return context

class StartArcadeView(ListView):

	def get(self, request, plan, subject,session=0):
		#check if this is a request to resume
		if session > 0:
			session_obj = get_object_or_404(History, id=session)
			if session_obj.complete:
				request.session['preview_mode_enabled'] = True
			request.session['quiz_session_id'] = session
			request.session['quiz_last_question']=0
			return redirect('arcade',session=session)

		#start a new quiz session
		quiz=History(user=request.user,plan_id=plan,subject_id=subject,score=0,complete=False)
		quiz.save()
		
		q=Question.objects.filter(subject__id=subject,plan__id=plan).order_by("?")[0:10]
		
		last_viewed=True
		for q_obj in q:
			arcade=Arcade(user=request.user,plan=quiz.plan,history=quiz,question=q_obj, is_last_viewed=last_viewed)
			arcade.save()
			last_viewed=False
		
		request.session['quiz_session_id'] = quiz.id
		request.session['quiz_last_question'] = 1

		subjectObj=Subject.objects.get(id=subject)
		subjectSlug=str(subject)+'-'+subjectObj.name
		return redirect('arcade',session=quiz.id,subjectSlug=subjectSlug)

class ArcadeView(ListView):
	template_name='base/arcade.html'

	def get(self, request, session, subjectSlug='', direction='stale'):
		if int(request.session.get('quiz_session_id')) != int(session):
			session=int(request.session.get('quiz_session_id'))
			return redirect('arcade',session=session)
		
		quiz = History.objects.get(id=session)
		if quiz.complete:
			self.template_name='base/arcade_closed.html'

		last_q=int(request.session['quiz_last_question']) or 0

		arcade_obj = self.quiz_operator(request,session,last_q,direction,last_q)
		request.session['quiz_last_question']=arcade_obj['last_q']
		return render(request,self.template_name,arcade_obj)
		
	def post(self, request, session, subjectSlug='', direction='next'):
		if int(request.session.get('quiz_session_id')) != int(session):
			return redirect('home')
		if request.POST.get('quit') is not None:
			return self.closeQuiz(request,session)
		
		selected = request.POST.get('arcade-options')
		last_q = int(request.POST.get('last_q'))

		if selected is not None:
			selected = int(selected)
			option = Option.objects.get(id=selected)

			Arcade.objects.filter(history_id=session).update(is_last_viewed=False)

			arcade = Arcade.objects.filter(history_id=session)[last_q-1:last_q]
			arcade=arcade[0]

			if arcade.selected_id is not selected:
				arcade.selected_as_text = option.option
				arcade.passed = option.is_answer
				arcade.selected_id = option.id
				arcade.save()

				history = arcade.history
				history.score+=option.is_answer
				history.save()
		
		if request.POST.get('submit') is not None:
			return self.closeQuiz(request,session)

		if request.POST.get('prev') is not None:
			request.session['quiz_last_question']=last_q-1
		else:
			request.session['quiz_last_question']=last_q+1
		return redirect('arcade',session=session)

	def quiz_operator(self,request, session,last_q,direction='stale',ignore_last_viewed=0):
		# get next/prev/same question
		if direction == 'stale':
			last_q=last_q

		if direction == 'prev':
			last_q-=1

		if direction == 'next':
			last_q+=1

		if last_q > 10:
			last_q=1
		
		if last_q < 1:
			last_q=10

		arcade = None
		if not ignore_last_viewed:
			arcadeList=Arcade.objects.filter(history_id=session).order_by('id')
			for index, item in enumerate(arcadeList):
				if item.is_last_viewed:
					last_q=index+1
					arcade=item
					break

		if arcade is None:
			arcade=Arcade.objects.filter(history_id=session)[last_q-1:last_q]
			arcade=arcade[0]

		arcade_obj={}
		arcade_obj['selected_option'] = arcade.selected_id
		arcade_obj['question'] = question = arcade.question
		arcade_obj['options'] = Option.objects.filter(question__id=question.id)
		arcade_obj['last_q'] = last_q

		if not arcade.is_last_viewed:
			Arcade.objects.filter(history_id=session).update(is_last_viewed=False)
			arcade.is_last_viewed=True
			arcade.save()
		return arcade_obj
		
	def closeQuiz(self, request, session):
		quiz = History.objects.get(id=session)
		quiz.complete=True
		quiz.complete_at=datetime.now()
		quiz.save()
		request.session['quiz_last_question']=0
		request.session['quiz_session_id'] = 0
		return redirect('home')
