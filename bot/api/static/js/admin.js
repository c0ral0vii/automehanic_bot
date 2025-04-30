const API_TOKEN = localStorage.getItem("ADMIN_TOKEN")
const API_BASE = '/api/v1';


async function fetchAPI(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'X-Admin-Token': API_TOKEN,
            ...options.headers
        }
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
}


// document.addEventListener('DOMContentLoaded', () => {
//     loadOverviewStats();
//     setInterval(loadOverviewStats, 30000);
// });
//
//
async function loadOverviewStats() {
    try {
        const stats = await fetchAPI('/stats/overview');
        // document.getElementById('totalUsers').textContent = stats.total_users;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}


class AdminDashboard {
    constructor() {
        this.charts = new DashboardCharts();
        this.updateInterval = 30000;
        this.statsUpdateInterval = 5000; // 5 sec
    }

    async initialize() {
        await this.charts.initializeCharts();
        this.startUpdateCycles();
        this.initializeEventListeners();
    }

    startUpdateCycles() {
        setInterval(() => this.updateAllData(), this.updateInterval);
    }

    initializeEventListeners() {
        document.querySelectorAll('[data-action]').forEach(element => {
            element.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                const id = e.target.dataset.id;
            });
        });
    }

    async updateAllData() {
        try {
            await Promise.all([
                this.charts.updateCharts(),
                loadOverviewStats()
            ]);
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const dashboard = new AdminDashboard();
    await dashboard.initialize();
});


class AdminPanel {
    constructor() {
        this.charts = null;
        this.currentGroupsPage = 1;
        this.groupsPerPage = 50;
        this.searchTerm = '';
        this.initializeEventListeners();
    }

    async initialize() {
        this.charts = new DashboardCharts();

        await this.loadDashboardData();

        // setInterval(() => this.refreshData(), 30000);
    }

    async fetchAPI(endpoint, options = {}) {
        const response = await fetch(`/api/v1${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return response.json();
    }

    async fetchFilesAPI(endpoint, options = {}) {
            const response = await fetch(`/api/v1${endpoint}`, {
                ...options,
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            return response.json();
        }

    async loadItems() {
            try {
                const params = new URLSearchParams({
                    skip: (this.currentGroupsPage - 1) * this.groupsPerPage,
                    limit: this.groupsPerPage,
                    search: this.searchTerm,
                });

                const groupsData = await this.fetchAPI(`/items?${params}`);
                this.updateItemTable(groupsData);

            } catch (error) {
                console.error('Error loading items:', error);
                this.showError('Failed to load items');
            }
        }

    initializeEventListeners() {
        document.getElementById('groupSearch').addEventListener('input', (e) => {
            this.searchTerm = e.target.value;
            this.loadItems();
        });

        document.getElementById('refreshButton').addEventListener('click', () => {
            this.refreshData();
        });

        document.getElementById("catalogUploadForm").addEventListener("submit", async (event) => {
            event.preventDefault();
            const fileInput = document.getElementById('catalogInput');
            if (fileInput.files.length > 0) {
                await this.uploadCatalog(fileInput.files[0]);
            } else {
                alert("Пожалуйста, выберите файл каталога");
            }
        });

        document.getElementById("fileUploadForm").addEventListener("submit", async (event) => {
            event.preventDefault();

            const fileInput = document.getElementById('fileInput');
            if (fileInput.files.length > 0) {
                await this.uploadPresentation(fileInput.files[0]);
            } else {
                alert("Пожалуйста, выберите файл");
            }
        });

        const refreshCatalogButton = document.getElementById('refreshCatalogButton');
        if (refreshCatalogButton) {
            refreshCatalogButton.addEventListener('click', async () => {
                try {
                    let response = await fetch("api/v1/catalog/refresh", {
                        'method': 'GET',
                    });
                    if (response.ok) {
                        await this.refreshData();
                        await this.showToast("Каталог успешно обновлен!");
                    } else {
                        let error = await response.json();
                        await this.showError("Ошибка обновления каталога: " + error.detail);
                    }
                } catch (error) {
                    await this.showError("Ошибка обновления каталога: " + error.message);
                }
            });
        } else {
            console.error('Element with ID "refreshCatalogButton" not found.');
        }

    }

    async uploadCatalog(file) {
        const modal = bootstrap.Modal.getInstance(document.getElementById('catalogUploadModal'));

        try {
            let formData = new FormData();
            formData.append("file", file);

            let response = await fetch("/api/v1/upload_catalog/", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                let error = await response.json();
                console.error("Ошибка загрузки:", error);
                alert("Ошибка загрузки: " + (error.detail || error.message));
            } else {
                let result = await response.json();
                alert("Файл успешно загружен: " + result.filename);
                // Можно добавить обновление данных каталога здесь
                // await this.loadCatalogData();
            }
        } catch (error) {
            console.error("Ошибка сети:", error);
            alert("Ошибка сети: " + error.message);
        } finally {
            modal.hide(); // Закрываем модальное окно в любом случае
            document.getElementById('catalogInput').value = ''; // Очищаем поле выбора файла
        }
    }

    async uploadPresentation(file, retry_count = 1, max_retries = 5) {
        const modal = bootstrap.Modal.getInstance(document.getElementById('fileUploadModal'));
    
        try {
            let formData = new FormData();
            formData.append("file", file);
    
            let response = await fetch("/api/v1/upload_presentation/", {
                method: "POST",
                body: formData
            });
    
            if (!response.ok) {
                let error = await response.json();
                console.error("Ошибка загрузки:", error);
                alert("Ошибка загрузки: " + error.detail);
                throw new Error(error.detail);
            } else {
                let result = await response.json();
                alert("Файл успешно загружен: " + result.filename);
                await this.loadDashboardData();
            }
        } catch (error) {
            if (retry_count >= max_retries) {
                console.error("Ошибка после всех попыток:", error);
                alert("Ошибка после " + max_retries + " попыток: " + error.message);
            } else {
                console.log(`Попытка ${retry_count} из ${max_retries} не удалась, повтор через 1 секунду...`);
                await new Promise(resolve => setTimeout(resolve, 1000)); // Задержка 1 секунда
                await this.uploadPresentation(file, retry_count + 1, max_retries);
            }
        } finally {
            modal.hide(); // Закрываем модальное окно в любом случае
            document.getElementById('fileInput').value = ''; // Очищаем поле выбора файла
        }
    }

    async loadDashboardData() {
        try {
            this.showLoader();

            const [overviewData, itemData, presentations] = await Promise.all([
                fetchAPI('/stats/overview'),
                fetchAPI('/items'),
                fetchAPI('/presentations/')
            ]);

            this.updateOverviewStats(overviewData);
            this.updateItemTable(itemData);
            this.updatePresentation(presentations);

            this.updateLastUpdateTime();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        } finally {
            this.hideLoader();
        }
    }

    showLoader() {
        document.getElementById('loader').classList.add('active');
    }

    hideLoader() {
        document.getElementById('loader').classList.remove('active');
    }

    showError(message) {
        alert(message);
    }

    updateLastUpdateTime() {
        const now = new Date();
        document.getElementById('lastUpdateTime').textContent = now.toLocaleTimeString();
    }

    updateOverviewStats(data) {
        document.getElementById('totalUsers').textContent = data.total_users;
        document.getElementById('activeToday').textContent = data.active_today;

        const statusElement = document.getElementById('systemStatus');
        statusElement.textContent = data.system_status;
        statusElement.className = `status-${data.system_status.toLowerCase()}`;
    }

     async refreshData() {
        console.log('refresh');
        await this.loadDashboardData();
    }

    async getMoreInfo(item_id) {
        const data = await this.fetchAPI(`/items/${item_id}/info`)
        console.log(data)
        document.getElementById('name').value = data.name;
        document.getElementById('itemArticle').value = data.article;
        document.getElementById('crossNumber').value = data.cross_number;
        document.getElementById('amount').value = data.amount;
        document.getElementById('default_price').value = data.default_price;
        document.getElementById('first_price').value = data.first_price;
        document.getElementById('second_lvl_price').value = data.second_lvl_price;
        document.getElementById('third_lvl_price').value = data.third_lvl_price;
        document.getElementById('fourth_lvl_price').value = data.fourth_lvl_price;
        document.getElementById('brand').value = data.brand;
        document.getElementById('product_group').value = data.product_group;
        document.getElementById('part_type').value = data.part_type;
        document.getElementById('photo_url_1').value = data.photo_url_1;
        document.getElementById('photo_url_2').value = data.photo_url_2;
        document.getElementById('photo_url_3').value = data.photo_url_3;
        document.getElementById('photo_url_4').value = data.photo_url_4;
        document.getElementById('applicability_brands').value = data.applicability_brands;
        document.getElementById('applicable_tech').value = data.applicable_tech;
        document.getElementById('weight_kg').value = data.weight_kg;
        document.getElementById('length_m').value = data.length_m;
        document.getElementById('inner_diameter_mm').value = data.inner_diameter_mm;
        document.getElementById('outer_diameter_mm').value = data.outer_diameter_mm;
        document.getElementById('thread_diameter_mm').value = data.thread_diameter_mm;
        document.getElementById('width_m').value = data.width_m;
        document.getElementById('height_m').value = data.height_m;
        const modal = new bootstrap.Modal(document.getElementById('editModal'));

        document.getElementById("saveItemButton").onclick = function () {
            adminPanel.saveChange(item_id);
        };

        modal.show();

        await this.loadDashboardData()
    }

    async deleteItem(item_id) {

        await this.fetchAPI(`/items/${item_id}/delete`, {method: 'DELETE'})

        await this.showToast("Удаление произошло успешно")
        await this.loadDashboardData()
    }

    async saveChange(item_id) {
        try {
            let updatedData = {
                "name": document.getElementById('name').value,
                "article_number": document.getElementById('itemArticle').value,
                "cross_numbers": document.getElementById('crossNumber').value,
                "amount": document.getElementById('amount').value,
                "default_price": document.getElementById('default_price').value,
                "first_lvl_price": document.getElementById('first_price').value,
                "second_lvl_price": document.getElementById('second_lvl_price').value,
                "third_lvl_price": document.getElementById('third_lvl_price').value,
                "fourth_lvl_price": document.getElementById('fourth_lvl_price').value,
                "brand": document.getElementById('brand').value,
                "product_group": document.getElementById('product_group').value,
                "part_type": document.getElementById('part_type').value,
                "photo_url_1": document.getElementById('photo_url_1').value,
                "photo_url_2": document.getElementById('photo_url_2').value,
                "photo_url_3": document.getElementById('photo_url_3').value,
                "photo_url_4": document.getElementById('photo_url_4').value,
                "applicability_brands": document.getElementById('applicability_brands').value,
                "applicable_tech": document.getElementById('applicable_tech').value,
                "weight_kg": document.getElementById('weight_kg').value,
                "length_m": document.getElementById('length_m').value,
                "inner_diameter_mm": document.getElementById('inner_diameter_mm').value,
                "outer_diameter_mm": document.getElementById('outer_diameter_mm').value,
                "thread_diameter_mm": document.getElementById('thread_diameter_mm').value,
                "width_m": document.getElementById('width_m').value,
                "height_m": document.getElementById('height_m').value,
            };

            const response = await this.fetchAPI(`/items/${item_id}/change`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedData),
            });

            await this.showToast("Изменения успешно занесены");
            await this.loadDashboardData();
        } catch (error) {
            console.error('Error saving changes:', error);
            this.showError('Не удалось сохранить изменения');
        }
    }

    async showToast(message) {
        const toastContainer = document.getElementById('toastContainer');

        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-bg-success border-0 position-relative';
        toast.role = 'alert';
        toast.ariaLive = 'assertive';
        toast.ariaAtomic = 'true';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        const bootstrapToast = new bootstrap.Toast(toast, {
            delay: 2000
        });
        bootstrapToast.show();

        // Optional: Remove the toast after it’s hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    updatePresentation(data) {
        const tbody = document.querySelector('#presentationsTable tbody');
        tbody.innerHTML = '';

        data.items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.name}</td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-danger" data-action="delete" data-id="${item.name}">
                            Удалить
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        tbody.querySelectorAll('[data-action="delete"]').forEach(button => {
            button.addEventListener('click', (e) => {
                const itemId = e.target.dataset.id;
                this.deletePresentation(itemId);
            });
        });
    }

    async deletePresentation(item_id) {
        try {
            const response = await fetch(`/api/v1/presentations/${item_id}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error('Failed to delete presentation');
            }

            await this.showToast("Презентация успешно удалена");
            await this.loadDashboardData(); // Refresh the dashboard data
        } catch (error) {
            console.error('Error deleting presentation:', error);
            this.showError('Failed to delete presentation');
            await this.loadDashboardData();
        }
    }

    updateItemTable(data) {
        const tbody = document.querySelector('#groupsTable tbody');
        tbody.innerHTML = '';

        data.items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.article}</td>
                <td>${item.cross_article}</td>
                <td>${item.name}</td>
                <td>${item.count}</td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-primary" data-action="edit" data-id="${item.id}">
                            Изменить
                        </button>
                        <button class="btn btn-sm btn-danger" data-action="delete" data-id="${item.id}">
                            Удалить
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        // Attach event listeners
        tbody.querySelectorAll('[data-action="edit"]').forEach(button => {
            button.addEventListener('click', (e) => {
                const itemId = e.target.dataset.id;
                this.getMoreInfo(itemId);
            });
        });

        tbody.querySelectorAll('[data-action="delete"]').forEach(button => {
            button.addEventListener('click', (e) => {
                const itemId = e.target.dataset.id;
                this.deleteItem(itemId);
            });
        });

        this.updatePagination(data.total, data.page, data.total_pages);
    }

    updatePagination(total, currentPage, totalPages) {
        const pagination = document.getElementById('groupsPagination');
        pagination.innerHTML = '';

        document.getElementById('showingCount').textContent = Math.min(this.groupsPerPage, total);
        document.getElementById('totalCount').textContent = total;

        if (totalPages > 1) {
            const pages = [];

            pages.push(1);

            for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
                pages.push(i);
            }

            if (totalPages > 1) {
                pages.push(totalPages);
            }

            pages.forEach((page, index) => {
                if (index > 0 && pages[index] - pages[index - 1] > 1) {
                    pagination.appendChild(this.createPaginationItem('...', false));
                }
                pagination.appendChild(this.createPaginationItem(page, page === currentPage));
            });
        }
    }

    createPaginationItem(text, isActive) {
        const li = document.createElement('li');
        li.className = `page-item${isActive ? ' active' : ''}`;

        const a = document.createElement('a');
        a.className = 'page-link';
        a.href = '#';
        a.textContent = text;

        if (text !== '...') {
            a.onclick = (e) => {
                e.preventDefault();
                this.currentGroupsPage = parseInt(text);
                this.loadItems();
            };
        }

        li.appendChild(a);
        return li;
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    window.adminPanel = new AdminPanel(); // Attach to window
    await adminPanel.initialize();
});