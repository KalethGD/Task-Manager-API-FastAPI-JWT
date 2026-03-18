// Configuracion de la api
const API_URL = "";

// Elementos del DOM
const loginForm = document.getElementById("loginForm");
const errorMessage = document.getElementById("errorMessage");
const errorText = document.getElementById("errorText");
const successMessage = document.getElementById("successMessage");
const successText = document.getElementById("successText");

// Funcion para mostrar mensajes
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

function hideMessages() {
    errorMessage.classList.add("hidden");
    successMessage.classList.add("hidden");
}

// Manejar el submit del formulario
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideMessages();

    // Obtener los datos del formulario
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    //validacion basica
    if (!email || !password) {
        showError("Por favor completa todos los campos");
        return;
    }

    try {
        // Llamar la API
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email: email, password: password }),
        });
        const data = await response.json();

        // Si el login es exitoso
        if (response.ok) {
            // Guardar ambos tokens en localStorage
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("refresh_token", data.refresh_token);
            localStorage.setItem("userEmail", email);

            // Mostrar mensaje de exito
            showSuccess("Login exitoso! Redirigiendo...");

            // Obtener informacion del usuario para verificar el rol
            const userResponse = await fetch("/users/me/profile", {
                headers: {
                    Authorization: `Bearer ${data.access_token}`,
                },
            });

            if (userResponse.ok) {
                const userData = await userResponse.json();

                // Redirigir segun el rol
                setTimeout(() => {
                    if (userData.role === "admin") {
                        window.location.href = "/static/admin.html";
                    } else {
                        window.location.href = "/static/dashboard.html";
                    }
                }, 1500);
            }
        } else {
            // si hay error de credenciales:
            if (response.status === 401) {
                showError("Credenciales incorrectas. Intenta de nuevo.");
            } else {
                showError(data.detail || "Ocurrió un error. Intenta de nuevo.");
            }
        }
    } catch (error) {
        // Error de red o del servidor
        console.error("Error:", error);
        showError(
            "No se pudo conectar al servidor. Intenta de nuevo más tarde.",
        );
    }
});

// Ocultar mensajes cuando el usuario empieza a escribir
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");

emailInput.addEventListener("input", hideMessages);
passwordInput.addEventListener("input", hideMessages);
