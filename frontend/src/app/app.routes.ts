
import { Routes } from '@angular/router';

import { authGuard } from './services/auth.guard';
import { adminGuard } from './services/admin.guard';

export const routes: Routes = [
  {
    path: 'login',
    title: 'Iniciar sesión | Autos Colombia',
    loadComponent: () =>
      import('./login/login').then((m) => m.Login),
  },
  {
    path: 'control-acceso',
    title: 'Control de acceso | Autos Colombia',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./control-acceso/control-acceso').then((m) => m.ControlAcceso),
  },
  {
    path: 'gestion/usuarios',
    title: 'Usuarios | Autos Colombia',
    canActivate: [authGuard, adminGuard],
    loadComponent: () =>
      import('./usuarios/usuarios').then((m) => m.UsuariosComponent),
  },
  {
    path: 'gestion/operadores',
    title: 'Operadores | Autos Colombia',
    canActivate: [authGuard, adminGuard],
    loadComponent: () =>
      import('./operadores/operadores').then((m) => m.Operadores),
  },
  {
    path: 'gestion/celdas',
    title: 'Celdas | Autos Colombia',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./celdas/celdas').then((m) => m.Celdas),
  },
  {
    path: 'gestion/vehiculos',
    title: 'Vehículos | Autos Colombia',
    canActivate: [authGuard, adminGuard],
    loadComponent: () =>
      import('./vehiculos/vehiculos').then((m) => m.Vehiculos),
  },
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'login',
  },
  {
    path: '**',
    redirectTo: 'login',
  },
];
