from django.test import TestCase, SimpleTestCase
from rest_framework.test import APITestCase
from django.urls import reverse, resolve
from Users.views import MyTokenObtainPairView, Create, Update, UpdatePassword, RetrieveUserInfo
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView
)
from Users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import json
import random
# Create your tests here.
pk = random.randint(1,2)

class TestUrls(SimpleTestCase):
    """
    Tests de urls de los endpoints, verifica que todas las urls nos devuelvan la view correspondiente
    """
    def test_create_url(self):
        url = reverse('create')
        self.assertEqual(resolve(url).func.view_class, Create)

    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, MyTokenObtainPairView)

    def test_logout_url(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func.view_class, TokenBlacklistView)

    def test_token_refresh_url(self):
        url = reverse('token_refresh')
        self.assertEqual(resolve(url).func.view_class, TokenRefreshView)

    def test_update_url(self):
        url = reverse('update', args=[f'{pk}'])
        self.assertEqual(resolve(url).func.view_class, Update)

    def test_update_password_url(self):
        url = reverse('update_password', args=[f'{pk}'])
        self.assertEqual(resolve(url).func.view_class, UpdatePassword)
    
    def test_retirve_info_url(self):
        url = reverse('retrieve_user_info', args=[f'{pk}'])
        self.assertEqual(resolve(url).func.view_class, RetrieveUserInfo)

class TestViews(APITestCase):
    """
    Tests de las views de los endpoints, verifica que todas las views respondan de manera exitosa basado en el statud_code
    """
    def setUp(self):
        #urls para los servicios que no requieren parámetros en la url
        self.create_url = reverse('create')
        self.login_user_url = reverse('login')
        self.logout_user_url = reverse('logout')
        self.refresh_token_user_url = reverse('token_refresh')
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

        #urls para los servicios que sí requieren parámteros
        self.retrieve_info_student_url = reverse('retrieve_user_info', args=[f'{self.student_user.id}'])
        self.retrieve_info_instructor_url = reverse('retrieve_user_info', args=[f'{self.instructor_user.id}'])

        self.update_student_user_url = reverse('update', args=[f'{self.student_user.id}'])
        self.update_instructor_user_url = reverse('update', args=[f'{self.instructor_user.id}'])

        self.update_student_password_url = reverse('update_password', args=[f'{self.student_user.id}'])
        self.update_instructor_password_url = reverse('update_password', args=[f'{self.instructor_user.id}'])
    
    #creación de usuario con rol de estudiante
    def test_student_create_POST(self):
        user_info = {
            'first_name':'student',
            'last_name':'test',
            'email':'student2@gmail.com',
            'password':'password',
            'rol':'Estudiante',
        }
        response = self.client.post(self.create_url, user_info)
        self.assertEqual(response.status_code,201)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['first_name'],'student')
        self.assertEqual(response_data['last_name'],'test')
        self.assertEqual(response_data['email'],'student2@gmail.com')
        self.assertEqual(response_data['rol'],'Estudiante')
    
    #creación de usuario con rol de Profesor
    def test_student_create_POST(self):
        user_info = {
            'first_name':'instructor',
            'last_name':'test',
            'email':'instructor2@gmail.com',
            'password':'password',
            'rol':'Profesor'
        }
        response = self.client.post(self.create_url, user_info)
        self.assertEqual(response.status_code,201)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['first_name'],'instructor')
        self.assertEqual(response_data['last_name'],'test')
        self.assertEqual(response_data['email'],'instructor2@gmail.com')
        self.assertEqual(response_data['rol'],'Profesor')
    
    #login de usuario
    def test_user_login_POST(self):
        user_info = {
            'email':'instructor@gmail.com',
            'password':'password',
        }
        response = self.client.post(self.login_user_url, user_info)
        self.assertEqual(response.status_code,200)

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

    #obtener información usuario con rol de estudiante
    def test_student_info_GET(self):
        self.authenticate_user(self.student_user)
        response = self.client.get(self.retrieve_info_student_url)
        self.assertEqual(response.status_code,200)
    
    #obtener información usuario con rol de profesor
    def test_instructor_info_GET(self):
        self.authenticate_user(self.instructor_user)
        response = self.client.get(self.retrieve_info_instructor_url)
        self.assertEqual(response.status_code,200)

    #actualizar información usuario con rol de profesor
    def test_update_instructor_info_POST(self):
        new_user_info = {
            'first_name':'instructor',
            'last_name':'test',
            'email':'instructorTest@gmail.com',
        }
        self.authenticate_user(self.instructor_user)
        response = self.client.put(self.update_instructor_user_url, new_user_info)
        self.assertEqual(response.status_code,200)

    #actualizar información usuario con rol de estudiante
    def test_update_student_info_POST(self):
        new_user_info = {
            'first_name':'student',
            'last_name':'test',
            'email':'studentTest@gmail.com',
        }
        self.authenticate_user(self.student_user)
        response = self.client.put(self.update_student_user_url, new_user_info)
        self.assertEqual(response.status_code,200)

    #actualizar contraseña usuario con rol de profesor
    def test_update_instructor_password_POST(self):
        new_user_password = {
            'current_password': 'password',
            'new_password': 'instructortestpassword',
            'confirm_new_password': 'instructortestpassword'
        }
        self.authenticate_user(self.instructor_user)
        response = self.client.put(self.update_instructor_password_url, new_user_password)
        self.assertEqual(response.status_code,200)
    
    #actualizar contraseña usuario con rol de estudiante
    def test_update_student_password_POST(self):
        new_user_password = {
            'current_password': 'password',
            'new_password': 'studenttestpassword',
            'confirm_new_password': 'studenttestpassword'
        }
        self.authenticate_user(self.student_user)
        response = self.client.put(self.update_student_password_url, new_user_password)
        self.assertEqual(response.status_code,200)

    #cerrar sesión del usuario
    def test_user_logout_POST(self):
        refresh = RefreshToken.for_user(self.student_user)
        refresh_token = {
            'refresh': f'{refresh}',
        }
        response = self.client.post(self.logout_user_url, refresh_token)
        self.assertEqual(response.status_code,200)