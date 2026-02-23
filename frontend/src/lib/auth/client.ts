/**
 * Authentication API Client
 * 
 * Handles API calls to backend authentication endpoints
 */

const API_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'

export interface User {
  id: string
  email: string
  full_name?: string
  is_active: boolean
  is_verified: boolean
  last_login_at?: string
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface AuthError {
  detail: string
}

class AuthAPI {
  private baseUrl: string

  constructor() {
    this.baseUrl = `${API_URL}/api`
  }

  /**
   * Sign up a new user
   */
  async signup(email: string, password: string, fullName?: string): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    })

    if (!response.ok) {
      const error: AuthError = await response.json()
      throw new Error(error.detail || 'Signup failed')
    }

    return response.json()
  }

  /**
   * Sign in with email and password
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    })

    if (!response.ok) {
      const error: AuthError = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    return response.json()
  }

  /**
   * Get current user from token
   */
  async getCurrentUser(token: string): Promise<User> {
    const response = await fetch(`${this.baseUrl}/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error: AuthError = await response.json()
      throw new Error(error.detail || 'Failed to get user')
    }

    return response.json()
  }

  /**
   * Logout (client-side token removal)
   */
  async logout(token: string): Promise<void> {
    await fetch(`${this.baseUrl}/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
  }
}

export const authAPI = new AuthAPI()
