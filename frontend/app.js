(() => {
  const API_BASE = window.MOVIE_REC_API_BASE || "https://movie-recommender-hybrid.onrender.com";
  const tokenKey = "movieRecToken";
  const userKey = "movieRecUser";
  const lastUserKey = "movieRecLastUserId";

  const page = document.body.dataset.page;

  const getToken = () => localStorage.getItem(tokenKey) || "";
  const setToken = (token) => {
    if (token) {
      localStorage.setItem(tokenKey, token);
    } else {
      localStorage.removeItem(tokenKey);
    }
  };
  const getUser = () => {
    const raw = localStorage.getItem(userKey);
    return raw ? JSON.parse(raw) : null;
  };
  const setUser = (user) => {
    if (user) {
      localStorage.setItem(userKey, JSON.stringify(user));
    } else {
      localStorage.removeItem(userKey);
    }
  };
  const setStatus = (el, message) => {
    if (!el) return;
    el.textContent = message;
  };

  const apiFetch = async (path, options = {}) => {
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    const token = getToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : null;
    if (!response.ok) {
      const message = payload?.detail || "Request failed";
      throw new Error(message);
    }
    return payload;
  };

  const renderList = (listEl, items) => {
    listEl.innerHTML = "";
    if (!items || items.length === 0) {
      listEl.innerHTML = "<li>No results yet.</li>";
      return;
    }
    items.forEach((movie) => {
      const li = document.createElement("li");
      li.textContent = `${movie.title} (${movie.year || "Year?"}) - ${movie.genres || "Genres unavailable"}`;
      listEl.appendChild(li);
    });
  };

  const loadUsers = async (selectEl, statusEl) => {
    try {
      setStatus(statusEl, "Loading users...");
      const users = await apiFetch("/api/users");
      selectEl.innerHTML = "";
      users.forEach((user) => {
        const option = document.createElement("option");
        option.value = String(user.id);
        option.textContent = user.username ? `User ${user.username} (ID ${user.id})` : `User ${user.id}`;
        selectEl.appendChild(option);
      });
      const firstId = users[0]?.id;
      if (firstId) {
        localStorage.setItem(lastUserKey, String(firstId));
      }
      setStatus(statusEl, "");
    } catch (err) {
      setStatus(statusEl, err.message);
    }
  };

  if (page === "home") {
    const selectEl = document.getElementById("home-user-select");
    const statusEl = document.getElementById("home-status");
    const form = document.getElementById("home-form");
    loadUsers(selectEl, statusEl);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const userId = selectEl.value;
      if (!userId) return;
      localStorage.setItem(lastUserKey, userId);
      window.location.href = `/recommend.html?user_id=${encodeURIComponent(userId)}`;
    });
  }

  if (page === "login") {
    const form = document.getElementById("login-form");
    const statusEl = document.getElementById("login-status");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const username = document.getElementById("login-username").value.trim();
      const password = document.getElementById("login-password").value.trim();
      if (!username || !password) {
        setStatus(statusEl, "Enter username and password.");
        return;
      }
      try {
        setStatus(statusEl, "Signing in...");
        const payload = await apiFetch("/api/login", {
          method: "POST",
          body: JSON.stringify({ username, password })
        });
        setToken(payload.token);
        setUser(payload.user);
        setStatus(statusEl, `Welcome ${payload.user.username}.`);
        window.location.href = "/dashboard.html";
      } catch (err) {
        setStatus(statusEl, err.message);
      }
    });
  }

  if (page === "signup") {
    const form = document.getElementById("signup-form");
    const statusEl = document.getElementById("signup-status");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const username = document.getElementById("signup-username").value.trim();
      const password = document.getElementById("signup-password").value.trim();
      if (!username || !password) {
        setStatus(statusEl, "Enter username and password.");
        return;
      }
      try {
        setStatus(statusEl, "Creating account...");
        await apiFetch("/api/signup", {
          method: "POST",
          body: JSON.stringify({ username, password })
        });
        const payload = await apiFetch("/api/login", {
          method: "POST",
          body: JSON.stringify({ username, password })
        });
        setToken(payload.token);
        setUser(payload.user);
        setStatus(statusEl, "Account created. Redirecting...");
        window.location.href = "/dashboard.html";
      } catch (err) {
        setStatus(statusEl, err.message);
      }
    });
  }

  if (page === "dashboard") {
    const statusEl = document.getElementById("dashboard-status");
    const listEl = document.getElementById("dashboard-list");
    const userEl = document.getElementById("dashboard-user");
    const linkEl = document.getElementById("recommend-link");
    const user = getUser();
    if (user) {
      userEl.textContent = user.username;
    } else {
      userEl.textContent = "Guest";
    }

    const userId = localStorage.getItem(lastUserKey) || user?.id;
    if (userId && linkEl) {
      linkEl.href = `/recommend.html?user_id=${encodeURIComponent(userId)}`;
    }

    if (!userId) {
      setStatus(statusEl, "Select a user on the Home page.");
    } else {
      apiFetch(`/api/recommendations?user_id=${userId}`)
        .then((data) => {
          renderList(listEl, data.results);
          setStatus(statusEl, "");
        })
        .catch((err) => setStatus(statusEl, err.message));
    }
  }

  if (page === "recommend") {
    const listEl = document.getElementById("recommend-list");
    const statusEl = document.getElementById("recommend-status");
    const params = new URLSearchParams(window.location.search);
    const userId = params.get("user_id") || localStorage.getItem(lastUserKey);
    if (!userId) {
      setStatus(statusEl, "Pick a user from Home first.");
    } else {
      apiFetch(`/api/recommendations?user_id=${userId}`)
        .then((data) => {
          renderList(listEl, data.results);
          setStatus(statusEl, "");
        })
        .catch((err) => setStatus(statusEl, err.message));
    }
  }

  if (page === "rate") {
    const form = document.getElementById("rate-form");
    const statusEl = document.getElementById("rate-status");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const movieId = Number(document.getElementById("rate-movie-id").value);
      const rating = Number(document.getElementById("rate-value").value);
      if (!movieId || Number.isNaN(rating)) {
        setStatus(statusEl, "Enter a valid movie ID and rating.");
        return;
      }
      try {
        setStatus(statusEl, "Submitting rating...");
        await apiFetch("/api/rate", {
          method: "POST",
          body: JSON.stringify({ movie_id: movieId, rating })
        });
        setStatus(statusEl, "Rating submitted.");
      } catch (err) {
        setStatus(statusEl, err.message);
      }
    });
  }
})();
