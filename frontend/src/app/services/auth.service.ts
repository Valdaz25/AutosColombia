
import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { catchError, switchMap, tap, throwError } from 'rxjs';

import { API_BASE_URL } from './api.service';

export interface LoginRequest {
  nombre_usuario: string;
  password: string;
}

export interface TokenRespuesta {
  access_token: string;
  token_type: string;
}

export interface Usuario {
  id: number;
  nombre_usuario: string;
  rol: 'ADMINISTRADOR' | 'OPERADOR';
  operador_id: number | null;
  activo: boolean;
  creado_en: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly base = inject(API_BASE_URL);

  readonly currentUser = signal<Usuario | null>(null);

  login(credentials: LoginRequest) {
    return this.http
      .post<TokenRespuesta>(`${this.base}/auth/login`, credentials)
      .pipe(
        tap((response) => {
          sessionStorage.setItem('access_token', response.access_token);
        }),
        switchMap(() => this.getMe()),
        tap((user) => this.currentUser.set(user)),
        catchError((error) => {
          this.logout();
          return throwError(() => error);
        }),
      );
  }

  getMe() {
    return this.http.get<Usuario>(`${this.base}/auth/me`);
  }

  restoreSession() {
    if (!sessionStorage.getItem('access_token')) {
      return;
    }

    this.getMe().subscribe({
      next: (user) => this.currentUser.set(user),
      error: () => this.logout(),
    });
  }

  logout() {
    sessionStorage.removeItem('access_token');
    this.currentUser.set(null);
  }

  isAuthenticated(): boolean {
    return this.currentUser() !== null;
  }

  isAdmin(): boolean {
    return this.currentUser()?.rol === 'ADMINISTRADOR';
  }
}
