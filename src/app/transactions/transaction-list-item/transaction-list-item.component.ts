import { Component, Input } from '@angular/core';

@Component({
  selector: 'transaction-list-item',
  templateUrl: './transaction-list-item.component.html',
  styleUrls: [
    './transaction-list-item.component.scss',
    '../../../styles/shared/_explorer-list-item.scss'
  ]
})
export class TransactionListItemComponent {
  @Input() data: any = {};
}
