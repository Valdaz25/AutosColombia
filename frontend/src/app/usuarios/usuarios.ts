
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { API_BASE_URL } from '../services/api.service';
import { Operador, OperadoresPagina } from '../models/operador';

interface Usuario {
  id: number;
  nombre_usuario: string;
  rol: 'ADMINISTRADOR' | 'OPERADOR';
  operador_id: number | null;
  activo: boolean;
  creado_en: string;
}

interface UsuariosPagina {
  items: Usuario[];
  total: number;
  offset: number;
  limit: number;
}

@Component({
  selector: 'app-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="usuarios-container">
      <h2>Gestión de usuarios</h2>
      <p>Administra las cuentas de acceso al sistema Autos Colombia.</p>

      <div class="formulario">
        <h3>Crear usuario</h3>

        <form #formUsuario="ngForm" (ngSubmit)="crearUsuario()">
          <label for="nombre_usuario">Nombre de usuario</label>
          <input
            id="nombre_usuario"
            type="text"
            name="nombre_usuario"
            [(ngModel)]="nuevoUsuario.nombre_usuario"
            required
            minlength="3"
          />

          <label for="password">Contraseña</label>
          <input
            id="password"
            type="password"
            name="password"
            [(ngModel)]="nuevoUsuario.password"
            required
            minlength="12"
          />

          <label for="rol">Rol</label>
          <select
            id="rol"
            name="rol"
            [(ngModel)]="nuevoUsuario.rol"
            (ngModelChange)="cambioRol()"
            required
          >
            <option value="ADMINISTRADOR">Administrador</option>
            <option value="OPERADOR">Operador</option>
          </select>

          <div *ngIf="nuevoUsuario.rol === 'OPERADOR'">
            <label for="operador_id">Seleccionar operador</label>

            <select
              id="operador_id"
              name="operador_id"
              [(ngModel)]="nuevoUsuario.operador_id"
              required
            >
              <option [ngValue]="null">Seleccione un operador</option>

              <option
                *ngFor="let operador of operadoresDisponibles"
                [ngValue]="operador.id"
              >
                {{ operador.nombre }} - {{ operador.documento }}
              </option>
            </select>

            <p *ngIf="!cargandoOperadores && operadoresDisponibles.length === 0">
              No hay operadores disponibles para vincular.
            </p>
          </div>

          <button
            type="submit"
            [disabled]="formUsuario.invalid || guardando || cargandoOperadores"
          >
            {{ guardando ? 'Creando...' : 'Crear usuario' }}
          </button>
        </form>
      </div>

      <div class="formulario" *ngIf="usuarioEditando">
        <h3>Editar usuario</h3>

        <form #formEditar="ngForm" (ngSubmit)="guardarEdicion()">
          <label for="editar_nombre">Nombre de usuario</label>
          <input
            id="editar_nombre"
            type="text"
            name="editar_nombre"
            [(ngModel)]="edicion.nombre_usuario"
            required
            minlength="3"
          />

          <label for="editar_password">Nueva contraseña</label>
          <input
            id="editar_password"
            type="password"
            name="editar_password"
            [(ngModel)]="edicion.password"
            minlength="12"
            placeholder="Dejar vacío para conservar la actual"
          />

          <label for="editar_rol">Rol</label>
          <select
            id="editar_rol"
            name="editar_rol"
            [(ngModel)]="edicion.rol"
            (ngModelChange)="cambioRolEdicion()"
            required
          >
            <option value="ADMINISTRADOR">Administrador</option>
            <option value="OPERADOR">Operador</option>
          </select>

          <div *ngIf="edicion.rol === 'OPERADOR'">
            <label for="editar_operador">Seleccionar operador</label>

            <select
              id="editar_operador"
              name="editar_operador"
              [(ngModel)]="edicion.operador_id"
              required
            >
              <option [ngValue]="null">Seleccione un operador</option>

              <option
                *ngFor="let operador of operadoresParaEdicion"
                [ngValue]="operador.id"
              >
                {{ operador.nombre }} - {{ operador.documento }}
              </option>
            </select>
          </div>

          <button
            type="submit"
            [disabled]="formEditar.invalid || guardando"
          >
            {{ guardando ? 'Guardando...' : 'Guardar cambios' }}
          </button>

          <button
            type="button"
            (click)="cancelarEdicion()"
            [disabled]="guardando"
          >
            Cancelar
          </button>
        </form>
      </div>

      <p *ngIf="mensaje" class="mensaje">{{ mensaje }}</p>
      <p *ngIf="error" class="error">{{ error }}</p>

      <div class="tabla-container">
        <h3>Usuarios registrados</h3>

        <button
          type="button"
          (click)="cargarDatos()"
          [disabled]="cargandoLista || cargandoOperadores"
        >
          {{ cargandoLista ? 'Actualizando...' : 'Actualizar lista' }}
        </button>

        <p *ngIf="cargandoLista">Cargando usuarios...</p>

        <table *ngIf="usuarios.length > 0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario</th>
              <th>Rol</th>
              <th>Operador</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr *ngFor="let usuario of usuarios">
              <td>{{ usuario.id }}</td>
              <td>{{ usuario.nombre_usuario }}</td>
              <td>{{ usuario.rol }}</td>
              <td>{{ nombreOperador(usuario.operador_id) }}</td>
              <td>{{ usuario.activo ? 'Activo' : 'Inactivo' }}</td>
              <td>
                <button
                  type="button"
                  (click)="iniciarEdicion(usuario)"
                  [disabled]="guardando"
                >
                  Editar
                </button>

                <button
                  type="button"
                  (click)="cambiarEstado(usuario)"
                  [disabled]="guardando"
                >
                  {{ usuario.activo ? 'Desactivar' : 'Activar' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <p *ngIf="!cargandoLista && usuarios.length === 0">
          No hay usuarios registrados.
        </p>
      </div>
    </section>
  `
})
export class UsuariosComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly base = inject(API_BASE_URL);
  private readonly cdr = inject(ChangeDetectorRef);

  usuarios: Usuario[] = [];
  operadores: Operador[] = [];

  usuarioEditando: Usuario | null = null;

  cargandoLista = false;
  cargandoOperadores = false;
  guardando = false;

  mensaje = '';
  error = '';

  nuevoUsuario = {
    nombre_usuario: '',
    password: '',
    rol: 'OPERADOR' as 'ADMINISTRADOR' | 'OPERADOR',
    operador_id: null as number | null
  };

  edicion = {
    nombre_usuario: '',
    password: '',
    rol: 'OPERADOR' as 'ADMINISTRADOR' | 'OPERADOR',
    operador_id: null as number | null
  };

  get operadoresDisponibles(): Operador[] {
    const vinculados = new Set(
      this.usuarios
        .filter(usuario => usuario.operador_id !== null)
        .map(usuario => usuario.operador_id)
    );

    return this.operadores.filter(
      operador => !vinculados.has(operador.id)
    );
  }

  get operadoresParaEdicion(): Operador[] {
    const usuarioActual = this.usuarioEditando;

    const vinculadosPorOtros = new Set(
      this.usuarios
        .filter(usuario =>
          usuario.operador_id !== null &&
          usuario.id !== usuarioActual?.id
        )
        .map(usuario => usuario.operador_id)
    );

    return this.operadores.filter(
      operador => !vinculadosPorOtros.has(operador.id)
    );
  }

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.cargarUsuarios();
    this.cargarOperadores();
  }

  cargarUsuarios(): void {
    if (this.cargandoLista) return;

    this.cargandoLista = true;
    this.error = '';
    this.cdr.detectChanges();

    this.http.get<UsuariosPagina>(
      `${this.base}/usuarios`
    ).pipe(
      finalize(() => {
        this.cargandoLista = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: respuesta => {
        this.usuarios = respuesta.items ?? [];
        this.cdr.detectChanges();
      },
      error: respuesta => {
        this.error =
          respuesta.error?.detail ||
          'No fue posible cargar los usuarios.';
        this.cdr.detectChanges();
      }
    });
  }

  cargarOperadores(): void {
    if (this.cargandoOperadores) return;

    this.cargandoOperadores = true;
    this.cdr.detectChanges();

    this.http.get<OperadoresPagina>(
      `${this.base}/operadores`
    ).pipe(
      finalize(() => {
        this.cargandoOperadores = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: respuesta => {
        this.operadores = respuesta.items ?? [];
        this.cdr.detectChanges();
      },
      error: respuesta => {
        this.error =
          respuesta.error?.detail ||
          'No fue posible cargar los operadores.';
        this.cdr.detectChanges();
      }
    });
  }

  nombreOperador(operadorId: number | null): string {
    if (operadorId === null) return 'No aplica';

    const operador = this.operadores.find(
      item => item.id === operadorId
    );

    return operador
      ? operador.nombre
      : `Operador ${operadorId}`;
  }

  cambioRol(): void {
    if (this.nuevoUsuario.rol === 'ADMINISTRADOR') {
      this.nuevoUsuario.operador_id = null;
    }
  }

  cambioRolEdicion(): void {
    if (this.edicion.rol === 'ADMINISTRADOR') {
      this.edicion.operador_id = null;
    }
  }

  crearUsuario(): void {
    if (this.guardando) return;

    this.mensaje = '';
    this.error = '';

    const datos: Record<string, unknown> = {
      nombre_usuario: this.nuevoUsuario.nombre_usuario.trim(),
      password: this.nuevoUsuario.password,
      rol: this.nuevoUsuario.rol
    };

    if (this.nuevoUsuario.rol === 'OPERADOR') {
      if (this.nuevoUsuario.operador_id === null) {
        this.error = 'Debes seleccionar un operador.';
        return;
      }

      datos['operador_id'] = this.nuevoUsuario.operador_id;
    }

    this.guardando = true;
    this.cdr.detectChanges();

    this.http.post(`${this.base}/usuarios`, datos).pipe(
      finalize(() => {
        this.guardando = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
        this.mensaje = 'Usuario creado correctamente.';

        this.nuevoUsuario = {
          nombre_usuario: '',
          password: '',
          rol: 'OPERADOR',
          operador_id: null
        };

        this.cargarDatos();
        this.cdr.detectChanges();
      },
      error: respuesta => {
        this.error =
          respuesta.error?.detail ||
          'No fue posible crear el usuario.';
        this.cdr.detectChanges();
      }
    });
  }

  iniciarEdicion(usuario: Usuario): void {
    this.mensaje = '';
    this.error = '';

    this.usuarioEditando = usuario;

    this.edicion = {
      nombre_usuario: usuario.nombre_usuario,
      password: '',
      rol: usuario.rol,
      operador_id: usuario.operador_id
    };

    this.cdr.detectChanges();
  }

  cancelarEdicion(): void {
    this.usuarioEditando = null;

    this.edicion = {
      nombre_usuario: '',
      password: '',
      rol: 'OPERADOR',
      operador_id: null
    };

    this.cdr.detectChanges();
  }

  guardarEdicion(): void {
    if (this.guardando || !this.usuarioEditando) return;

    this.mensaje = '';
    this.error = '';

    const datos: Record<string, unknown> = {
      nombre_usuario: this.edicion.nombre_usuario.trim(),
      rol: this.edicion.rol,
      operador_id: this.edicion.rol === 'OPERADOR'
        ? this.edicion.operador_id
        : null
    };

    if (this.edicion.password.trim()) {
      datos['password'] = this.edicion.password;
    }

    if (
      this.edicion.rol === 'OPERADOR' &&
      this.edicion.operador_id === null
    ) {
      this.error = 'Debes seleccionar un operador.';
      return;
    }

    const userId = this.usuarioEditando.id;

    this.guardando = true;
    this.cdr.detectChanges();

    this.http.put(
      `${this.base}/usuarios/${userId}`,
      datos
    ).pipe(
      finalize(() => {
        this.guardando = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
        this.mensaje = 'Usuario actualizado correctamente.';
        this.cancelarEdicion();
        this.cargarDatos();
      },
      error: respuesta => {
        this.error =
          respuesta.error?.detail ||
          'No fue posible actualizar el usuario.';
        this.cdr.detectChanges();
      }
    });
  }

  cambiarEstado(usuario: Usuario): void {
    if (this.guardando) return;

    const nuevoEstado = !usuario.activo;
    const accion = nuevoEstado ? 'activar' : 'desactivar';

    if (!confirm(`¿Estás seguro de que deseas ${accion} esta cuenta?`)) {
      return;
    }

    this.mensaje = '';
    this.error = '';
    this.guardando = true;
    this.cdr.detectChanges();

    this.http.patch(
      `${this.base}/usuarios/${usuario.id}/estado`,
      { activo: nuevoEstado }
    ).pipe(
      finalize(() => {
        this.guardando = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
        this.mensaje = nuevoEstado
          ? 'Usuario activado correctamente.'
          : 'Usuario desactivado correctamente.';

        this.cargarDatos();
        this.cdr.detectChanges();
      },
      error: respuesta => {
        this.error =
          respuesta.error?.detail ||
          'No fue posible cambiar el estado del usuario.';
        this.cdr.detectChanges();
      }
    });
  }
}
