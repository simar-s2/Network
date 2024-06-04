import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


from .models import User, Post, Comment, Like


@login_required(login_url="/login")
def index(request):
    # Retrieve and serialize all posts in descending order
    posts = [post.serialize() for post in Post.objects.order_by('-timestamp')]
    return render(request, "network/index.html", {
        "posts": posts
    })


@csrf_exempt
@login_required(login_url="/login")
def create_post(request):
    """
    Create a new post.
    Requires a POST request with a JSON body containing 'title' and 'content' keys.
    """
    if request.method != "POST":
        # Return error if request method is not POST
        return JsonResponse({"error": "POST required."}, status=400)

    try:
        # Parse JSON request body
        data = json.loads(request.body)
        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            # Return error if title or content is missing
            return JsonResponse({"error": "Title and content required."}, status=400)

        # Create new post with provided title, content, and user ID
        post = Post(title=title, content=content, user_id=request.user)
        post.save()

        # Return success message
        return JsonResponse({"message": "Post created."}, status=201)
    except (ValueError, IntegrityError):
        # Return error if JSON parsing or post creation fails
        return JsonResponse({"error": "Error creating post."}, status=500)


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
