import { BrowserModule } from '@angular/platform-browser';
import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatMenuModule } from '@angular/material/menu';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';

import { ExplorerComponent } from './explorer/explorer.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';

import { EntityDetailComponent } from './entities/entity-detail/entity-detail.component';

import { BlockListItemComponent } from './blocks/block-list-item/block-list-item.component';
import { BlockDetailComponent } from './blocks/block-detail/block-detail.component';
import { BlockComponent } from './blocks/block/block.component';

import { BatchListItemComponent } from './batches/batch-list-item/batch-list-item.component';
import { BatchDetailComponent } from './batches/batch-detail/batch-detail.component';
import { BatchComponent } from './batches/batch/batch.component';

import { TransactionListItemComponent } from './transactions/transaction-list-item/transaction-list-item.component';
import { TransactionDetailComponent } from './transactions/transaction-detail/transaction-detail.component';
import { TransactionComponent } from './transactions/transaction/transaction.component';

import { StateMonitorComponent } from './states/state-monitor/state-monitor.component';
import { StateComponent } from './states/state/state.component';

import { DataTableComponent } from './data-table/data-table.component';

import { APIService } from './services/api-service/api.service';
import { AuthService } from './services/auth.service';

import { AuthGuard } from './guards/auth.guard';

import { DynamicViewDirective } from './dynamic-views/dynamic-view-directive/dynamic-view.directive';
import { DynamicViewLoaderComponent } from './dynamic-views/dynamic-view-loader/dynamic-view-loader.component';
import { Base64DecodePipe } from './pipes/base64-decode/base64-decode.pipe';
import { UIAceDataTransformPipe } from './pipes/ui-ace-data-transform/ui-ace-data-transform.pipe';

@NgModule({
  declarations: [
    AppComponent,
    ExplorerComponent,
    LoginComponent,
    DashboardComponent,
    EntityDetailComponent,
    BlockListItemComponent,
    BlockDetailComponent,
    BlockComponent,
    BatchListItemComponent,
    BatchDetailComponent,
    BatchComponent,
    TransactionListItemComponent,
    TransactionDetailComponent,
    TransactionComponent,
    StateMonitorComponent,
    StateComponent,
    DataTableComponent,
    DynamicViewDirective,
    DynamicViewLoaderComponent,
    Base64DecodePipe,
    UIAceDataTransformPipe
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    BrowserAnimationsModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatPaginatorModule,
    MatTabsModule,
    MatTableModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    MatSnackBarModule,
    MatCardModule,
    MatMenuModule,
    MatProgressSpinnerModule,
    MatDividerModule
  ],
  providers: [
    APIService,
    AuthService,
    AuthGuard
  ],
  bootstrap: [AppComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class AppModule {}
