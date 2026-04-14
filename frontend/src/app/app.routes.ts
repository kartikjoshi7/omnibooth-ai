import { Routes } from '@angular/router';
import { KioskComponent } from './kiosk/kiosk.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AnalyticsComponent } from './analytics/analytics.component';

export const routes: Routes = [
  { path: 'kiosk', component: KioskComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'analytics', component: AnalyticsComponent },
  { path: '', redirectTo: '/kiosk', pathMatch: 'full' }
];
