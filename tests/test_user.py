from core import security


def test_hash_password():
    """Test que hash_password genera un hash bcrypt válido"""
    password = "mipassword123"
    hashed = security.hash_password(password)
    
    print(f'Password: {password}')
    print(f'Hashed: {hashed}')
    
    assert hashed is not None
    assert hashed.startswith("$2b$")
    assert len(hashed) > 50


def test_verify_password_correct():
    """Test verificación de password correcto"""
    password = "mipassword123"
    hashed = security.hash_password(password)
    
    result = security.verify_password(password, hashed)
    print(f'Verificación del password: {result}')
    
    assert result is True


def test_verify_password_incorrect():
    """Test verificación de password incorrecto"""
    password = "mipassword123"
    hashed = security.hash_password(password)
    
    result = security.verify_password("wrongpassword", hashed)
    print(f'Verificación del password incorrecto: {result}')
    
    assert result is False


def test_create_access_token():
    """Test creación de token JWT"""
    data = {"sub": "user@email.com"}
    token = security.create_access_token(data=data)
    
    print(f'Token: {token}')
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 50


def test_verify_token_valid():
    """Test verificación de token válido"""
    data = {"sub": "user@email.com"}
    token = security.create_access_token(data=data)
    
    decoded = security.verify_access_token(token)
    print(f'Decoded: {decoded}')
    
    assert decoded is not None
    assert decoded.get("sub") == "user@email.com"
    assert "exp" in decoded


def test_verify_token_invalid():
    """Test verificación de token inválido"""
    token_invalid = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.signature"
    
    result = security.verify_access_token(token_invalid)
    print(f'Invalid token decode: {result}')
    
    assert result is None
