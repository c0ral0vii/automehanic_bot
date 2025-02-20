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

        document.querySelectorAll('[data-period]').forEach(button => {
            button.addEventListener('click', (e) => {
                const period = e.target.dataset.period;
                this.charts.updateActivityPeriod(period);
            });
        });
    }

    async loadDashboardData() {
        try {
            this.showLoader();

            const [overviewData, itemData] = await Promise.all([
                fetchAPI('/stats/overview'),
                fetchAPI('/items'),
            ]);

            this.updateOverviewStats(overviewData);
            this.updateItemTable(itemData)


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
        }
        await this.fetchAPI(`/items/${item_id}/change`, {method: 'PUT', body: JSON.stringify(updatedData)})
        await this.showToast("Изменения успешно занесены")
        await this.loadDashboardData()
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
                        <button class="btn btn-sm btn-outline-primary"
                            onclick="adminPanel.getMoreInfo(${item.id})">
                            Изменить
                        </button>
                        <button class="btn btn-sm btn-danger"
                                onclick="adminPanel.deleteItem(${item.id})">
                                Удалить
                        </button>
                    </div>
                </td>
                
            `;
            tbody.appendChild(row);
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

let adminPanel;
document.addEventListener('DOMContentLoaded', async () => {
    adminPanel = new AdminPanel();
    await adminPanel.initialize();
});