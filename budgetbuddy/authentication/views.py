from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from .serializers import RegisterSerializer, LoginSerializer
from .forms import CustomUserCreationForm

User = get_user_model()

# -------------------------
# ✅ API Views (Django REST Framework)
# -------------------------

class RegisterAPIView(generics.CreateAPIView):
    """API View for User Registration"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginAPIView(APIView):
    """API View for User Login"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """API View for User Logout"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


# -------------------------
# ✅ Function-Based API Views (Alternative)
# -------------------------

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_api_view(request):
    """Function-based API View for User Login"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_api_view(request):
    """Function-based API View for User Logout"""
    request.user.auth_token.delete()
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


# -------------------------
# ✅ Web-Based Views (Django Templates)
# -------------------------

def register_view(request):
    """Handles user registration via web form"""
    form = CustomUserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)  # Auto-login after registration
        messages.success(request, "🎉 Registration successful! Redirecting to dashboard...")
        return redirect("dashboard")
    
    return render(request, "authentication/register.html", {"form": form})


def login_view(request):
    """Handles user login via web form"""
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "✅ Login successful! Redirecting to dashboard...")
        return redirect("dashboard")

    messages.error(request, "⚠️ Invalid username or password. Please try again.")
    return render(request, "authentication/login.html", {"form": form})


def logout_view(request):
    """Handles user logout via web form"""
    if request.method == "POST":
        logout(request)
        messages.success(request, "👋 You have been logged out.")
        return redirect("login")
    return render(request, "authentication/logout.html")


# -------------------------
# ✅ User Profile & Settings
# -------------------------

@login_required
def user_settings(request):
    """Allows users to update their profile and change their password"""
    profile_form = UserChangeForm(request.POST or None, instance=request.user)
    password_form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST":
        if "update_profile" in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect("user_settings")

        elif "update_password" in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "🔑 Password changed successfully!")
            return redirect("user_settings")

    return render(request, "authentication/user_settings.html", {
        "profile_form": profile_form,
        "password_form": password_form,
    })
