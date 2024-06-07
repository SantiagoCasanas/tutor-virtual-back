from django.db import models
from Users.models import User


def validate_context(value):
    """
    Validate the context of a course.

    Args:
        value (str): The context to validate.

    Returns:
        bool: True if the context is valid, False otherwise.
    """
    words = value.split()
    return len(words) <= 130


class Course(models.Model):
    """
    Model representing a course.
    """
    name = models.CharField(max_length=100, verbose_name="Title for your course")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    description = models.CharField(max_length=200, verbose_name="Write a quick description of your course")
    context = models.TextField(
        verbose_name="Write the topics, context, and a large description for your course",
    )
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Creation date")
    active = models.BooleanField(null=False, default=True)

    class Meta:
        ordering = ['name']

    @staticmethod
    def get_by_id(course_id):
        """
        Get a course by its ID.

        Args:
            course_id (int): The ID of the course.

        Returns:
            Course: The course with the specified ID, or None if not found.
        """
        return Course.objects.filter(pk=course_id).first()

    @staticmethod
    def get_context(course_id):
        """
        Get the context of a course by its ID.

        Args:
            course_id (int): The ID of the course.

        Returns:
            str: The context of the course.
        """
        course = Course.get_by_id(course_id)
        if course is None:
            return "Without context"
        else:
            return f'{course.name}: {course.context}'

    @staticmethod
    def create(name, description, context):
        """
        Create a new course.

        Args:
            name (str): The name of the course.
            description (str): A description of the course.
            context (str): The context of the course.

        Returns:
            Course: The created course instance, or None if validation fails.
        """
        if validate_context(context):
            course = Course.objects.create(name=name, description=description, context=context)
            return course
        return None


class FavoriteCourse(models.Model):
    """
    Model representing a favorite course of a student.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=False, null=False)
    active = models.BooleanField(default=True, null=False)

    @staticmethod
    def create(student: User, course: Course, active=True):
        """
        Create a new FavoriteCourse entry or reactivate an existing one.

        Args:
            student (User): The student marking the course as favorite.
            course (Course): The course being marked as favorite.
            active (bool): The status of the favorite course entry.

        Returns:
            FavoriteCourse: The created or reactivated FavoriteCourse instance.
        """
        if not FavoriteCourse.exists(student=student, course=course):
            return FavoriteCourse.objects.create(student=student, course=course, active=active)
        else:
            favorite_course = FavoriteCourse.objects.filter(student=student, course=course).first()
            favorite_course.active = True
            favorite_course.save()
            return favorite_course

    @staticmethod
    def exists(student: User, course: Course):
        """
        Check if a FavoriteCourse entry exists for a given student and course.

        Args:
            student (User): The student to check.
            course (Course): The course to check.

        Returns:
            bool: True if the entry exists, False otherwise.
        """
        return FavoriteCourse.objects.filter(student=student, course=course).exists()
