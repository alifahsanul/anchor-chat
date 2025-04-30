const ENV = {
    development: {
        backendURL: 'http://127.0.0.1:8000'
    },
    production: {
        backendURL: 'https://anchor-chat-production.up.railway.app'
    }
};

// Automatically detect environment based on hostname
const config = {
    get backendURL() {
        // Check if we're on localhost or local IP
        if (window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1' ||
            window.location.hostname.includes('192.168.')) {
            return ENV.development.backendURL;
        }
        return ENV.production.backendURL;
    }
};

export default config;