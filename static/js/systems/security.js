// Security System Implementation

class SecuritySystem {
    constructor() {
        this.accessToken = null;
        this.refreshToken = null;
    }

    // Initialize the security system
    async initialize() {
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        
        // Check if tokens need refresh
        if (this.accessToken) {
            const isValid = await this.validateToken(this.accessToken);
            if (!isValid && this.refreshToken) {
                await this.refreshAccessToken();
            }
        }
    }

    // Store authentication tokens
    setTokens(accessToken, refreshToken) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
    }

    // Clear authentication tokens
    clearTokens() {
        this.accessToken = null;
        this.refreshToken = null;
        
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    // Validate JWT token
    async validateToken(token) {
        try {
            const response = await fetch('/api/auth/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
            return response.ok;
        } catch (error) {
            console.error('Token validation error:', error);
            return false;
        }
    }

    // Refresh access token using refresh token
    async refreshAccessToken() {
        try {
            const response = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.refreshToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access_token, null);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Token refresh error:', error);
            this.clearTokens();
            return false;
        }
    }

    // Get authorization header for API requests
    getAuthHeader() {
        return this.accessToken ? { 'Authorization': `Bearer ${this.accessToken}` } : {};
    }

    // Add authentication to fetch requests
    async authenticatedFetch(url, options = {}) {
        const headers = {
            ...options.headers,
            ...this.getAuthHeader()
        };

        try {
            let response = await fetch(url, { ...options, headers });
            
            // Handle 401 by attempting token refresh
            if (response.status === 401 && this.refreshToken) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    headers.Authorization = `Bearer ${this.accessToken}`;
                    response = await fetch(url, { ...options, headers });
                }
            }
            
            return response;
        } catch (error) {
            console.error('Authenticated fetch error:', error);
            throw error;
        }
    }

    // Login user
    async login(credentials) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(credentials)
            });

            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access_token, data.refresh_token);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Login error:', error);
            return false;
        }
    }

    // Logout user
    async logout() {
        try {
            if (this.accessToken) {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: this.getAuthHeader()
                });
            }
        } finally {
            this.clearTokens();
        }
    }
}

// Export singleton instance
const securitySystem = new SecuritySystem();
export default securitySystem;