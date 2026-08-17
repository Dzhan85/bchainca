import { Component, AfterViewInit, Input, ViewChild, Type, ViewContainerRef } from '@angular/core';
import { DynamicViewDirective } from '../dynamic-view-directive/dynamic-view.directive';

@Component({
  selector: 'dynamic-view-loader',
  templateUrl: './dynamic-view-loader.component.html',
  styleUrls: ['./dynamic-view-loader.component.scss']
})
export class DynamicViewLoaderComponent implements AfterViewInit {

  @Input() component!: Type<any>;
  @Input() data: any = {};
  @Input() params: any = {};

  @ViewChild(DynamicViewDirective) dynamicView!: DynamicViewDirective;

  ngAfterViewInit() {
    setTimeout(() => this.loadComponent(this.data, this.component, this.params));
  }

  loadComponent(itemData: any, itemComponent: Type<any>, params?: any) {
    const viewContainerRef: ViewContainerRef = this.dynamicView.viewContainerRef;
    viewContainerRef.clear();

    // Angular 18: createComponent directly (no factory resolver needed)
    const componentRef = viewContainerRef.createComponent(itemComponent);
    componentRef.instance['data'] = itemData;

    if (params) {
      for (const param in params) {
        componentRef.instance[param] = params[param];
      }
    }
  }
}
