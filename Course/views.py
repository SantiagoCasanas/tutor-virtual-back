from Course.utils import ask_open_ai, validate_context
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, FavoriteCourse
from .permissions import IsCoursePermission, IsYourOwnIdInstructor, IsYourOwnIdStudent
from .serializers import AddFavoriteCourseSerializer, CourseCreateSerializer, CourseListSerializer, CourseUpdateSerializer, DeleteFavoriteCourseSerializer, QuestionSerializer, ListFavoriteCourseSerializer


class List(generics.ListAPIView):
    """
    List all courses. (for students)
    """
    queryset = Course.objects.filter(active=True)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseListSerializer


class ListOwnCourse(generics.ListAPIView):
    """
    List courses owned by the authenticated user. (for instructors)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseListSerializer

    def get_queryset(self):
        instructor_pk = self.request.user.id
        return Course.objects.filter(instructor__id=instructor_pk, active=True)


class Create(generics.CreateAPIView):
    """
    Create a new course. (for instructors)
    """
    permission_classes = [permissions.IsAuthenticated, IsYourOwnIdInstructor]
    serializer_class = CourseCreateSerializer


class Modify(generics.UpdateAPIView):
    """
    Update a course. (for instructors)
    """
    queryset = Course.objects.filter(active= True)
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated, IsCoursePermission]
    serializer_class = CourseUpdateSerializer


class DeleteCourseView(generics.GenericAPIView):
    queryset = Course.objects.filter(active=True)
    permission_classes = [permissions.IsAuthenticated, IsCoursePermission]
    lookup_field = 'pk'
    serializer_class = CourseCreateSerializer

    def post(self, request, *args, **kwargs):
        """
        Change the activation status of a Course object and return the serialized response.
        If the course is deactivated, also disappears from favorite courses
        """
        instance = self.get_object()
        new_value = instance.active
        instance.active = not new_value
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddCourseFavoriteView(generics.CreateAPIView):
    """
    Add course to favorites. (for students)
    """
    permission_classes = [permissions.IsAuthenticated, IsYourOwnIdStudent]
    serializer_class = AddFavoriteCourseSerializer


class DeleteFavoriteCourseView(generics.GenericAPIView):
    """
    Delete course from favorites. (for students)
    """
    permission_classes = [permissions.IsAuthenticated, IsYourOwnIdStudent]
    serializer_class = DeleteFavoriteCourseSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student = serializer.validated_data['student']
            course = serializer.validated_data['course']
            serializer.deactivate_favorite_course(student, course)
            return Response({'status': 'Favorite course deactivated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListFavoriteCourseView(generics.ListAPIView):
    """
    List favorite courses of student
    """
    def get_queryset(self):
        """
        Customize queryset for retrieve only active and favorite courses of the authenticated user
        """
        user = self.request.user
        return FavoriteCourse.objects.filter(student=user,course__active=True,active=True)
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListFavoriteCourseSerializer

class Chat(APIView):
    """
    Chat with the OpenAI model. (for students)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuestionSerializer

    def post(self, request, pk):
        """
        Handle POST requests to chat with the OpenAI model.

        Args:
            request: The HTTP request object.
            pk (int): The primary key of the course.

        Returns:
            Response: The model's response to the question.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data.get('content')
            if validate_context(question):
                context = Course.get_context(pk)
                answer = ask_open_ai(context, question)
                return Response({'answer': answer})
            else:
                return Response({'error': 'Invalid question'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
