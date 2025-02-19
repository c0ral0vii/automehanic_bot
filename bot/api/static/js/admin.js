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

    getMoreInfo(item_id) {
        const data = this.fetchAPI(`/users/${item_id}/info`)

        document.getElementById('itemName').value = 'Item ' + item_id;
        document.getElementById('itemDescription').value = 'Description for item ' + item_id;

        const modal = new bootstrap.Modal(document.getElementById('editModal'));
        modal.show();
    }

    deleteItem(item_id) {

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
                                onclick="adminPanel.deleteItem()">
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