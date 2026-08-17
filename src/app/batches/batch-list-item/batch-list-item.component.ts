import { Component, Input } from '@angular/core';

@Component({
  selector: 'batch-list-item',
  templateUrl: './batch-list-item.component.html',
  styleUrls: [
    './batch-list-item.component.scss',
    '../../../styles/shared/_explorer-list-item.scss'
  ]
})
export class BatchListItemComponent {
  @Input() data: any = {};
  @Input() active = false;
}
