/**
 * Copyright 2017 PokitDok, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ------------------------------------------------------------------------------
 */

import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
// Old components temporarily disabled
// import { TransactionDetailComponent } from './transactions/transaction-detail/transaction-detail.component';
// import { BatchDetailComponent } from './batches/batch-detail/batch-detail.component';
// import { BlockDetailComponent } from './blocks/block-detail/block-detail.component';
// import { ExplorerComponent } from './explorer/explorer.component';
// import { StateMonitorComponent } from './states/state-monitor/state-monitor.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },
  // Old routes temporarily disabled for Angular 18 compatibility
  // {
  //   path: 'explorer',
  //   component: ExplorerComponent,
  //   canActivate: [AuthGuard]
  // },
  // {
  //   path: 'transactions/:id',
  //   component: TransactionDetailComponent,
  //   canActivate: [AuthGuard]
  // },
  // {
  //   path: 'batches/:id',
  //   component: BatchDetailComponent,
  //   canActivate: [AuthGuard]
  // },
  // {
  //   path: 'blocks/:id',
  //   component: BlockDetailComponent,
  //   canActivate: [AuthGuard]
  // },
  // {
  //   path: 'state-monitor',
  //   component: StateMonitorComponent,
  //   canActivate: [AuthGuard]
  // },
  {
    path: '**',
    redirectTo: '/dashboard'
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
