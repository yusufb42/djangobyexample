from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


# Create your views here.
class PostListView(ListView):
    """
    Alternative post list view
    """

    queryset = Post.published.all()  # or `model = Post` -> would use Post.objects.all()
    context_object_name = "posts"  # by default would return `object_list`
    paginate_by = 3  # three objects per page
    template_name = "blog/post/list.html"  # default would be "blog/post_list.html"


# def post_list(request):
#     posts_list = Post.published.all()
#     # Pagination with 3 posts per page
#     paginator = Paginator(posts_list, 3)
#     page_number = request.GET.get(
#         "page", 1
#     )  # if page parameter is not in the GET parameters, then the default page number is 1

#     try:
#         posts = paginator.page(page_number)
#     except PageNotAnInteger:
#         # if page_number is not an integer deliver the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # if page_number is out of range deliver last page of results.
#         posts = paginator.page(paginator.num_pages)

#     return render(request, "blog/post/list.html", {"posts": posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    # list of active comments for this post
    comments = post.comments.filter(active=True)
    # form for users to comment
    form = CommentForm()

    return render(
        request,
        "blog/post/detail.html",
        {"post": post, "comments": comments, "form": form},
    )


# def post_detail(request, id):
#     # try:
#     #     post = Post.published.get(id=id)
#     # except Post.DoesNotExist:
#     #     raise Http404("No Post found.")
#     post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)

#     return render(request, "blog/post/detail.html", {"post": post})


def post_share(request, post_id):
    # retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # form fields passed validation
            cd = form.cleaned_data

            # send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, "a@yusuf.rocks", [cd["to"]])
            sent = True

    else:
        form = EmailPostForm()

    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    # a comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # create a Comment object without saving it to the database
        comment = form.save(commit=False)

        # assign the post to the comment
        comment.post = post

        # save the comment to the database
        comment.save()

    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )