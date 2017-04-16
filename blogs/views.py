# from django.contrib.auth.models import User, Group
# from django.http import Http404
# from rest_framework import viewsets, status
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import redirect
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer

# from users.models import Task
# from users.serializers import UserSerializer, GroupSerializer, TaskSerializer
from blogs import utils
from blogs.models import Post, Category
from blogs.serializers import UserSerializer, LoginSerializer, PostSerializer


class UserRegisterView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'registration.html'
    serializer_class = UserSerializer

    # authentication_classes = (SessionAuthentication, BasicAuthentication)
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        users = UserSerializer()
        return Response({'serializer': users, 'user': False})

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect('login')
        return Response(serializer.errors)

        # return Response(content)


class UserLoginView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'login.html'
    serializer_class = LoginSerializer

    # authentication_classes = (SessionAuthentication, BasicAuthentication)
    # permission_classes = (IsAuthenticated,)

    def auth_user(self, request, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return True

        else:
            return False

    def get(self, request, format=None):
        auth = request.user.is_authenticated()
        users = LoginSerializer()
        return Response({'serializer': users, 'user': auth})

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.POST)
        if serializer.is_valid():
            status = self.auth_user(request, serializer.validated_data['username'],
                                    serializer.validated_data['password'])
            if status:
                return redirect('post_list')
        auth = request.user.is_authenticated()
        return Response({'serializer': serializer, 'user': auth})

        # return Response(content)


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
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'post_list.html'
    serializer_class = PostSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        categories = utils.get_all_visible_categories()
        cat_slug = request.GET.get('cat', None)
        sort = request.GET.get('sort', None)
        auth = request.user.is_authenticated()
        posts = Post.objects.filter(is_published=True)
        if cat_slug:
            posts = posts.filter(category__slug=cat_slug)
        if sort:
            posts = posts.order_by(sort)
        return Response({'posts': posts, 'user': auth, 'categories': categories, 'selected_cat': cat_slug,
                         'logged_in_user': request.user})


class AddPostView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'add_post.html'
    serializer_class = PostSerializer

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        post = PostSerializer()
        cats = Category.objects.all()

        return Response({'serializer': post, 'category': cats})

    def post(self, request, format=None):
        post = PostSerializer(data=request.POST, context={'user_id': request.user.id, 'request': request,
                                                          'category': request.POST.getlist('category')})
        if post.is_valid():
            post.save()
        return Response({'serializer': post})


class AddUpdateView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'add_post.html'
    serializer_class = PostSerializer

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        post = PostSerializer()
        cats = Category.objects.all()

        return Response({'serializer': post, 'category': cats})

        # def post(self, request):

    def post(self, request, format=None):
        post = PostSerializer(data=request.POST, context={'user_id': request.user.id, 'request': request,
                                                          'category': request.POST.getlist('category')})
        if post.is_valid():
            post.save()
        return Response({'serializer': post})


class PostDetails(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'post_details.html'
    serializer_class = PostSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    # noinspection PyMethodMayBeStatic
    def get_object(self, slug):
        try:
            return Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, slug):
        categories = utils.get_all_visible_categories()
        auth = request.user.is_authenticated()
        post = PostSerializer(self.get_object(slug), many=False,
                              context={'request': request, 'user_id': request.user.id}).data
        return Response({'post': post, 'user': auth, 'categories': categories})


class UpdateDeletePost(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'update_post.html'
    serializer_class = PostSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    # noinspection PyMethodMayBeStatic
    def get_object(self, slug):
        try:
            return Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        cats = Category.objects.all()
        post_data = self.get_object(slug)
        post = PostSerializer(post_data, many=False, context={'request': request})
        return Response({'serializer': post, 'category': cats, slug: slug, 'post': post_data})

    def post(self, request, slug, format=None):
        if request.POST.get('delete'):
            self.delete_post(slug)
            request
            redirect('post-list')
        else:
            cats = Category.objects.all()
            post_data = self.get_object(slug)
            post = PostSerializer(post_data, data=request.POST,
                                  context={'user_id': request.user.id, 'request': request,
                                           'category': request.POST.getlist('category')})
            if post.is_valid():
                post.save()
            return Response({'serializer': post, 'category': cats, slug: slug, 'post': post_data})

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
