
const API = {
    projects: "/users/dashboard/get-accesses",
    addProject: "/users/dashboard/add-project",
};

const ANALYTICS_URL = (projectId) => `/dashboard/${projectId}/`;

document.addEventListener("DOMContentLoaded", () => {
    const projectForm = document.querySelector("#add-project-form");
    const apiKeyInput = document.querySelector("#api-key");
    const projectsList = document.querySelector("#projects-list");
    const emptyState = document.querySelector("#empty-state");
    const submitButton = document.querySelector("#submit-button");

    if (!projectForm || !apiKeyInput || !projectsList || !emptyState || !submitButton) {
        console.error("Не найдены необходимые элементы страницы.");
        return;
    }

    projectForm.addEventListener("submit", addProject);

    loadProjects();

    const projectsCount = document.querySelector("#projects-count");

    function updateProjectsCount(count) {
        projectsCount.textContent = String(count);
    }

    async function loadProjects() {
        try {
            const response = await fetch(API.projects, {
                method: "GET",
                credentials: "include",
                headers: {
                    Accept: "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(
                    `Ошибка загрузки проектов: ${response.status}`
                );
            }

            const projects = await response.json();

            renderProjects(projects);
        } catch (error) {
            console.error(error);
            showError("Не удалось загрузить проекты");
        }
    }

    async function addProject(event) {
        event.preventDefault();

        console.log("submit");

        const apiKey = apiKeyInput.value.trim();

        if (!apiKey) {
            apiKeyInput.focus();
            return;
        }

        setLoading(true);

        try {
            const response = await fetch(API.addProject, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                },
                body: JSON.stringify({
                    api_key: apiKey,
                }),
            });

            if (!response.ok) {
                let errorMessage = `Ошибка добавления проекта: ${response.status}`;

                try {
                    const errorData = await response.json();

                    if (errorData.detail) {
                        errorMessage = errorData.detail;
                    } else if (errorData.message) {
                        errorMessage = errorData.message;
                    }
                } catch {
                    // Сервер мог вернуть не JSON
                }

                throw new Error(errorMessage);
            }

            const data = await response.json();

            console.log("Проект добавлен:", data);

            if (!data.id) {
                throw new Error("Сервер не вернул ID проекта");
            }

            addProjectCard(data.id);

            apiKeyInput.value = "";
        } catch (error) {
            console.error(error);
            showError(error.message || "Не удалось добавить проект");
        } finally {
            setLoading(false);
        }
    }

    function renderProjects(projects) {
        projectsList.innerHTML = "";

        const validProjects = Array.isArray(projects)
            ? projects.filter(project => project && project.id)
            : [];

        if (validProjects.length === 0) {
            emptyState.hidden = false;
            updateProjectsCount(0);
            return;
        }

        emptyState.hidden = true;

        validProjects.forEach(project => {
            addProjectCard(project.id,project.title);
        });

        updateProjectsCount(projectsList.children.length);
    }

    function addProjectCard(projectId,projectTitle) {
        emptyState.hidden = true;

        const card = document.createElement("a");

        card.className = "project-card";
        card.href = ANALYTICS_URL(projectId);

        card.innerHTML = `
            <div class="project-card__content">
                <span class="project-card__label">Проект</span>
                <span class="project-card__id">
                    ${escapeHtml(projectTitle)}
                </span>
            </div>

            <svg
                class="project-card__arrow"
                width="18"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    d="M6.75 3.75L12 9L6.75 14.25"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                />
            </svg>
        `;

        projectsList.appendChild(card);
        updateProjectsCount(projectsList.children.length);
    }

    function setLoading(isLoading) {
        submitButton.disabled = isLoading;

        if (isLoading) {
            submitButton.dataset.originalText =
                submitButton.textContent;
            submitButton.textContent = "Добавление...";
        } else {
            submitButton.textContent =
                submitButton.dataset.originalText || "Добавить";
        }
    }

    function showError(message) {
        console.error(message);

        // Пока оставляем консоль.
        // Здесь можно подключить ваш UI для отображения ошибки.
    }

    function escapeHtml(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }
});

