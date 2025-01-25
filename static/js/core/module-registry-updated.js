// Enhanced Module Registry System

class ModuleRegistry {
    constructor() {
        this.modules = new Map();
        this.dependencies = new Map();
        this.lifecycleHooks = new Map();
        this.moduleStates = new Map();
        this.initializationOrder = [];
    }

    /**
     * Register a module with its dependencies and lifecycle hooks
     * @param {string} moduleName - Unique identifier for the module
     * @param {Object} moduleConfig - Module configuration
     * @param {Array<string>} moduleConfig.dependencies - List of module dependencies
     * @param {Object} moduleConfig.hooks - Lifecycle hooks for the module
     * @param {Function} moduleInstance - The module instance or constructor
     */
    register(moduleName, moduleConfig, moduleInstance) {
        if (this.modules.has(moduleName)) {
            throw new Error(`Module ${moduleName} is already registered`);
        }

        // Validate module configuration
        this._validateModuleConfig(moduleConfig);

        // Store module information
        this.modules.set(moduleName, moduleInstance);
        this.dependencies.set(moduleName, moduleConfig.dependencies || []);
        this.lifecycleHooks.set(moduleName, moduleConfig.hooks || {});
        this.moduleStates.set(moduleName, 'registered');

        // Log registration
        console.log(`Module ${moduleName} registered successfully`);
    }

    /**
     * Initialize all registered modules in the correct order
     */
    async initialize() {
        try {
            // Calculate initialization order
            this.initializationOrder = this._calculateInitOrder();
            
            // Initialize modules in order
            for (const moduleName of this.initializationOrder) {
                await this._initializeModule(moduleName);
            }

            console.log('All modules initialized successfully');
        } catch (error) {
            console.error('Module initialization failed:', error);
            throw error;
        }
    }

    /**
     * Get a module instance by name
     * @param {string} moduleName - Name of the module to retrieve
     */
    getModule(moduleName) {
        if (!this.modules.has(moduleName)) {
            throw new Error(`Module ${moduleName} not found`);
        }
        return this.modules.get(moduleName);
    }

    /**
     * Calculate the correct initialization order based on dependencies
     */
    _calculateInitOrder() {
        const visited = new Set();
        const initOrder = [];
        const visiting = new Set();

        const visit = (moduleName) => {
            if (visiting.has(moduleName)) {
                throw new Error(`Circular dependency detected: ${moduleName}`);
            }
            if (visited.has(moduleName)) {
                return;
            }

            visiting.add(moduleName);

            const dependencies = this.dependencies.get(moduleName) || [];
            for (const dep of dependencies) {
                if (!this.modules.has(dep)) {
                    throw new Error(`Missing dependency: ${dep} required by ${moduleName}`);
                }
                visit(dep);
            }

            visiting.delete(moduleName);
            visited.add(moduleName);
            initOrder.push(moduleName);
        };

        for (const moduleName of this.modules.keys()) {
            visit(moduleName);
        }

        return initOrder;
    }

    /**
     * Initialize a single module
     * @param {string} moduleName - Name of the module to initialize
     */
    async _initializeModule(moduleName) {
        const module = this.modules.get(moduleName);
        const hooks = this.lifecycleHooks.get(moduleName);

        try {
            // Pre-initialization hook
            if (hooks.beforeInit) {
                await hooks.beforeInit();
            }

            // Initialize module
            if (typeof module.initialize === 'function') {
                await module.initialize();
            }

            // Post-initialization hook
            if (hooks.afterInit) {
                await hooks.afterInit();
            }

            this.moduleStates.set(moduleName, 'initialized');
            console.log(`Module ${moduleName} initialized successfully`);
        } catch (error) {
            this.moduleStates.set(moduleName, 'failed');
            console.error(`Failed to initialize module ${moduleName}:`, error);
            throw error;
        }
    }

    /**
     * Validate module configuration
     * @param {Object} config - Module configuration to validate
     */
    _validateModuleConfig(config) {
        if (!config) {
            throw new Error('Module configuration is required');
        }

        if (config.dependencies && !Array.isArray(config.dependencies)) {
            throw new Error('Module dependencies must be an array');
        }

        if (config.hooks && typeof config.hooks !== 'object') {
            throw new Error('Module hooks must be an object');
        }
    }

    /**
     * Get the current state of all modules
     */
    getModuleStates() {
        return Object.fromEntries(this.moduleStates);
    }

    /**
     * Clean up all modules
     */
    async cleanup() {
        for (const moduleName of [...this.initializationOrder].reverse()) {
            const hooks = this.lifecycleHooks.get(moduleName);
            if (hooks.cleanup) {
                try {
                    await hooks.cleanup();
                    console.log(`Module ${moduleName} cleaned up successfully`);
                } catch (error) {
                    console.error(`Failed to clean up module ${moduleName}:`, error);
                }
            }
        }
    }
}

// Export as singleton
export const moduleRegistry = new ModuleRegistry();