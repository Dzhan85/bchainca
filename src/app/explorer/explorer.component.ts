import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, ActivatedRoute, Params } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Subject, Subscription } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

import { APIService } from '../services/api-service/api.service';

import { BlockListItemComponent } from '../blocks/block-list-item/block-list-item.component';
import { BatchListItemComponent } from '../batches/batch-list-item/batch-list-item.component';
import { TransactionListItemComponent } from '../transactions/transaction-list-item/transaction-list-item.component';

@Component({
  selector: 'app-explorer',
  templateUrl: './explorer.component.html',
  styleUrls: ['./explorer.component.scss']
})
export class ExplorerComponent implements OnInit, OnDestroy {

  constructor(private apiService: APIService,
              private activatedRoute: ActivatedRoute,
              private router: Router,
              private snackBar: MatSnackBar) {}

  items: any[] = [];
  viewType!: string;
  currentHead!: string;
  nextPosition!: string;
  views = ['transactions', 'batches', 'blocks'];
  listViewComponent: any;
  selectedItem: any;
  private apiItemsSubscription!: Subscription;

  navPageSize = 10;
  navPageIndex = 0;
  navTotalItems = 0;
  navPageSizeOptions = [5, 10, 20, 50];
  loading = true;
  error!: string;

  private apiErrorMessage = 'Error fetching items from API';
  private ngUnsubscribe = new Subject<void>();

  listViewComponents: { [key: string]: any } = {
    'blocks': BlockListItemComponent,
    'batches': BatchListItemComponent,
    'transactions': TransactionListItemComponent
  };

  ngOnInit() {
    this.activatedRoute.queryParams.subscribe((queryParams: Params) => {
      const viewType = queryParams['view'];
      if (this.viewType && viewType === this.viewType) return;
      this.viewType = this.views.indexOf(viewType) !== -1 ? viewType : 'transactions';
      this.subscribeToItems(this.viewType, {
        pageSize: this.navPageSize, pageIndex: this.navPageIndex
      });
    });
  }

  updateView(data: any) {
    if (!data) return;
    if (this.navPageIndex === 0) this.items = [];
    this.items = data.data;
    this.navTotalItems = data.data.length;
    this.currentHead = data.head;
    this.nextPosition = data.paging?.next_position;
    this.selectedItem = this.items[0];
    this.listViewComponent = this.listViewComponents[this.viewType];
    this.updateParams(this.viewType, this.currentHead);
    this.loading = false;
  }

  updateNavPaging(event: any) {
    this.navPageSize = event['pageSize'];
    this.navPageIndex = event['pageIndex'];
    this.subscribeToItems(this.viewType, event);
  }

  onChangeViewType(viewType: string): void {
    this.viewType = viewType;
    this.currentHead = null!;
    this.nextPosition = null!;
    this.navPageIndex = 0;
    this.subscribeToItems(this.viewType, {
      pageSize: this.navPageSize, pageIndex: this.navPageIndex
    });
  }

  subscribeToItems(viewType: string, pagingSettings: any) {
    this.loading = true;
    if (this.apiItemsSubscription) this.apiItemsSubscription.unsubscribe();
    pagingSettings['head'] = this.currentHead;
    pagingSettings['start'] = this.nextPosition;
    this.apiItemsSubscription = this.apiService
      .getItems(viewType, pagingSettings)
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe({
        next: data => {
          this.updateView(data);
          this.error = undefined!;
        },
        error: error => {
          this.loading = false;
          this.error = error.message ? error.message : this.apiErrorMessage + '.';
          this.snackBar.open(this.apiErrorMessage + '(' + this.viewType + ').', undefined, { duration: 3000 });
        }
      });
  }

  showItemDetails(item: any): void {
    this.selectedItem = item;
    this.updateParams(this.viewType, this.currentHead);
  }

  updateParams(viewType: string, currentHead: string): void {
    const queryParams: Params = Object.assign({}, this.activatedRoute.snapshot.queryParams);
    queryParams['view'] = viewType;
    queryParams['head'] = currentHead;
    this.router.navigate(['.'], {
      queryParams,
      replaceUrl: true,
      relativeTo: this.activatedRoute
    });
  }

  nextPage() {
    this.updateNavPaging({ pageSize: this.navPageSize, pageIndex: this.navPageIndex + 1 });
  }

  ngOnDestroy() {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }
}
