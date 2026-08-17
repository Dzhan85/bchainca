import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';

export interface User {
  username: string;
  email: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;
  private readonly TOKEN_KEY = 'auth_token';
  private readonly USER_KEY = 'current_user';

  // Demo users - In production, this would be handled by backend API
  private readonly DEMO_USERS = [
    { username: 'admin', password: 'admin123', email: 'admin@bchainca.com', role: 'Administrator' },
    { username: 'user', password: 'user123', email: 'user@bchainca.com', role: 'User' },
    { username: 'operator', password: 'operator123', email: 'operator@bchainca.com', role: 'Operator' }
  ];

  constructor(private router: Router) {
    const storedUser = localStorage.getItem(this.USER_KEY);
    this.currentUserSubject = new BehaviorSubject<User | null>(
      storedUser ? JSON.parse(storedUser) : null
    );
    this.currentUser = this.currentUserSubject.asObservable();
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  public get isAuthenticated(): boolean {
    return !!this.currentUserSubject.value && !!localStorage.getItem(this.TOKEN_KEY);
  }

  login(username: string, password: string): Observable<boolean> {
    return new Observable(observer => {
      // Simulate API call delay
      setTimeout(() => {
        const user = this.DEMO_USERS.find(
          u => u.username === username && u.password === password
        );

        if (user) {
          const { password, ...userWithoutPassword } = user;
          const token = this.generateToken(username);

          localStorage.setItem(this.TOKEN_KEY, token);
          localStorage.setItem(this.USER_KEY, JSON.stringify(userWithoutPassword));
          this.currentUserSubject.next(userWithoutPassword);

          observer.next(true);
          observer.complete();
        } else {
          observer.next(false);
          observer.complete();
        }
      }, 500);
    });
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private generateToken(username: string): string {
    // Simple token generation - In production, use JWT from backend
    const timestamp = new Date().getTime();
    return btoa(`${username}:${timestamp}`);
  }

  // Check if token is expired (demo - always returns false)
  isTokenExpired(): boolean {
    return false;
  }
}
