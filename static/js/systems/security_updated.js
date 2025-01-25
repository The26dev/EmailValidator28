// Enhanced Security System Implementation

class SecuritySystem {
    constructor() {
        this.tokenStorage = window.sessionStorage; // More secure than localStorage
        this.csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    }

    async initialize() {
        try {
            await this.validateCurrentSession();
            this.setupSecurityHeaders();
            this.initializeCSRFProtection();
        } catch (error) {
            console.error('Security system initialization failed:', error);
            throw error;
        }
    }

    setupSecurityHeaders() {
        // Add security headers to all requests
        axios.defaults.headers.common['X-Content-Type-Options'] = 'nosniff';
        axios.defaults.headers.common['X-Frame-Options'] = 'DENY';
        axios.defaults.headers.common['X-XSS-Protection'] = '1; mode=block';
        if (this.csrfToken) {
            axios.defaults.headers.common['X-CSRF-Token'] = this.csrfToken;
        }
    }

    initializeCSRFProtection() {
        const tokenElement = document.querySelector('meta[name="csrf-token"]');
        if (tokenElement) {
            axios.defaults.headers.common['X-CSRF-Token'] = tokenElement.content;
        }
    }

    setTokens(accessToken, refreshToken) {
        if (!accessToken || !refreshToken) {
            throw new Error('Invalid token data');
        }
        
        // Store tokens securely
        this.tokenStorage.setItem('accessToken', this._encryptToken(accessToken));
        this.tokenStorage.setItem('refreshToken', this._encryptToken(refreshToken));
    }

    clearTokens() {
        this.tokenStorage.removeItem('accessToken');
        this.tokenStorage.removeItem('refreshToken');
    }

    async validateToken(token) {
        try {
            const response = await axios.post('/api/auth/validate', { token });
            return response.data.valid;
        } catch (error) {
            console.error('Token validation failed:', error);
            return false;
        }
    }

    _encryptToken(token) {
        // Implementation of token encryption
        // This is a placeholder - actual implementation would use WebCrypto API
        return token;
    }

    _decryptToken(encryptedToken) {
        // Implementation of token decryption
        // This is a placeholder - actual implementation would use WebCrypto API
        return encryptedToken;
    }

    async refreshAccessToken() {
        const refreshToken = this._decryptToken(this.tokenStorage.getItem('refreshToken'));
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        try {
            const response = await axios.post('/api/auth/refresh', { refreshToken });
            const { accessToken, newRefreshToken } = response.data;
            this.setTokens(accessToken, newRefreshToken);
            return accessToken;
        } catch (error) {
            console.error('Token refresh failed:', error);
            this.clearTokens();
            throw error;
        }
    }

    getAuthHeader() {
        const accessToken = this._decryptToken(this.tokenStorage.getItem('accessToken'));
        return accessToken ? `Bearer ${accessToken}` : '';
    }

    async authenticatedFetch(url, options = {}) {
        const headers = {
            ...options.headers,
            'Authorization': this.getAuthHeader(),
            'X-CSRF-Token': this.csrfToken
        };

        try {
            const response = await fetch(url, { ...options, headers });
            
            if (response.status === 401) {
                // Token expired, attempt refresh
                await this.refreshAccessToken();
                headers.Authorization = this.getAuthHeader();
                return fetch(url, { ...options, headers });
            }
            
            return response;
        } catch (error) {
            console.error('Authenticated fetch failed:', error);
            throw error;
        }
    }

    sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        return input
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\//g, '&#x2F;');
    }

    validatePassword(password) {
        const minLength = 12;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        
        return password.length >= minLength &&
            hasUpperCase &&
            hasLowerCase &&
            hasNumbers &&
            hasSpecialChars;
    }
}

// Export as singleton
export const securitySystem = new SecuritySystem();