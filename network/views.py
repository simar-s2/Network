import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse


from .models import User, Post, Comment, Like


@login_required(login_url="/login")
def index(request):
    # Retrieve and serialize all posts in descending order
    posts = [post.serialize() for post in Post.objects.order_by('-timestamp')]
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
    try:
        user = User.objects.get(username=username)
        if user is None:
            return JsonResponse({"error": "User not found."}, status=404)
        user_items = user.serialize()
        return JsonResponse(user_items, safe=False)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except Exception:
        return JsonResponse({"error": "Internal server error."}, status=500)


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
