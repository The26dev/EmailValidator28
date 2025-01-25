class AuthSystem {
    constructor() {
        this.token = null;
        this.tokenExpiry = null;
        this.refreshInterval = null;
        this.initializeAuth();
    }

    async initializeAuth() {
        const token = localStorage.getItem('authToken');
        if (token) {
            try {
                await this.validateAndSetToken(token);
            } catch (error) {
                console.error('Error initializing auth:', error);
                this.clearAuth();
            }
        }
    }

    async validateAndSetToken(token) {
        const response = await fetch('/api/auth/validate', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Token validation failed');
        }

        const data = await response.json();
        if (data.valid) {
            this.setAuth(token, data.expiry);
            return true;
        }
        return false;
    }

    setAuth(token, expiry) {
        this.token = token;
        this.tokenExpiry = new Date(expiry);
        localStorage.setItem('authToken', token);
        
        this.setupAutoRefresh();
    }

    clearAuth() {
        this.token = null;
        this.tokenExpiry = null;
        localStorage.removeItem('authToken');
        
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    setupAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(() => {
            const timeUntilExpiry = this.tokenExpiry - new Date();
            if (timeUntilExpiry < 5 * 60 * 1000) { // Refresh if less than 5 minutes until expiry
                this.refreshToken().catch(console.error);
            }
        }, 60 * 1000); // Check every minute
    }

    async refreshToken() {
        try {
            const response = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            this.setAuth(data.token, data.expiry);
            return true;
        } catch (error) {
            console.error('Error refreshing token:', error);
            this.clearAuth();
            this.redirectToLogin();
            return false;
        }
    }

    async login(credentials) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(credentials)
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            this.setAuth(data.token, data.expiry);
            return true;
        } catch (error) {
            console.error('Login error:', error);
            return false;
        }
    }

    logout() {
        this.clearAuth();
        this.redirectToLogin();
    }

    redirectToLogin() {
        window.location.href = '/login';
    }

    getAuthHeaders() {
        if (!this.token) {
            return {};
        }
        return {
            'Authorization': `Bearer ${this.token}`
        };
    }

    isAuthenticated() {
        return !!this.token && this.tokenExpiry > new Date();
    }

    hasRole(role) {
        if (!this.token) {
            return false;
        }
        
        try {
            const payload = this.decodeToken(this.token);
            return payload.roles && payload.roles.includes(role);
        } catch (error) {
            console.error('Error checking role:', error);
            return false;
        }
    }

    decodeToken(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            return JSON.parse(window.atob(base64));
        } catch (error) {
            console.error('Error decoding token:', error);
            return {};
        }
    }

    async validatePermission(permission) {
        try {
            const response = await fetch('/api/auth/validate-permission', {
                method: 'POST',
                headers: {
                    ...this.getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ permission })
            });

            if (!response.ok) {
                throw new Error('Permission validation failed');
            }

            const data = await response.json();
            return data.hasPermission;
        } catch (error) {
            console.error('Error validating permission:', error);
            return false;
        }
    }

    onAuthStateChange(callback) {
        window.addEventListener('storage', (event) => {
            if (event.key === 'authToken') {
                callback(this.isAuthenticated());
            }
        });
        return () => {
            window.removeEventListener('storage', callback);
        };
    }
}