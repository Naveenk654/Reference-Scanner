// API Configuration
// In production, this will use VITE_API_URL from environment variables
// In development, it defaults to localhost:8002

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

export default API_URL;

