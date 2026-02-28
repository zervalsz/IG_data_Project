/**
 * API Configuration
 * Centralized configuration for API base URL
 */

/**
 * Get the API base URL dynamically
 * - For production: Use environment variable
 * - For GitHub Codespaces: Construct from window.location
 * - For local development: Use localhost:5000
 */
export function getApiBaseUrl(): string {
  // Server-side or build time: use environment variable
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
  }
  
  // Client-side: check for GitHub Codespaces
  if (window.location.hostname.includes('github.dev')) {
    return window.location.origin.replace('-3000.', '-5000.');
  }
  
  // Client-side: use environment variable or localhost
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
}

// Export a constant for use in API routes (server-side)
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
