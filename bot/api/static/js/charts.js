class DashboardCharts {
    constructor() {
        this.charts = {};
        this.currentPeriod = '24h';
    }

    async initializeCharts() {
        await this.createActivityChart();
        await this.createUsersChart();
    }

    async createActivityChart() {
        const ctx = document.getElementById('activityChart').getContext('2d');
        const data = await this.fetchActivityData();
        console.log(data)

        this.charts.activity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Активность',
                    data: data.values,
                    borderColor: 'rgb(50,186,186)',
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    async createUsersChart() {
        const ctx = document.getElementById('usersChart').getContext('2d');
        const data = await this.fetchUsersChartsData();

        this.charts.users = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ["Авторизованные", "Не авторизованные"],
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        'rgb(0,115,62)',
                        'rgb(8,11,116)',
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    async fetchActivityData() {
        try {
            const response = await fetch('/api/v1/analytics/activity');
            return await response.json();
        } catch (error) {
            console.error('Error fetching activity data:', error);
            return { labels: [], values: [] };
        }
    }

    async fetchUsersChartsData() {
        try {
            const response = await fetch('/api/v1/analytics/users');
            return await response.json();
        } catch (error) {
            console.error('Error fetching activity data:', error);
            return { values: [] };
        }
    }

    async updateCharts() {
        const activityData = await this.fetchActivityData();
        const users_chartsData = await this.fetchUsersChartsData();

        if (this.charts.activity) {
            this.charts.activity.data.labels = activityData.labels;
            this.charts.activity.data.datasets[0].data = activityData.values;
            this.charts.activity.update();
        }

        if (this.charts.users) {
            this.charts.users.data.datasets[0].data = users_chartsData.values;
            this.charts.users.update();
        }
    }

    async updateActivityPeriod(period) {
        this.currentPeriod = period;
        await this.updateCharts();
    }

}