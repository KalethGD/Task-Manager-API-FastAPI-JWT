from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from database import get_db
from models import User
from schemas import schema_task
from services import service_task

router = APIRouter(prefix='/tasks', tags=['Tasks'])


@router.get('/get_tasks', response_model=list[schema_task.TaskResponseWithUser], status_code=status.HTTP_200_OK)
def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """ Endpoin que se encargara de hacer la peticion GET para traer todas las Tareas existentes"""
    is_admin = current_user.role == 'admin'
    return service_task.get_tasks(current_user.id, db, is_admin)

@router.get('/get_task/{task_id}', response_model=schema_task.TaskResponse, status_code=status.HTTP_200_OK)
def get_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    is_admin = current_user.role == 'admin'
    task = service_task.get_task(task_id, current_user.id, db, is_admin)

    """ Endpoin que se encargara de hacer la peticion get para traer una Tarea en especifico por su ID"""

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Tarea con id: {task_id}, no encontrada'
        )
    return task


@router.post('/create_task', response_model=schema_task.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schema_task.TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    """ Endpoin que se encargara de hacer la peticion POST para crear una nueva Tarea"""

    try:
        return service_task.create_task(task, current_user.id, db)
    
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Error de integridad al crear la tarea. Verifique los datos proporcionados.'
        )
    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error al crear la tarea. Error en el servidor.'
        )

@router.delete('/delete_task/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    """ Endpoin que se encargara de hacer la peticion DELETE para eliminar una Tarea en especifico por su ID"""

    try:
        task = service_task.delete_task(task_id, current_user.id, db)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Tarea con id: {task_id}, no encontrada'
            )
        return None
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error al eliminar la tarea. Error en el servidor.'
        )
    
@router.patch('/update_task/{task_id}', status_code=status.HTTP_200_OK, response_model=schema_task.TaskResponse)
def update_task(task_id: int, task_data: schema_task.TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    """ Endpoin que se encargara de hacer la peticion PATCH para actualizar una Tarea en especifico por su ID"""
    is_admin = current_user.role == 'admin'
    try:
        task = service_task.update_task(task_id, task_data, current_user.id, db, is_admin)

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'La tarea: {task_data.title}, no fue encontrada'
            )
        return task
    except Exception as e:
        raise e