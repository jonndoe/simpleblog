from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm, \
                   CustomUserChangeForm, ProfileEditForm, UserEditForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . models import Profile

from django.contrib import messages

from django.shortcuts import get_object_or_404
from app_users.models import CustomUser

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from .models import Contact

from app_actions.utils import create_action
from app_actions.models import Action

from app_posts.models import Post


'''
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
'''


def signup(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password1'])
            # Save the User object
            new_user.save()
            # Create the user profile
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')

            return render(request,
                          'registration/signup_done.html',
                          {'new_user': new_user})
    else:
        user_form = CustomUserCreationForm()
    return render(request,
                  'signup.html',
                  {'user_form': user_form})


@login_required
def dashboard(request):
    # Display all actions by default
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',
                                                       flat=True)
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]

    return render(request,
                  'registration/dashboard.html',
                  {'section': 'dashboard',
                   'actions': actions})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                         data=request.POST)
        profile_form = ProfileEditForm(
                       instance=request.user.profile,
                       data=request.POST,
                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            new_photo = profile_form.save(commit=False)
            if profile_form.cleaned_data['photo'] == False:
                new_photo.photo = 'no_image.png'
            new_photo.save()

            messages.success(request, 'Profile updated successfully')
            return render(request,
                          'registration/dashboard.html',
                          {'section': 'dashboard'}, )
        else:
            messages.error(request, 'Error updating your profile')
            return render(request,
                          'registration/dashboard.html',
                          {'section': 'dashboard'}, )

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

        return render(request,
                  'registration/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


@login_required
def user_list(request):
    users = CustomUser.objects.filter(is_active=True)

    print(users)

    return render(request,
                  'registration/user/list.html',
                  {'section': 'people',
                   'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(CustomUser,
                             username=username,
                             is_active=True)
    return render(request,
                  'registration/user/detail.html',
                  {'section': 'people',
                   'user': user})


@login_required
def posts_of_user(request, id):
    user = get_object_or_404(CustomUser,
                             id=id,
                             is_active=True)

    user_posts = Post.objects.filter(owner=user.id)
    #assert False
    return  render(request,
                   'registration/user/detail.html',
                   {'section': 'people',
                    'user': user,
                    'user_posts': user_posts})



@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = CustomUser.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'ko'})
    return JsonResponse({'status': 'ko'})
