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
    # Render the index.html template with the network/index.html template path.
    return render(request, "network/index.html")


@login_required(login_url="/login")
def get_all_posts(request):
    # Retrieve all posts and order them by the created_at field in descending order
    posts = Post.objects.order_by('-timestamp')
    
    # Serialize each post into a dictionary and return them as a JSON response
    return JsonResponse([post.serialize() for post in posts], safe=False)


@csrf_exempt
@login_required(login_url="/login")
def create_post(request):
    # Check if the request method is POST
    if request.method != "POST":
        # Return error response if the request method is not POST
        return JsonResponse({"error": "POST request required."}, status=400)

    try:
        # Parse the request body as JSON
        data = json.loads(request.body)

        # Retrieve the title and content fields from the request body
        title = data.get("title")
        content = data.get("content")

        # Check if the title and content fields are present in the request body
        if not title or not content:
            # Return error response if the title or content fields are missing
            return JsonResponse({"error": "Title and content are required."}, status=400)

        # Create a new Post object with the given title, content, and author
        post = Post(title=title, content=content, author=request.user)
        post.save()

        # Return success response if the post is created successfully
        return JsonResponse({"message": "Post created successfully."}, status=201)
    except ValueError:
        # Return error response if the request body is not valid JSON
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except IntegrityError:
        # Return error response if there was an error creating the post
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
