from rest_framework import serializers
from Users.models import User
from .models import Course, FavoriteCourse


class BaseCourseSerializer(serializers.ModelSerializer):
    """
    Base serializer for course with common validation.
    """

    def validate_instructor(self, value):
        """
        Validate that the instructor is a professor.

        Args:
            value (User): The instructor.

        Returns:
            User: The validated instructor.

        Raises:
            serializers.ValidationError: If the instructor does not exist or is not a professor.
        """
        try:
            if value.rol != "Profesor":
                raise serializers.ValidationError('Only professors can create courses.')
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist.')
        return value


class CourseCreateSerializer(BaseCourseSerializer):
    """
    Serializer for creating a new course.
    """
    class Meta:
        model = Course
        fields = '__all__'
        extra_kwargs = {
            "name": {"required": True},
            "instructor": {"required": True},
            "description": {"required": True},
            "context": {"required": True},
            "creation_date": {"required": False}
        }

    def create(self, validated_data):
        """
        Create a new course instance.

        Args:
            validated_data (dict): Validated data for the new course.

        Returns:
            Course: The created course instance.
        """
        course = Course(**validated_data)
        course.save()
        return course


class CourseUpdateSerializer(BaseCourseSerializer):
    """
    Serializer for updating a course.
    """
    class Meta:
        model = Course
        fields = ["name", "description", "context", "active"]


class QuestionSerializer(serializers.Serializer):
    """
    Serializer for questions.
    """
    content = serializers.CharField(max_length=200)


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing courses.
    """
    instructor = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
    
    def get_instructor(self, obj):
        """
        Get the full name of the course instructor.

        Args:
            obj (Course): The course instance.

        Returns:
            str: The full name of the instructor.
        """
        return f"{obj.instructor.first_name} {obj.instructor.last_name}"


class BaseFavoriteCourseSerializer(serializers.ModelSerializer):
    """
    Base serializer for FavoriteCourse with common validation.
    """
    class Meta:
        model = FavoriteCourse
        fields = "__all__"
        extra_kwargs = {
                "student": {"required": True},
                "course": {"required": True},
                "active": {"required": False}
            }
        
    def validate_student(self, value):
        """
        Validate that the user is a student.

        Args:
            value (User): The student.

        Returns:
            User: The validated user.

        Raises:
            serializers.ValidationError: If the user does not exist or is not a student.
        """
        try:
            if value.rol != "Estudiante":
                raise serializers.ValidationError('Only students can add courses to favorite courses.')
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist.')
        return value

    def validate_course(self, value):
        """
        Validate that the course is active.

        Args:
            value (Course): The course.

        Returns:
            User: The validated course.

        Raises:
            serializers.ValidationError: If the course is not active.
        """
        try:
            if value.active == False:
                raise serializers.ValidationError('The course is not active')
        except User.DoesNotExist:
            raise serializers.ValidationError('User course not exist.')
        return value


class AddFavoriteCourseSerializer(BaseFavoriteCourseSerializer):
    """
    Serializer for adding a course to favorite courses.
    """
    def create(self, validated_data):
        student = validated_data.get("student")
        course = validated_data.get("course")
        favorite = FavoriteCourse.create(student=student, course=course)
        return favorite


class DeleteFavoriteCourseSerializer(BaseFavoriteCourseSerializer):
    """
    Serializer for deleting a course from favorite courses.
    """
    def deactivate_favorite_course(self, student, course):
        """
        Deactivate a favorite course by setting its 'active' field to False.

        Args:
            student (User): The student.
            course (Course): The course.

        Returns:
            FavoriteCourse: The updated FavoriteCourse instance or None if not found.

        Raises:
            serializers.ValidationError: If the FavoriteCourse does not exist.
        """
        try:
            favorite_course = FavoriteCourse.objects.get(student=student, course=course)
            favorite_course.active = False
            favorite_course.save()
            return favorite_course
        except FavoriteCourse.DoesNotExist:
            raise serializers.ValidationError('FavoriteCourse does not exist.')


class ListFavoriteCourseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source = 'course.name', read_only=True)
    instructor = serializers.CharField(source = 'course.instructor', read_only=True)
    description = serializers.CharField(source = 'course.description', read_only=True)

    class Meta:
        model = FavoriteCourse
        fields = ["student","course","name","instructor", "description", "active"]
