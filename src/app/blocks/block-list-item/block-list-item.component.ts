import { Component, Input } from '@angular/core';

@Component({
  selector: 'block-list-item',
  templateUrl: './block-list-item.component.html',
  styleUrls: [
    './block-list-item.component.scss',
    '../../../styles/shared/_explorer-list-item.scss'
  ]
})
export class BlockListItemComponent {
  @Input() data: any = {};
  @Input() active = false;
}
