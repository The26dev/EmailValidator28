// Example module registrations

import { moduleRegistry } from './module-registry-updated';
import { errorSystem } from '../systems/error-system-updated';
import { securitySystem } from '../systems/security_updated';

// Register error handling system
moduleRegistry.register('errorSystem', {
    dependencies: [],
    hooks: {
        beforeInit: () => console.log('Initializing error system...'),
        afterInit: () => console.log('Error system initialized'),
        cleanup: () => console.log('Cleaning up error system...')
    }
}, errorSystem);

// Register security system with dependency on error system
moduleRegistry.register('securitySystem', {
    dependencies: ['errorSystem'],
    hooks: {
        beforeInit: () => console.log('Initializing security system...'),
        afterInit: () => console.log('Security system initialized'),
        cleanup: () => console.log('Cleaning up security system...')
    }
}, securitySystem);

// Example usage
async function initializeApplication() {
    try {
        await moduleRegistry.initialize();
        console.log('Application initialized successfully');
        
        // Get module states
        console.log('Module states:', moduleRegistry.getModuleStates());
        
        // Use registered modules
        const security = moduleRegistry.getModule('securitySystem');
        await security.validateCurrentSession();
    } catch (error) {
        console.error('Application initialization failed:', error);
    }
}

// Cleanup on application shutdown
async function shutdownApplication() {
    await moduleRegistry.cleanup();
    console.log('Application shutdown complete');
}