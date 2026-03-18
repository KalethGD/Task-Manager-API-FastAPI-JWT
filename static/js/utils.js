// Verificar si el usuario está autenticado
function isAuthenticated() {
    const token = localStorage.getItem("access_token");
    return token !== null && token !== "";
}

// Verificar autenticación y redirigir si no está logueado
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = "/static/login.html";
    }
}

// Logout: revoca el refresh token en BD y limpia localStorage
async function logout() {
    const refreshToken = localStorage.getItem("refresh_token");
    if (refreshToken) {
        try {
            await fetch("/auth/logout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });
        } catch (_) {
            // Si falla la red, continuar con el logout local igualmente
        }
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("userEmail");
    window.location.href = "/static/login.html";
}

// Intenta renovar los tokens usando el refresh token almacenado.
// Retorna el nuevo access token, o null si falla.
async function _tryRefreshToken() {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return null;

    try {
        const response = await fetch("/auth/refresh", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("refresh_token", data.refresh_token);
            return data.access_token;
        }
        return null;
    } catch (_) {
        return null;
    }
}

// Wrapper para fetch que inyecta el Authorization header automáticamente.
// Si recibe un 401, intenta refrescar el token y reintenta la request una vez.
// Si el refresh también falla, redirige al login.
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem("access_token");

    const authOptions = {
        ...options,
        headers: {
            "content-type": "application/json",
            ...options.headers,
            Authorization: `Bearer ${token}`,
        },
    };

    let response = await fetch(url, authOptions);

    if (response.status === 401) {
        const newToken = await _tryRefreshToken();

        if (!newToken) {
            // Refresh falló: sesión realmente expirada
            localStorage.clear();
            window.location.href = "/static/login.html";
            throw new Error("Sesión expirada");
        }

        // Reintentar la request original con el nuevo token
        authOptions.headers.Authorization = `Bearer ${newToken}`;
        response = await fetch(url, authOptions);
    }

    return response;
}
