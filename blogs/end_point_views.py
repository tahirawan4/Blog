from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import redirect
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from blogs.serializers import UserSerializer, LoginSerializer, PostSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from blogs.models import Blog, Post
from blogs.serializers import BlogSerializer, PostSerializer
from rest_framework.response import Response


class UserRegisterView(APIView):
    serializer_class = UserSerializer

    def get(self, request, format=None):
        users = UserSerializer()
        return Response(users.data)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

        # return Response(content)


class UserLoginView(APIView):
    serializer_class = LoginSerializer

    def auth_user(self, request, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return True

        else:
            return False

    def get(self, request, format=None):
        users = LoginSerializer()
        return Response(users.data)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.POST)
        if serializer.is_valid():
            status = self.auth_user(request, serializer.validated_data['username'],
                                    serializer.validated_data['password'])
            if status:
                return Response(serializer.data)
        return Response(serializer.errors)


class UserProfileView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'registration.html'
    serializer_class = UserSerializer

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        users = UserSerializer(request.user)
        return Response({'serializer': users})

    def put(self, request, format=None):
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect('login')
        return Response(serializer.errors)

    def delete(self, request, format=None):
        user = request.user
        User.objects.filter(id=user.id).delete()
        return Response("successfully removed")


class PostListView(APIView):
    serializer_class = PostSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        # categories = utils.get_all_visible_categories()
        cat_slug = request.GET.get('cat', None)
        sort = request.GET.get('sort', None)
        # auth = request.user.is_authenticated()
        posts = Post.objects.filter(is_published=True).order_by('-posted_at')
        if cat_slug:
            posts = posts.filter(category__slug=cat_slug)
        if sort:
            if sort == 'posted_at':
                sort = "-" + sort
            posts = posts.order_by(sort)

        posts = PostSerializer(posts, many=True).data
        return Response(posts)


class AddPostView(APIView):
    serializer_class = PostSerializer
    parser_classes = (MultiPartParser, FormParser,)

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        post = PostSerializer(Post.objects.all(), many=True).data
        return Response(post)

    def post(self, request, format=None):
        post = PostSerializer(data=request.data,
                              context={'user_id': request.user.id, 'request': request,
                                       'category': request.POST.getlist('category')})
        if post.is_valid():
            post.save()
            return Response(post.data)
        return Response(post.errors)


class PostDetails(APIView):
    serializer_class = PostSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_object(self, slug):
        try:
            return Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, slug):
        post = PostSerializer(self.get_object(slug), many=False,
                              context={'request': request, 'user_id': request.user.id}).data
        return Response(post)


class UpdateDeletePost(APIView):
    serializer_class = PostSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_object(self, slug):
        try:
            return Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        post_data = self.get_object(slug)
        post = PostSerializer(post_data, many=False, context={'request': request})
        return Response(post.data)

    def post(self, request, slug, format=None):
        post_data = self.get_object(slug)
        post = PostSerializer(post_data, data=request.POST,
                              context={'user_id': request.user.id, 'request': request,
                                       'category': request.POST.getlist('category')})
        if post.is_valid():
            post.save()
        return Response(post.data)

    def delete_post(self, slug):
        post = self.get_object(slug)
        post.delete()


class LogOutView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class = PostSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        logout(request)
        return redirect('post_list')


class BlogListView(APIView):
    serializer_class = BlogSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        blogs = BlogSerializer(Blog.objects.all(), many=True).data
        return Response(blogs)


class BlogPostListView(APIView):
    serializer_class = PostSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get(self, request, username, format=None):
        cat_slug = request.GET.get('cat', None)
        sort = request.GET.get('sort', None)
        posts = Post.objects.filter(is_published=True, blog__author__username=username)
        if cat_slug:
            posts = posts.filter(category__slug=cat_slug)
        if sort:
            posts = posts.order_by(sort)
        posts = PostSerializer(posts, many=True).data
        return Response(posts)
