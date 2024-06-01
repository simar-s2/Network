import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


from .models import User, Post, Comment


@login_required(login_url="/login")
def index(request):
    return render(request, "network/index.html")


@login_required(login_url="/login")
def get_all_posts(request):
    posts = Post.objects.all()
    posts = posts.order_by('-created_at')
    return JsonResponse([post.serialize() for post in posts], safe=False)

@csrf_exempt
@login_required(login_url="/login")
def create_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    try:
        data = json.loads(request.body)
        title = data.get("title")
        content = data.get("content")
        if not title or not content:
            return JsonResponse({"error": "Title and content are required."}, status=400)

        post = Post(title=title, content=content, author=request.user)
        post.save()
        return JsonResponse({"message": "Post created successfully."}, status=201)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except IntegrityError:
        return JsonResponse({"error": "Error creating post."}, status=500)
        

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
