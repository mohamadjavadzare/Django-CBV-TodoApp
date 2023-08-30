from django.db import models
from django.shortcuts import render, redirect

from django.views.generic.base import (TemplateView ,RedirectView)
from django.views.generic import (
            View,
            ListView,
            FormView,
            CreateView,
            UpdateView,
            DeleteView)
from .models import *
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Profile
from django.urls import reverse_lazy
# Create your views here.

# show todo list ../todo/task_list.html
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'todo/task_list.html'
    context_object_name = "tasks"

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        return self.model.objects.filter(user=profile)

    paginate_by = 7
    
    def get_context_data(self, **kwargs):
        context = super(TaskList, self).get_context_data(**kwargs)
        if not context.get('is_paginated', False):
            return context
        # Custom Pagination
        paginator = context.get('paginator')
        num_pages = paginator.num_pages
        current_page = context.get('page_obj')
        page_no = current_page.number

        if num_pages <= 5 or page_no <= 3:  # case 1 and 2
            pages = [x for x in range(1, min(num_pages + 1, 5))]
        elif page_no > num_pages - 3:  # case 4
            pages = [x for x in range(num_pages - 4, num_pages + 1)]
        else:  # case 3
            pages = [x for x in range(page_no - 2, page_no + 3)]

        # previous page and first page
        if page_no == 1 :
            previous_page = 1
            first_page = 1
        else:
            previous_page = pages[page_no-1] -1
            first_page = pages[0]

        # next page and last page
        if page_no == pages[-1] :
            next_page = page_no    
            last_page = 1
        else: # page_no ==1  , pages[page_no] == 2 , pages[page_no] +1 = 3
            next_page = pages[page_no-1] + 1 
            last_page = pages[-1]
        page_count = len(pages)
        context.update({'pages': pages ,
                        'first_page': first_page,
                        'last_page': last_page,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        # 'current_page' : page_no, 
                        'page_count' : page_count,} )
        return context


# create a task ../todo/task_form.html
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    form_class = CreateTaskForm
    success_url = reverse_lazy("todo:task_list")
    template_name = 'todo/task_list.html'

    # automatically detect author
    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        form.instance.user = profile
        return super().form_valid(form)
    
    

# update/edit a task ../todo/task_update.html
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'todo/task_update.html'
    success_url = reverse_lazy("todo:task_list")
    form_class = UpdateTaskForm
    # automatically detect author
    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        form.instance.user = profile
        return super().form_valid(form)
    

# delete  a task ../todo/task_confirm_delete.html
class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("todo:task_list")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
        
    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        return self.model.objects.filter(user=profile)



# mark a task as completed 
class TaskComplete(LoginRequiredMixin, View):
    model = Task
    success_url = reverse_lazy("todo:task_list")
    context_object_name = "task"

    def get(self, request, *args, **kwargs):
        task = Task.objects.get(id=kwargs.get('pk'))
        task.complete = True
        task.save()
        return redirect(self.success_url)