
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  nombre_usuario = '';
  password = '';

  readonly cargando = signal(false);
  readonly error = signal('');

  iniciarSesion(): void {
    if (!this.nombre_usuario.trim() || !this.password) {
      this.error.set('Ingresa tu usuario y contraseña.');
      return;
    }

    this.cargando.set(true);
    this.error.set('');

    this.auth.login({
      nombre_usuario: this.nombre_usuario.trim(),
      password: this.password,
    }).subscribe({
      next: (usuario) => {
        this.cargando.set(false);

        if (usuario.rol === 'ADMINISTRADOR') {
          this.router.navigate(['/gestion/operadores']);
        } else {
          this.router.navigate(['/control-acceso']);
        }
      },
      error: (err) => {
        this.cargando.set(false);

        if (err.status === 401) {
          this.error.set('Usuario o contraseña incorrectos.');
        } else {
          this.error.set('No fue posible iniciar sesión. Intenta nuevamente.');
        }
      },
    });
  }
}
