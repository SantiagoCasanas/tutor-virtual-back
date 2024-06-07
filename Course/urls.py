from django.urls import path
from .views import *

urlpatterns = [
    path('instructor/create', Create.as_view(), name='instructor_register'),
    path('instructor/list', ListOwnCourse.as_view(), name='instructor_list'),
    path('instructor/modify/<int:pk>', Modify.as_view(), name='instructor_modify'),
    path('instructor/delete/<int:pk>', DeleteCourseView.as_view(), name='instructor_delete'),

    path('student/<int:pk>/chat', Chat.as_view(), name='chat'),
    path('student/list', List.as_view(), name='student_list'),
    path('student/course/favorites/add', AddCourseFavoriteView.as_view(), name='student_courses_favorites_add'),
    path('student/course/favorites/delete', DeleteFavoriteCourseView.as_view(), name='student_courses_favorites_delete'),
]