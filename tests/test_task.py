
#crear 
def test_crear_tarea(cliente):
    data = {
        "title": "Nueva Tarea",
        "completed": False, 
    }
    response = cliente.post("/tasks/create_task", json=data)

    assert response.status_code == 201
    assert response.json()["title"] == "Nueva Tarea"

def test_crear_tarea_fallida(cliente):
    data = {
        "title": "",  
        "completed": False,
    }
    response = cliente.post("/tasks/create_task", json=data)

    assert response.status_code == 422

#obtener
def test_obtener_tareas_multiples(cliente):
    cliente.post('/tasks/create_task', json={
        'title': 'Tarea 1',
        'completed': False
    })
    cliente.post('/tasks/create_task', json={
        'title': 'Tarea 2',
        'completed': True
    })

    response = cliente.get('/tasks/get_tasks')

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_obtener_tarea_por_id(cliente):
    crear_response = cliente.post('/tasks/create_task', json={
        'title': 'Tarea Especifica',
        'completed': False
    })
    tarea_id = crear_response.json()['id']

    response = cliente.get(f'/tasks/get_task/{tarea_id}')

    assert response.status_code == 200
    assert response.json()['title'] == 'Tarea Especifica'

def test_obtener_tarea_no_encontrada(cliente):
    response = cliente.get('/tasks/get_task/9999')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Tarea con id: 9999, no encontrada'

#eliminar
def test_eliminar_tarea_existente(cliente):
    crear_response = cliente.post('/tasks/create_task', json={
        'title': 'Tarea a Eliminar',
        'completed': False
    })
    tarea_id = crear_response.json()['id']

    delete_response = cliente.delete(f'/tasks/delete_task/{tarea_id}')

    assert delete_response.status_code == 204

    get_response = cliente.get(f'/tasks/get_task/{tarea_id}')
    assert get_response.status_code == 404

def test_eliminar_tarea_no_existente(cliente):
    response = cliente.delete('/tasks/delete_task/9999')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Tarea con id: 9999, no encontrada'

#actualizar
def test_actualizar_tarea_existente(cliente):
    crear_response = cliente.post('/tasks/create_task', json={
        'title': 'Tarea a Actualizar',
        'completed': False
    })
    tarea_id = crear_response.json()['id']

    update_data = {
        'title': 'Tarea Actualizada',
        'completed': True
    }
    update_response = cliente.patch(f'/tasks/update_task/{tarea_id}', json=update_data)

    assert update_response.status_code == 200
    assert update_response.json()['title'] == 'Tarea Actualizada'
    assert update_response.json()['completed'] is True

def test_actualizar_tarea_no_existente(cliente):
    update_data = {
        'title': 'Tarea Inexistente',
        'completed': True
    }
    response = cliente.patch('/tasks/update_task/9999', json=update_data)

    assert response.status_code == 404
    assert response.json()['detail'] == 'La tarea: Tarea Inexistente, no fue encontrada'

def test_actualizar_tarea_datos_invalidos(cliente):
    crear_response = cliente.post('/tasks/create_task', json={
        'title': 'Tarea a Actualizar Invalidamente',
        'completed': False
    })
    tarea_id = crear_response.json()['id']

    update_data = {
        'title': '',  
        'completed': True
    }
    response = cliente.patch(f'/tasks/update_task/{tarea_id}', json=update_data)

    assert response.status_code == 422