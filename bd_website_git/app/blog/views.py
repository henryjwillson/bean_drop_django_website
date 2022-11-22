from .models import Post
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
# Used to add logged in requirements to class based views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContactForm


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'    # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']     # ordering of posts
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'    # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('date_posted')


class PostDetailView(DetailView):
    model = Post


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        else:
            return False


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'header_image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        else:
            return False


def contactView(request):
    if request.method == "GET":
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            from_email = form.cleaned_data["from_email"]
            message = form.cleaned_data['message']
            try:
                email = EmailMessage(
                    subject,
                    message,
                    from_email,
                    [from_email, 'beandrop.company@gmail.com'],
                    reply_to=[from_email],
                )
                email.send()
                #send_mail(subject, message, from_email, ["beandrop.coompany@gmail.com"])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            messages.success(
                request,  'Thank you for contacting us, we will respond as soon as possible.')
            return redirect('blog-home')
    return render(request, "blog/contact_us.html", {'form': form})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'header_image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        else:
            return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


def charity(request):
    return render(request, 'blog/charity.html', {'title': 'Charity'})


def private_policy(request):
    return render(request, 'blog/private_policy.html', {'title': 'private_policy'})

def the_bean_drop_team(request):
    return render(request, 'blog/the_bean_drop_team.html', {'title': 'the-bean-drop-team'})

def faqs(request):
    return render(request, 'blog/faqs.html', {'title': 'faqs'})

def locations(request):
    return render(request, 'blog/locations.html', {'title': 'locations'})
# Create your views here.
