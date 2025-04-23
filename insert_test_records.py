# flake8: noqa: E402

import os

import django

# Set the environment variable for Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app_config.settings")

# Now set up Django
django.setup()

# get user model function import
from django.contrib.auth import get_user_model

# Import your models after setting up Django
from blog.models import BlogPost

User = get_user_model()

owner = User.objects.get(username="shailesh")

test_records = [
    {
        "title": "How to Learn Django in 30 Days",
        "content": "This is a beginner-friendly guide to mastering Django in 30 days.",
        "status": "published",
    },
    {
        "title": "Why Python is the Best Language for Web Development",
        "content": "Python's simplicity and readability make it ideal for web development.",
        "status": "published",
    },
    {
        "title": "Understanding Django ORM with Practical Examples",
        "content": "In this post, we dive into Django ORM's power with real examples.",
        "status": "draft",
    },
    {
        "title": "10 Tips for Writing Clean Django Code",
        "content": "These tips will help you write maintainable and readable Django code.",
        "status": "published",
    },
    {
        "title": "Deploying Django Apps with Docker",
        "content": "Learn how to containerize and deploy Django apps using Docker.",
        "status": "draft",
    },
]
for record in test_records:
    BlogPost.objects.create(owner=owner, **record)

print("Test records added successfully!")
