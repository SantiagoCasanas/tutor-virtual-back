from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from Users.models import User
from .models import Course

class CourseAPITestCase(APITestCase):
    def setUp(self):
        self.refresh_token_user_url = reverse('token_refresh')
        self.login_user_url = reverse('login')

        # Crear usuarios para pruebas
        self.student_user = User.objects.create_user(
            first_name='student',
            last_name='test',
            email='student@gmail.com',
            password='password',
            rol='Estudiante'
        )
        self.instructor_user = User.objects.create_user(
            first_name='instructor',
            last_name='test',
            email='instructor@gmail.com',
            password='password',
            rol='Profesor'
        )
        self.course = Course.objects.create(
            name='Test Course',
            instructor=self.instructor_user,
            description='A test course',
            context='Test context'
        )

    #obtener nuevos token de accesso y refresco para extender la sesión del usuario
    def test_user_refresh_token_POST(self):
        refresh = RefreshToken.for_user(self.student_user)
        refresh_token = {
            'refresh': f'{refresh}',
        }
        response = self.client.post(self.refresh_token_user_url, refresh_token)
        self.assertEqual(response.status_code,200)
    
    #autenticar usuarios para testear los servicios que requieren autenticación del usuario
    def authenticate_user(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_courses(self):
        self.authenticate_user(self.student_user)
        url = reverse('student_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_own_courses(self):
        self.authenticate_user(self.instructor_user)
        url = reverse('instructor_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_course(self):
        self.authenticate_user(self.instructor_user)
        url = reverse('instructor_modify', args=[self.course.pk])
        data = {
            'name': 'Updated Course',
            'description': 'Updated description',
            'context': 'Updated context',
            'active': True
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_chat_with_model(self):
        self.authenticate_user(self.student_user)
        url = reverse('chat', args=[self.course.pk])
        data = {
            'content': 'What is the context?'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('answer', response.data)
