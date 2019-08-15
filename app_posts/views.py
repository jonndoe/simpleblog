from django.views.generic.list import ListView
from django.views.generic.detail import DetailView


from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic.base import TemplateResponseMixin, View
from .forms import MyCommentForm, SearchForm

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


from django.forms.models import modelform_factory
from django.apps import apps
from .models import Post, Content, MyComment

from braces.views import CsrfExemptMixin, JsonRequestResponseMixin

from django.db.models import Count
from .models import Subject

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from taggit.models import Tag



class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerPostMixin(OwnerMixin, LoginRequiredMixin):
    model = Post
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')



class OwnerPostEditMixin(OwnerPostMixin, OwnerEditMixin):
    fields = ['subject', 'title', 'slug',]
    success_url = reverse_lazy('manage_post_list')
    template_name = 'posts/manage/post/form.html'


class ManagePostListView(OwnerPostMixin, ListView):
    template_name = 'posts/manage/post/list.html'


class PostCreateView(OwnerPostEditMixin, CreateView):
    pass


class PostUpdateView(OwnerPostEditMixin, UpdateView):
    pass


class PostDeleteView(OwnerPostEditMixin, DeleteView):
    template_name = 'posts/manage/post/delete.html'
    success_url = reverse_lazy('manage_post_list')




class ContentCreateUpdateView(TemplateResponseMixin, View):
    postobj = None
    model = None
    obj = None
    template_name = 'posts/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='app_posts',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, post_id, model_name, id=None):
        self.postobj = get_object_or_404(Post,
                                        id=post_id,
                                        owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super(ContentCreateUpdateView,
                         self).dispatch(request, post_id, model_name, id)

    def get(self, request, post_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, post_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(post=self.postobj,
                                       item=obj)
            return redirect('post_content_list', self.postobj.id)

        return self.render_to_response({'form': form,
                                        'object': self.obj})




class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    )
        postobj = content.post
        content.item.delete()
        content.delete()
        return redirect('post_content_list', postobj.id)


class PostContentListView(TemplateResponseMixin, View):
    template_name = 'posts/manage/post/content_list.html'

    def get(self, request, post_id):
        postobj = get_object_or_404(Post,
                                   id=post_id,
                                   owner=request.user)

        return self.render_to_response({'post': postobj})


class ContentOrderView(CsrfExemptMixin,
                       JsonRequestResponseMixin,
                       View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                                   post__owner=request.user).update(order=order)
        return self.render_json_object_response({'saved': 'OK'})





class PostListView(TemplateResponseMixin, View):
    model = Post
    template_name = 'posts/post/list.html'

    def get(self, request, subject=None, tag_slug=None):
        subjects = Subject.objects.annotate(
            total_posts=Count('posts'))
        posts = Post.published.annotate(
            total_contents=Count('contents'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            posts = posts.filter(subject=subject)
        tag = None
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            posts = posts.filter(tags__in=[tag])
            print(posts)
            tagged_posts = len(posts)
        else:
            tagged_posts = None

        #pagination
        paginator = Paginator(posts, 3) # 3 posts in each page
        page = request.GET.get('page')
        tags = Tag.objects.all()
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            # if page is not an iteger deliver the first page
            posts = paginator.page(1)
        except EmptyPage:
            # if page is out of range deliver last page of results
            posts = paginator.page(paginator.num_pages)

        return self.render_to_response({'subjects': subjects,
                                        'subject': subject,
                                        'page': page,
                                        'posts': posts,
                                        'tagged_posts': tagged_posts,
                                        'tag': tag,
                                        'tags': tags,
                                        'section': 'posts'})



#class PostDetailView(DetailView):
   # model = Post
   # template_name = 'posts/post/detail.html'


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # list of active comments for the post
    comments = post.mycomments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # a comment was posted
        comment_form = MyCommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.owner = request.user
            new_comment.save()
    else:
        comment_form = MyCommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                                 .order_by('-same_tags','-publish')[:4]

    return render(request,
                  'posts/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A')+ SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.3).order_by('-similarity')
    return render(request,
                  'posts/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})





'''
class PostOrderView(CsrfExemptMixin,
                      JsonRequestResponseMixin,
                      View):
    def post(self, request):
        for id, order in self.request_json.items():
            Post.objects.filter(id=id,
                                  owner=request.user).update(order=order)
        return self.render_json_object_response({'saved': 'OK'})









class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        qs = super(ManageCourseListView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class AllCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/all_list.html'





class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/student_course_detail.html'

    def get_queryset(self):
        qs = super(StudentCourseDetailView, self).get_queryset()
        return qs

    def get_context_data(self, **kwargs):
        context = super(StudentCourseDetailView,
                        self).get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                id=self.kwargs['module_id'])
        else:
            # get first module
            context['module'] = course.modules.all()[0]
        return context



class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None


    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super(CourseModuleUpdateView,
                     self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                       'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})














class ManagePostListView(ListView):
    model = Post
    template_name = 'posts/manage/post/list.html'

    def get_queryset(self):
        qs = super(ManagePostListView, self).get_queryset()
        return qs.filter(owner=self.request.user)
'''
