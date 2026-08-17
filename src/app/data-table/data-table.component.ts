import { Component, Input, OnChanges, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';

import { BlockComponent } from '../blocks/block/block.component';
import { BatchComponent } from '../batches/batch/batch.component';
import { TransactionComponent } from '../transactions/transaction/transaction.component';
import { StateComponent } from '../states/state/state.component';

@Component({
  selector: 'data-table',
  templateUrl: './data-table.component.html',
  styleUrls: ['./data-table.component.scss']
})
export class DataTableComponent implements OnChanges {
  @Input() data: any[] = [];
  @Input() type = '';

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  component: any;
  items: any[] = [];
  activeIdx = -1;
  itemCount = 0;

  pageSizeOptions = [10, 20, 50, 100];
  pageSize = 50;
  pageIndex = 0;

  components: { [key: string]: any } = {
    'blocks': BlockComponent,
    'batches': BatchComponent,
    'transactions': TransactionComponent,
    'states': StateComponent
  };

  ngOnChanges(): void {
    if (!this.data) this.data = [];
    this.component = this.components[this.type.toLowerCase()];
    this.itemCount = this.data.length;
    this.updateTableDisplay(this.pageSize, this.pageIndex);
  }

  updatePaging(event: any): void {
    this.pageSize = event.pageSize;
    this.pageIndex = event.pageIndex;
    this.updateTableDisplay(this.pageSize, this.pageIndex);
    this.activeIdx = -1;
  }

  updateTableDisplay(pageSize: number, pageIndex: number): void {
    this.items = this.data.slice(pageSize * pageIndex, pageSize * pageIndex + pageSize);
    this.activeIdx = -1;
  }

  setItemActive(itemIdx: number) { this.activeIdx = itemIdx; }
  clearActiveItem() { this.setItemActive(-1); }
}
