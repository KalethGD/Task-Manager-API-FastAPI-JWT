def test_crear_usuario(cliente):
    """ Test crear un nuevo usuario """
    user = {'email': 'usuario@gmail.com', 'username': 'usuario', 'password': 'password123'}
    usuario = cliente.post('users/register', json=user)

    assert usuario.status_code == 201
    assert usuario.json()['email'] == 'usuario@gmail.com' 

def test_obtener_usuarios(cliente):
    """ Test obtener todos los usuarios """

    cliente.post('users/register', json={'email': 'usuario1@gmail.com', 'username': 'usuario1', 'password': 'password123'})
    cliente.post('users/register', json={'email': 'usuario2@gmail.com', 'username': 'usuario2', 'password': 'password123'})

    res = cliente.get('users/')

    assert res.status_code == 200
    assert len(res.json()) == 2

def test_obtener_usuario_por_id(cliente):
    """ Test obtener un usuario por su ID """

    nuevo_usuario = cliente.post('users/register', json={'email': 'usuario@gmail.com', 'username': 'usuario', 'password': 'password123'})

    user_id = nuevo_usuario.json()['id']

    res = cliente.get(f'users/{user_id}')
    assert res.status_code == 200
    assert res.json()['email'] == 'usuario@gmail.com'
    assert res.json()['username'] == 'usuario'

def test_login_usuario(cliente):
    """ Test login de un usuario """

    cliente.post('users/register', json={'email': 'usuario@gmail.com', 'username': 'usuario', 'password': 'password123'})

    res = cliente.post('/auth/login', json={'email': 'usuario@gmail.com', 'password': 'password123'})

    assert res.status_code == 200
     