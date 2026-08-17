import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Observable, Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

import { APIService } from '../../services/api-service/api.service';

@Component({
  selector: 'entity-detail',
  templateUrl: './entity-detail.component.html',
  styleUrls: ['./entity-detail.component.scss']
})
export class EntityDetailComponent implements OnInit, OnDestroy {

  constructor(private activatedRoute: ActivatedRoute,
              private apiService: APIService,
              private snackBar: MatSnackBar) {}

  @Input() collection!: string;
  @Input() displayName = 'Item';
  @Input() component: any;

  id!: string;
  data: any = {};
  loading = true;
  error: any;

  private dataObservable!: Observable<any>;
  private apiErrorMessage = 'Error fetching item from API';
  private ngUnsubscribe = new Subject<void>();

  ngOnInit() {
    this.activatedRoute.params.subscribe((params: Params) => {
      this.id = params['id'];
      this.dataObservable = this.apiService.getItemByID(this.collection, this.id);
      this.dataObservable
        .pipe(takeUntil(this.ngUnsubscribe))
        .subscribe({
          next: data => {
            this.data = data;
            this.error = undefined;
            this.loading = false;
          },
          error: error => {
            this.loading = false;
            this.error = error.message ? error.message : this.apiErrorMessage + '.';
            this.snackBar.open(this.error, undefined, { duration: 3000 });
          }
        });
    });
  }

  ngOnDestroy() {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }
}
