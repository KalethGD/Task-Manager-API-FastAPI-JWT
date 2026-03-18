let allTasksCache = [];

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

// Cargar estadísticas cuando la página carga
async function loadStats() {
    try {
        const response = await fetchWithAuth("/users/", {
            method: "GET",
        });

        if (response.ok) {
            const users = await response.json();

            // Total de usuarios
            document.querySelector("#totalUsers").textContent = users.length;

            // Total admins
            const admins = users.filter((user) => user.role === "admin");
            document.querySelector("#totalAdmins").textContent = admins.length;

            // Cargar total de tareas
            await loadTotalTasks();
        }
    } catch (error) {
        console.error("Error al cargar estadísticas:", error);
    }
}

// Cargar total de tareas
async function loadTotalTasks() {
    try {
        const response = await fetchWithAuth("/tasks/get_tasks", {
            method: "GET",
        });

        if (response.ok) {
            const tasks = await response.json();
            document.querySelector("#totalTasks").textContent = tasks.length;
        }
    } catch (error) {
        console.error("Error al cargar el total de tareas:", error);
        document.querySelector("#totalTasks").textContent = "0";
    }
}

// Cargar usuarios en la tabla
async function loadUsers() {
    hideMessages();
    try {
        const response = await fetchWithAuth("/users/", {
            method: "GET",
        });

        if (response.ok) {
            const users = await response.json();
            const tablaUsers = document.querySelector("#usersTableBody");
            const userFilter = document.querySelector("#filterByUser");

            tablaUsers.innerHTML = ""; // Limpiar tabla antes de cargar
            userFilter.innerHTML =
                '<option value="all">Todos los usuarios</option>'; // Opción "Todos"

            users.forEach((user) => {
                userFilter.innerHTML += `<option value="${user.id}">${user.email}</option>`;

                const row = document.createElement("tr");
                row.className = "hover:bg-gray-50";

                // Determinar color del badge según el rol
                const roleBadgeColor =
                    user.role === "admin"
                        ? "bg-purple-100 text-purple-800"
                        : "bg-blue-100 text-blue-800";

                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${user.id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${user.email}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-3 py-1 text-xs font-semibold rounded-full ${roleBadgeColor}">
                            ${user.role}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-3 py-1 text-xs font-semibold rounded-full ${user.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}">
                            ${user.is_active ? "Activo" : "Inactivo"}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        <button onclick="editUser(${user.id})" class="text-blue-600 hover:text-blue-800 font-medium">
                            Editar
                        </button>
                        <button onclick="deleteUser(${user.id}, '${user.email}')" class="text-red-600 hover:text-red-800 font-medium">
                            Eliminar
                        </button>
                    </td>
                `;
                tablaUsers.appendChild(row);
            });

            // Agregar evento al select para filtrar tareas
            if (userFilter) {
                userFilter.addEventListener("change", (e) => {
                    filterTaskForUser(e.target.value);
                });
            }
        }
    } catch (error) {
        console.error("Error al cargar usuarios:", error);
    }
}

// funcion para eliminar usuario
async function deleteUser(userId, userEmail) {
    if (!confirm(`⚠️ ¿Estás seguro de que quieres eliminar a: ${userEmail}?`)) {
        return;
    }
    try {
        const userRole = await fetchWithAuth("/users/me/profile", {
            method: "GET",
        });
        const userData = await userRole.json();
        if (userData.id === userId) {
            showAlert("No puedes eliminar tu propia cuenta.");
            setTimeout(() => {
                hideMessages();
            }, 3000);
            return;
        }

        const response = await fetchWithAuth(`/users/delete/${userId}/`, {
            method: "DELETE",
        });

        if (response.ok) {
            loadStats();
            loadUsers();
            showAlert(`Eliminando usuario: ${userEmail}`);
            setTimeout(() => {
                hideMessages();
            }, 1500);
        }
    } catch (error) {
        console.error("Error al eliminar usuario:", error);
        showError("Error al eliminar usuario.");
    }
}

async function editUser(userId) {
    try {
        const response = await fetchWithAuth(`/users/${userId}/`, {
            method: "GET",
        });
        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status}`);
        }
        const userData = await response.json();

        // Rellenar el formulario con los datos del usuario
        document.querySelector("#editUserId").value = userData.id;
        document.querySelector("#editUserEmail").value = userData.email;
        document.querySelector("#editUserRole").value = userData.role;
        document.querySelector("#editUserActive").checked = userData.is_active;

        // Mostrar el modal de edición
        document.querySelector("#editUserModal").classList.remove("hidden");
    } catch (error) {
        console.error("Error al obtener datos: ", error);
        alert("No se pudo cargar el usuario. Inténtalo de nuevo.");
    }
}

function filterTaskForUser(userId) {
    // Mostrar overlay de carga
    const overlay = document.querySelector("#tasksLoadingOverlay");
    if (overlay) overlay.classList.remove("hidden");

    // Usar setTimeout para permitir que el overlay se muestre
    setTimeout(() => {
        if (!userId || userId === "all") {
            // Mostrar todas las tareas
            renderTasks(allTasksCache);
        } else {
            // Filtrar por usuario
            const filtered = allTasksCache.filter(
                (task) => task.owner?.id === parseInt(userId),
            );
            renderTasks(filtered);
        }

        // Ocultar overlay después de renderizar
        if (overlay) overlay.classList.add("hidden");
    }, 1000);
}

// Tasks

async function loadTasks() {
    // Mostrar overlay de carga
    const overlay = document.querySelector("#tasksLoadingOverlay");
    if (overlay) overlay.classList.remove("hidden");

    try {
        const response = await fetchWithAuth("/tasks/get_tasks", {
            method: "GET",
        });

        if (response.ok) {
            const tasks = await response.json();
            allTasksCache = tasks; // Guardado en cache para futuros filtros
            renderTasks(tasks);
        } else {
            console.error("Error en la respuesta:", response.status);
        }
    } catch (error) {
        console.error("Error al cargar tareas:", error);
        const tableTasks = document.querySelector("#allTasksTable");
        if (tableTasks) {
            tableTasks.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-8 text-center text-red-500">
                        Error al cargar las tareas
                    </td>
                </tr>
            `;
        }
    } finally {
        // Ocultar overlay siempre, incluso si hay error
        if (overlay) overlay.classList.add("hidden");
    }
}

function renderTasks(tasks) {
    const tableTasks = document.querySelector("#allTasksTable");

    if (!tableTasks) {
        console.error("No se encontró el elemento #allTasksTable");
        return;
    }

    tableTasks.innerHTML = ""; // Limpiar tabla

    if (tasks.length === 0) {
        tableTasks.innerHTML = `
                    <tr>
                        <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                            No hay tareas registradas
                        </td>
                    </tr>
                `;
        return;
    }

    tasks.forEach((task) => {
        const row = document.createElement("tr");
        row.className = "hover:bg-gray-50";
        const fechaLegible = new Date(task.created_at).toLocaleDateString(
            "es-ES",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
            },
        );
        // Badge para estado completado/pendiente
        const statusBadge = task.completed
            ? '<span class="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">✓ Completada</span>'
            : '<span class="px-3 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">⏳ Pendiente</span>';

        row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${task.id}</td>
                    <td class="px-6 py-4 text-sm text-gray-900">${task.title}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${task.owner.username}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${statusBadge}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${fechaLegible}</td>

                    <td class="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        <button onclick="editTaskAdmin('${task.id}', '${task.owner.username}', '${task.title}')" 
                                class="text-blue-600 hover:text-blue-800 font-medium">
                            Editar
                        </button>
                        <button onclick="deleteTaskAdmin('${task.id}', '${task.owner.username}', '${task.title}')" 
                                class="text-red-600 hover:text-red-800 font-medium">
                            Eliminar
                        </button>
                    </td>
                `;
        tableTasks.appendChild(row);
    });
}

async function deleteTaskAdmin(taskId, taskOwner, taskTitle) {
    if (
        !confirm(
            `⚠️ ¿Estás seguro de que quieres eliminar la tarea "${taskTitle}" del usuario: ${taskOwner} (ID: ${taskId})?`,
        )
    ) {
        return;
    }
    try {
        const response = await fetchWithAuth(`/tasks/delete_task/${taskId}/`, {
            method: "DELETE",
        });
        if (response.ok) {
            showAlert(
                `Tarea: "${taskTitle}" de ${taskOwner} eliminada correctamente...`,
            );
            setTimeout(() => {
                hideMessages();
            }, 4000);
            loadStats();
            loadTasks();
        }
    } catch (error) {
        console.error("Error al eliminar tarea:", error);
        alert("Error al eliminar tarea. Inténtalo de nuevo.");
    }
}

async function editTaskAdmin(taskId, taskOwner, taskTitle) {
    console.log("Editar tarea:", taskId, taskOwner, taskTitle);
    try {
        const response = await fetchWithAuth(`/tasks/get_task/${taskId}/`, {
            method: "GET",
        });
        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status}`);
        }
        const taskData = await response.json();
        console.log("Datos de la tarea obtenidos:", taskData);

        // Rellenar el formulario con los datos de la tarea
        document.querySelector("#editTaskId").value = taskData.id;
        document.querySelector("#editTaskTitle").value = taskData.title;
        document.querySelector("#editTaskCompleted").value = taskData.completed;

        // Mostrar el modal de edición
        document.querySelector("#editTaskModal").classList.remove("hidden");
    } catch (error) {
        console.error("Error al obtener datos de la tarea: ", error);
        alert("No se pudo cargar la tarea. Inténtalo de nuevo.");
    }
}

function closeEditModal() {
    document.querySelector("#editUserModal").classList.add("hidden");
    document.querySelector("#editTaskModal").classList.add("hidden");
    document.querySelector("#editUserForm").reset();
}

// Manejar envio del formulario de usuarios
async function handleEditSubmit(event) {
    event.preventDefault();

    const userId = document.querySelector("#editUserId").value;
    const email = document.querySelector("#editUserEmail").value;
    const role = document.querySelector("#editUserRole").value;
    const isActive = document.querySelector("#editUserActive").checked;

    try {
        const response = await fetchWithAuth(`/users/update/${userId}/`, {
            method: "PATCH",
            body: JSON.stringify({
                email: email,
                role: role,
                is_active: isActive,
            }),
        });

        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status}`);
        }
        const updatedUser = await response.json();
        loadStats();
        loadUsers();
        showSuccess(`Usuario actualizado: ${updatedUser.email}`);
        setTimeout(() => {
            hideMessages();
        }, 4000);
        setTimeout(() => {
            closeEditModal();
        }, 500);
    } catch (error) {
        console.error("Error al actualizar usuario:", error);
        showError("Error al actualizar usuario.");
        setTimeout(() => {
            hideMessages();
        }, 2000);
    }
}

async function handleEditTaskSubmit(e) {
    e.preventDefault();

    const taskId = document.querySelector("#editTaskId").value;
    const title = document.querySelector("#editTaskTitle").value;
    const completed =
        document.querySelector("#editTaskCompleted").value === "true";

    try {
        const response = await fetchWithAuth(`/tasks/update_task/${taskId}/`, {
            method: "PATCH",
            body: JSON.stringify({ title: title, completed: completed }),
        });
        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status}`);
        }
        const updatedTask = await response.json();
        loadStats();
        loadTasks();
        showSuccess(`Tarea actualizada: ${updatedTask.title}`);
        setTimeout(() => {
            hideMessages();
        }, 4000);
        setTimeout(() => {
            closeEditModal();
        }, 500);
    } catch (error) {
        console.error("Error al actualizar tarea:", error);
        alert("Error al actualizar tarea. Inténtalo de nuevo.");
    }
}
