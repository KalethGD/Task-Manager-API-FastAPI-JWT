from sqlalchemy.orm import Session, joinedload

from models import Task, User


# Funcion get_tasks que se encargara de traer todas las tareas existentes en la base de datos
def get_tasks(user_id: int, db: Session, is_admin: bool = False) -> list[Task]:
    query = db.query(Task).options(joinedload(Task.owner))
    if is_admin:
        return query.all()
    return query.filter(Task.user_id == user_id).all()

# Funcion get_task que se encargara de traer una tarea en especifico por su ID
def get_task(task_id: int, user_id: int, db: Session, is_admin: bool = False) -> Task | None:
    if is_admin:
        return db.query(Task).filter(Task.id == task_id).first()
    return db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()

# Funcion create_task que se encargara de crear una nueva tarea en la base de datos
def create_task(task_data: Task, user_id: int, db: Session) -> Task:
    try:
        task_dict = task_data.model_dump()
        task_dict['user_id'] = user_id
        task = Task(**task_dict)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except Exception as e:
        db.rollback()
        raise e
    
# Funcion delete_task que se encargara de eliminar una tarea en especifico por su ID
def delete_task(task_id: int, user_id: int, db: Session) -> None:
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if user.role == 'admin':
            task = db.query(Task).filter(Task.id == task_id).first()
        else:
            task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()

        if not task:
            return False
        
        db.delete(task)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    
# Funcion update_task que se encargara de actualizar una tarea en especifico por su ID
def update_task(task_id: int, task_data: Task, user_id: int, db: Session, is_admin: bool = False) -> Task | None:
    try:
        if is_admin:
            task = db.query(Task).filter(Task.id == task_id).first()
        else:
            task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()

        if not task:
            return None
        
        task_update = task_data.model_dump(exclude_unset=True)
        for key, value in task_update.items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)
        return task
    except Exception as e:
        db.rollback()
        raise e