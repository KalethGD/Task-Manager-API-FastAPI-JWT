const taskForm = document.querySelector("#createTaskForm");
const taskTitle = document.querySelector("#taskTitle");
const tasksList = document.querySelector("#tasksList");

let currentSkip = 0;
const PAGE_LIMIT = 10;

// Obtener token de localStorage
function getToken() {
    return localStorage.getItem("access_token");
}

// Header con autenticación
function getAuthHeaders() {
    return {
        "content-type": "application/json",
        Authorization: `Bearer ${getToken()}`,
    };
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove("hidden");
    successMessage.classList.add("hidden");
}

function showSuccess(message) {
    successText.textContent = message;
    successMessage.classList.remove("hidden");
    errorMessage.classList.add("hidden");
}

function showAlert(message) {
    alertText.textContent = message;
    alertMessage.classList.remove("hidden");
    errorMessage.classList.add("hidden");
    successMessage.classList.add("hidden");
}

function hideMessages() {
    errorMessage.classList.add("hidden");
    successMessage.classList.add("hidden");
    alertMessage.classList.add("hidden");
}

// Cargar tareas cuando la página carga
document.addEventListener("DOMContentLoaded", async () => {
    await loadTasks();
});

// Función para cargar tareas
const loadTasks = async () => {
    try {
        const response = await fetchWithAuth(
            `/tasks/get_tasks?skip=${currentSkip}&limit=${PAGE_LIMIT}`,
        );

        if (response.ok) {
            const tasks = await response.json();
            displayTasks(tasks);
            updatePaginationControls(tasks.length);
        } else {
            tasksList.innerHTML = `<p class="text-red-500 text-center">Error al cargar tareas</p>`;
        }
    } catch (error) {
        console.error("Error al cargar tareas:", error);
        tasksList.innerHTML =
            '<p class="text-red-500 text-center">Error de conexión</p>';
    }
};

function updatePaginationControls(itemsCount) {
    const prevBtn = document.getElementById("prevPage");
    const nextBtn = document.getElementById("nextPage");
    const pageInfo = document.getElementById("pageInfo");
    const currentPage = Math.floor(currentSkip / PAGE_LIMIT) + 1;
    if (pageInfo) pageInfo.textContent = `Página ${currentPage}`;
    if (prevBtn) prevBtn.disabled = currentSkip === 0;
    if (nextBtn) nextBtn.disabled = itemsCount < PAGE_LIMIT;
}

function nextPage() {
    currentSkip += PAGE_LIMIT;
    loadTasks();
}

function prevPage() {
    if (currentSkip >= PAGE_LIMIT) {
        currentSkip -= PAGE_LIMIT;
        loadTasks();
    }
}

// Función para crear tarea
const createTask = async (title) => {
    try {
        const response = await fetchWithAuth(`/tasks/create_task`, {
            method: "POST",
            body: JSON.stringify({ title }),
        });
        if (response.ok) {
            showSuccess("Tarea creada exitosamente");
            setTimeout(() => {
                hideMessages();
            }, 3000);
            await loadTasks();
        } else {
            showError("Error al crear tarea");
        }
    } catch (error) {
        console.error("Error al crear tarea:", error);
        alert("Error de conexión al crear tarea");
    }
};

// Función para eliminar tarea
const deleteTask = async (id, title) => {
    if (!confirm(`¿Estás seguro de eliminar la tarea "${title}"?`)) {
        return;
    }
    const response = await fetchWithAuth(`/tasks/delete_task/${id}`, {
        method: "DELETE",
    });
    if (response.ok) {
        showAlert(`Tarea "${title}" eliminada`);
        setTimeout(() => {
            hideMessages();
        }, 3000);
        await loadTasks();
    } else {
        showError("Error al eliminar tarea");
    }
};

// Función para marcar tarea como completada/pendiente
const toggleTask = async (id, completed) => {
    const response = await fetchWithAuth(`/tasks/update_task/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ completed }),
    });
    if (response.ok) {
        await loadTasks();
    } else {
        showError(`Error al actualizar tarea ${id}`);
    }
};

function editTask(taskId, span, currentTitle) {
    // Crear input
    const input = document.createElement("input");
    input.type = "text";
    input.value = currentTitle;
    input.className =
        "w-full px-2 py-1 border border-blue-500 rounded focus:ring-2 focus:ring-blue-300 outline-none";

    // Reemplazar span con input
    span.replaceWith(input);
    input.focus();

    // Al presionar Enter
    input.addEventListener("keypress", async (e) => {
        if (e.key === "Enter") {
            const newTitle = input.value.trim();
            if (newTitle && newTitle !== currentTitle) {
                await updateTask(taskId, newTitle);
            } else {
                await loadTasks(); // Cancelar
            }
        }
    });

    // Al perder focus (click fuera)
    input.addEventListener("blur", async () => {
        const newTitle = input.value.trim();
        if (newTitle && newTitle !== currentTitle) {
            await updateTask(taskId, newTitle);
        } else {
            await loadTasks(); // Cancelar
        }
    });
}

async function updateTask(taskId, newTitle) {
    try {
        const response = await fetchWithAuth(`/tasks/update_task/${taskId}`, {
            method: "PATCH",
            body: JSON.stringify({ title: newTitle }),
        });

        if (response.ok) {
            await loadTasks();
        }
    } catch (error) {
        console.error(`Error al actualizar tarea ${newTitle}:`, error);
    }
}

//function para mostrar tareas en el DOM
function displayTasks(tasks) {
    if (tasks.length === 0) {
        tasksList.innerHTML = `<p class="text-gray-500 text-center">No hay tareas disponibles</p>`;
        return;
    }

    tasksList.innerHTML = "";

    tasks.forEach((task) => {
        const li = document.createElement("li");
        li.classList.add(
            "flex",
            "items-center",
            "justify-between",
            "p-4",
            "border",
            "border-gray-200",
            "rounded-lg",
            "hover:bg-gray-50",
            "transition",
        );

        // Check Box para marcar tarea como completada
        const checkBox = document.createElement("input");
        checkBox.classList.add(
            "w-5",
            "h-5",
            "px-4",
            "text-blue-600",
            "rounded",
            "focus:ring-2",
            "focus:ring-blue-500",
        );
        checkBox.type = "checkbox";
        checkBox.checked = task.completed || false;
        checkBox.addEventListener("change", () => {
            toggleTask(task.id, checkBox.checked);
        });

        // Span para el título de la tarea
        const span = document.createElement("span");
        span.className = task.completed
            ? "line-through text-green-400 px-4"
            : "text-gray-800 px-4";

        span.textContent = task.title;

        //Boton para eliminar tarea
        const deleteButton = document.createElement("button");
        deleteButton.classList.add(
            "text-red-500",
            "hover:text-red-700",
            "font-semibold",
            "px-3",
            "py-1",
            "rounded",
            "hover:bg-red-50",
            "transition",
        );
        deleteButton.textContent = "Eliminar";
        deleteButton.addEventListener("click", () => {
            deleteTask(task.id, task.title);
        });

        //Botón para editar tarea
        const editButton = document.createElement("button");
        editButton.classList.add(
            "text-green-500",
            "hover:text-green-700",
            "font-semibold",
            "px-3",
            "py-1",
            "rounded",
            "hover:bg-green-50",
            "transition",
        );
        editButton.textContent = "Editar";
        editButton.addEventListener("click", () => {
            editTask(task.id, span, task.title);
        });

        const firstDiv = document.createElement("div");
        firstDiv.className = "flex items-center w-full gap-4";

        const secondDiv = document.createElement("div");
        secondDiv.className = "flex gap-2";

        firstDiv.appendChild(checkBox);
        firstDiv.appendChild(span);
        secondDiv.appendChild(editButton);
        secondDiv.appendChild(deleteButton);

        li.appendChild(firstDiv);
        li.appendChild(secondDiv);

        tasksList.appendChild(li);
    });
}

taskForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const title = taskTitle.value.trim();

    if (!title) {
        alert("Por favor escribe el título de la tarea");
        return;
    }
    await createTask(title);
    taskTitle.value = "";
});
