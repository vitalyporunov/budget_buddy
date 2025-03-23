from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes

from .serializers import RegisterSerializer, LoginSerializer
from .forms import CustomUserCreationForm, UserSettingsForm

User = get_user_model()

# -------------------------
# 🔐 API Views (Class-Based)
# -------------------------

class RegisterAPIView(generics.CreateAPIView):
    """DRF API View to register a new user"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginAPIView(APIView):
    """DRF API View to login a user"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"]
            )
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """DRF API View to logout a user"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

# -------------------------
# 🧩 API Views (Function-Based)
# -------------------------

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_api_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"]
        )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_api_view(request):
    request.user.auth_token.delete()
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

# -------------------------
# 🖥️ Web Views (Templates)
# -------------------------

def register_view(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Redirecting to dashboard...")
            return redirect("dashboard")
        messages.error(request, "Registration failed. Please fix the errors below.")
    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Login successful! Redirecting to dashboard...")
        return redirect("dashboard")
    elif request.method == "POST":
        messages.error(request, "Invalid username or password.")
    return render(request, "authentication/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return render(request, "authentication/logout.html")

# -------------------------
# ⚙️ User Settings (Profile & Password)
# -------------------------

@login_required
def user_settings(request):
    profile_form = UserSettingsForm(request.POST or None, instance=request.user)
    password_form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == 'POST':
        if 'update_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('user_settings')

        elif 'update_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect('user_settings')

    return render(request, 'authentication/user_settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })
