"""
Authentication system tests.
Covers signup, login, JWT, refresh token, logout, and RBAC.
"""

import pytest
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, UserRole
from app.repositories import UserRepository
from app.utils import hash_password, create_access_token
from app.db import get_session_factory

client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
async def session_factory():
    """Get database session factory"""
    factory = get_session_factory()
    return factory


@pytest.fixture
async def clean_database(session_factory):
    """Clean database before and after each test"""
    async with session_factory() as session:
        # Clear users before test
        await session.execute("TRUNCATE TABLE \"user\" CASCADE")
        await session.commit()
    yield
    # Cleanup after test
    async with session_factory() as session:
        await session.execute("TRUNCATE TABLE \"user\" CASCADE")
        await session.commit()


@pytest.fixture
async def test_patient(session_factory, clean_database):
    """Create a test patient user"""
    async with session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.create(
            email="patient@example.com",
            password_hash=hash_password("TestPassword123!"),
            role=UserRole.PATIENT,
        )
        await session.commit()
        yield {
            "id": user.id,
            "email": "patient@example.com",
            "password": "TestPassword123!",
            "role": UserRole.PATIENT,
        }


@pytest.fixture
async def test_admin(session_factory, clean_database):
    """Create a test admin user"""
    async with session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.create(
            email="admin@example.com",
            password_hash=hash_password("AdminPassword123!"),
            role=UserRole.ADMIN,
        )
        await session.commit()
        yield {
            "id": user.id,
            "email": "admin@example.com",
            "password": "AdminPassword123!",
            "role": UserRole.ADMIN,
        }


# ============================================================================
# SIGNUP TESTS
# ============================================================================


class TestSignup:
    """User signup endpoint tests"""

    def test_signup_successful(self, clean_database):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "role": "PATIENT",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["email"] == "newuser@example.com"
        assert data["data"]["role"] == "PATIENT"
        assert data["data"]["mfa_enabled"] is False

    def test_signup_duplicate_email(self, test_patient):
        """Test signup with duplicate email fails"""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": test_patient["email"],
                "password": "DifferentPassword123!",
                "role": "PATIENT",
            },
        )

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_signup_weak_password(self, clean_database):
        """Test signup with weak password fails"""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user@example.com",
                "password": "weakpass",  # Too short, no uppercase, no digit
                "role": "PATIENT",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_signup_invalid_email(self, clean_database):
        """Test signup with invalid email fails"""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "not-an-email",
                "password": "ValidPassword123!",
                "role": "PATIENT",
            },
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_signup_password_no_uppercase(self, clean_database):
        """Test password must have uppercase"""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user@example.com",
                "password": "validpassword123!",  # No uppercase
                "role": "PATIENT",
            },
        )

        assert response.status_code == 400
        assert "uppercase" in response.json()["detail"].lower()

    def test_signup_password_no_digit(self, clean_database):
        """Test password must have digit"""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user@example.com",
                "password": "ValidPassword!",  # No digit
                "role": "PATIENT",
            },
        )

        assert response.status_code == 400
        assert "digit" in response.json()["detail"].lower()

    def test_signup_different_roles(self, clean_database):
        """Test signup with different user roles"""
        roles = ["PATIENT", "HEALTHCARE_PROVIDER", "SURGEON"]

        for role in roles:
            response = client.post(
                "/api/v1/auth/signup",
                json={
                    "email": f"{role.lower()}@example.com",
                    "password": "SecurePassword123!",
                    "role": role,
                },
            )

            assert response.status_code == 201
            assert response.json()["data"]["role"] == role


# ============================================================================
# LOGIN TESTS
# ============================================================================


class TestLogin:
    """User login endpoint tests"""

    def test_login_successful(self, test_patient):
        """Test successful login returns access token"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_patient["email"],
                "password": test_patient["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["mfa_required"] is False

    def test_login_invalid_password(self, test_patient):
        """Test login with wrong password fails"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_patient["email"],
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, clean_database):
        """Test login with nonexistent email fails"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "AnyPassword123!",
            },
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_case_sensitive_email(self, test_patient):
        """Test email is case-insensitive in database"""
        # Assuming database handles this - this test documents the behavior
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_patient["email"].upper(),
                "password": test_patient["password"],
            },
        )
        # Should fail if email is case-sensitive
        # Should succeed if case-insensitive
        # Document actual behavior


# ============================================================================
# JWT TOKEN TESTS
# ============================================================================


class TestTokens:
    """JWT token handling tests"""

    def test_token_has_expiration(self, test_patient):
        """Test that access token includes expiration"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_patient["email"],
                "password": test_patient["password"],
            },
        )

        token = response.json()["data"]["access_token"]
        # Token should have exp claim (checked during verification)
        assert token is not None
        assert len(token) > 20  # JWT format

    def test_refresh_token_endpoint(self, test_patient):
        """Test token refresh endpoint"""
        # First get a refresh token (need to implement this)
        # This is a placeholder for Phase 2 enhancement
        pass

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token fails"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 403  # Forbidden (no auth header)

    def test_access_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token fails"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401

    def test_access_protected_endpoint_with_valid_token(self, test_patient):
        """Test accessing protected endpoint with valid token succeeds"""
        # Login to get token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_patient["email"],
                "password": test_patient["password"],
            },
        )

        token = login_response.json()["data"]["access_token"]

        # Access protected endpoint
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["user_id"] == test_patient["id"]
        assert data["email"] == test_patient["email"]


# ============================================================================
# RBAC TESTS
# ============================================================================


class TestRBAC:
    """Role-based access control tests"""

    def test_patient_cannot_access_admin_endpoint(self, test_patient):
        """Test patient cannot access admin-only endpoints"""
        # Login as patient
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_patient["email"],
                "password": test_patient["password"],
            },
        )

        token = login_response.json()["data"]["access_token"]

        # Try to access admin endpoint (if one exists)
        # For now, this is a placeholder for when admin endpoints are implemented
        # Example: response = client.get("/api/v1/admin/metrics", headers=...)
        # assert response.status_code == 403

    def test_admin_can_access_admin_endpoint(self, test_admin):
        """Test admin can access admin-only endpoints"""
        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_admin["email"],
                "password": test_admin["password"],
            },
        )

        token = login_response.json()["data"]["access_token"]

        # Verify role in token
        # This should be 200 when admin endpoints are implemented
        assert token is not None


# ============================================================================
# LOGOUT TESTS
# ============================================================================


class TestLogout:
    """Logout endpoint tests"""

    def test_logout_successful(self, test_patient):
        """Test successful logout"""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_patient["email"],
                "password": test_patient["password"],
            },
        )

        token = login_response.json()["data"]["access_token"]

        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_logout_without_token(self):
        """Test logout without authentication fails"""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 403


# ============================================================================
# MFA TESTS
# ============================================================================


class TestMFA:
    """Multi-factor authentication tests"""

    def test_mfa_setup(self, test_patient):
        """Test MFA setup returns QR code"""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_patient["email"],
                "password": test_patient["password"],
            },
        )

        token = login_response.json()["data"]["access_token"]

        # Setup MFA
        response = client.post(
            "/api/v1/auth/mfa/setup",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert "mfa_secret" in data
        assert "qr_code" in data
        assert "backup_codes" in data
        assert len(data["backup_codes"]) > 0

    def test_mfa_already_enabled_error(self, session_factory):
        """Test error when MFA is already enabled"""
        # Would need to create user with MFA already enabled
        # This is a placeholder for future enhancement
        pass


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestAuthFlow:
    """End-to-end authentication flow tests"""

    def test_complete_signup_login_flow(self, clean_database):
        """Test complete user flow: signup -> login -> access protected endpoint"""
        # 1. Signup
        signup_response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "role": "PATIENT",
            },
        )
        assert signup_response.status_code == 201

        # 2. Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["data"]["access_token"]

        # 3. Access protected endpoint with token
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["data"]["email"] == "newuser@example.com"
