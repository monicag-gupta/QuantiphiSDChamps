from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pwdlib import PasswordHash


app = FastAPI(
    title="JWT Authentication API"
)


# ============================================================
# 1. JWT CONFIGURATION
# ============================================================

SECRET_KEY = "change-this-to-a-long-random-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ============================================================
# 2. PASSWORD HASHING
# ============================================================

password_hash = PasswordHash.recommended()


# ============================================================
# 3. FAKE DATABASE
# Replace this later with MySQL/PostgreSQL
# ============================================================

fake_users_db = {
    "jay": {
        "username": "jay",
        "full_name": "Jay Kumar",
        "hashed_password": password_hash.hash("password123"),
        "disabled": False
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "hashed_password": password_hash.hash("admin123"),
        "disabled": False
    }
}


# ============================================================
# 4. SECURITY SCHEME
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# ============================================================
# 5. PASSWORD FUNCTIONS
# ============================================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Compare the plain password entered by the user
    with the hashed password stored in the database.
    """
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# ============================================================
# 6. AUTHENTICATE USER
# ============================================================

def authenticate_user(
    username: str,
    password: str
):
    """
    Check whether the username exists and whether
    the password is correct.
    """

    user = fake_users_db.get(username)

    if not user:
        return None

    if not verify_password(
        password,
        user["hashed_password"]
    ):
        return None

    return user


# ============================================================
# 7. CREATE JWT TOKEN
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
):
    """
    Create a signed JWT token.
    """

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    # Add expiration to JWT payload
    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# ============================================================
# 8. GET CURRENT USER FROM TOKEN
# ============================================================

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    """
    Extract JWT from Authorization header,
    verify it, and return the authenticated user.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        # Decode and verify JWT
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Get username from token
        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    # Find user in database
    user = fake_users_db.get(username)

    if user is None:
        raise credentials_exception

    return user


# ============================================================
# 9. LOGIN ENDPOINT
# ============================================================

@app.post("/login")
async def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ]
):
    """
    User sends username and password.
    If valid, return JWT access token.
    """

    user = authenticate_user(
        form_data.username,
        form_data.password
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    access_token = create_access_token(
        data={
            "sub": user["username"]
        },
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# 10. PROTECTED ENDPOINT
# ============================================================

@app.get("/profile")
async def get_profile(
    current_user: Annotated[
        dict,
        Depends(get_current_user)
    ]
):
    """
    Only users with a valid JWT token can access this.
    """

    return {
        "message": "Welcome to protected profile",
        "username": current_user["username"],
        "full_name": current_user["full_name"]
    }


# ============================================================
# 11. PUBLIC ENDPOINT
# ============================================================

@app.get("/")
async def home():

    return {
        "message": "This is a public endpoint"
    }
