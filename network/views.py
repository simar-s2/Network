import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.core.paginator import Paginator


from .models import User, Post, Comment, Like


def index(request):
    # Retrieve and serialize all posts in descending order
    posts = Post.objects.order_by('-timestamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "posts": posts
    })


@login_required(login_url="/login")
def create_post(request):
    """
    Create a new post.
    """
    # Check if the request method is POST
    if request.method == "POST":
        try:
            # Get data from the form submitted
            title = request.POST.get("title")
            content = request.POST.get("content")

            # Check if title and content are provided
            if not title or not content:
                # Display an error message and redirect to index
                messages.error(request, "Title and content are required.")
                return HttpResponseRedirect(reverse("index"))

            # Create a new post with the provided data and current user
            post = Post(title=title, content=content, user_id=request.user)
            post.save()

            # Display a success message and redirect to index
            messages.success(request, "Post created successfully.")
            return HttpResponseRedirect(reverse("index"))
        except (ValueError, IntegrityError):
            # Display an error message and redirect to index
            messages.error(request, "Error creating post.")
            return HttpResponseRedirect(reverse("index"))


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    followers = user_profile.followers.all()
    following = user_profile.followed_by.all()
    posts = Post.objects.filter(user_id=user_profile.id).order_by('-timestamp')
    current_user = request.user

    return render(request, "network/profile.html", {
        "user_profile": user_profile,
        "user": current_user,
        "followers": followers,
        "following": following,
        "posts": posts
    })


def follow(request, username):
    if request.method == "POST":
        current_user = request.user
        user_profile = get_object_or_404(User, username=username)
        if current_user == user_profile: return JsonResponse({"success": False})
        elif current_user in user_profile.followers.all():
            user_profile.followers.remove(current_user)
        else:
            user_profile.followers.add(current_user)
        return JsonResponse({"follower_count": user_profile.followers.count()})


def following(request):
    try:
        current_user = request.user
        followings = current_user.followed_by.all()
        posts = []
        for following in followings:
            posts += list(following.posts_by_user.all())
            print(posts[1].user_id)
        posts = sorted(posts, key=lambda x: x.timestamp, reverse=True)

        return render(request, "network/following.html", {
            "posts": posts
        })
    except AttributeError:
        # If current_user is None or doesn't have followed_by attribute
        return render(request, "network/following.html", {
            "posts": []
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

