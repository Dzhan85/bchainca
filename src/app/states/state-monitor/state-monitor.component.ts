import { Component, OnInit, OnDestroy, Input, HostListener } from '@angular/core';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-state-monitor',
  templateUrl: './state-monitor.component.html',
  styleUrls: [
    './state-monitor.component.scss',
    '../../../styles/shared/_explorer-detail.scss'
  ]
})
export class StateMonitorComponent implements OnInit, OnDestroy {

  @Input() states: any[] = [];
  addresses: string[] = [];
  newAddress = '';
  private webSocket!: WebSocket;
  webSocketUrl = environment.apiURL.replace(/^(https?):\/\//, 'ws:') + '/subscriptions';

  ngOnInit() {
    this.states = [];
    this.addresses = [];
  }

  ngOnDestroy() {
    this.closeWebsocket();
  }

  @HostListener('window:unload')
  unloadHandler() {
    this.closeWebsocket();
  }

  addAddress(address: string) {
    if (!address) return;
    this.addresses.push(address);
    this.newAddress = '';
    this.resetWebsocket(this.addresses);
  }

  removeAddress(index: number) {
    if (!this.addresses || this.addresses.length <= index) return;
    if (index < 0 || index >= this.addresses.length) return;
    this.addresses.splice(index, 1);
    this.resetWebsocket(this.addresses);
  }

  resetWebsocket(addresses: string[]) {
    this.closeWebsocket();
    this.openWebsocket(addresses);
  }

  openWebsocket(addresses: string[]): void {
    if (!addresses || !addresses.length) return;
    this.webSocket = new WebSocket(this.webSocketUrl);
    this.webSocket.onopen = () => {
      this.webSocket.send(JSON.stringify({ action: 'subscribe', address_prefixes: addresses }));
    };
    this.webSocket.onmessage = (message) => {
      const newStates = this.parseDeltaSubscriptionMessage(message);
      if (newStates && newStates.length) {
        this.states = this.states.concat(newStates);
      }
    };
  }

  parseDeltaSubscriptionMessage(message: MessageEvent): any[] {
    const stateChanges: any[] = [];
    if (!message.data) return stateChanges;
    const messageData = JSON.parse(message.data);
    const stateChangeData = messageData['state_changes'];
    if (!stateChangeData) return stateChanges;
    stateChangeData.forEach((change: any) => {
      stateChanges.push({
        block_id: messageData['block_id'],
        block_num: messageData['block_num'],
        previous_block_id: messageData['previous_block_id'],
        payload: change
      });
    });
    return stateChanges;
  }

  closeWebsocket(): void {
    if (this.webSocket) {
      this.webSocket.send(JSON.stringify({ action: 'unsubscribe' }));
      this.webSocket.close();
    }
    this.webSocket = null!;
  }
}
