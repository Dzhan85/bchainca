import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService, User } from '../services/auth.service';
import { APIService } from '../services/api-service/api.service';

interface DashboardStats {
  totalBlocks: number;
  totalBatches: number;
  totalTransactions: number;
  networkStatus: string;
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  currentUser: User | null = null;
  stats: DashboardStats = {
    totalBlocks: 0,
    totalBatches: 0,
    totalTransactions: 0,
    networkStatus: 'Checking...'
  };
  loading = true;
  recentBlocks: any[] = [];

  quickActions = [
    {
      title: 'API Explorer',
      description: 'Access REST API at localhost:8008',
      icon: 'api',
      route: 'http://localhost:8008/blocks',
      color: '#667eea',
      external: true
    },
    {
      title: 'Blockchain Data',
      description: 'View live blockchain information',
      icon: 'storage',
      route: '/dashboard',
      color: '#764ba2'
    },
    {
      title: 'Network Status',
      description: 'Monitor network health',
      icon: 'network_check',
      route: '/dashboard',
      color: '#f093fb'
    },
    {
      title: 'Documentation',
      description: 'View project documentation',
      icon: 'description',
      route: '/dashboard',
      color: '#4facfe'
    }
  ];

  constructor(
    private authService: AuthService,
    private apiService: APIService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.currentUserValue;
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.loading = true;

    this.apiService.get('blocks?limit=5').subscribe({
      next: (response) => {
        const blocks = response.data || [];
        this.recentBlocks = blocks;
        this.stats.totalBlocks = blocks.length > 0 ? parseInt(blocks[0].header.block_num, 10) + 1 : 0;
        this.stats.networkStatus = 'Online';
        this.loading = false;
      },
      error: () => {
        this.stats.networkStatus = 'Offline';
        this.loading = false;
      }
    });

    // Load batches count
    this.apiService.get('batches?limit=1').subscribe({
      next: (response) => {
        this.stats.totalBatches = response.data?.length || 0;
      }
    });

    // Load transactions count
    this.apiService.get('transactions?limit=1').subscribe({
      next: (response) => {
        this.stats.totalTransactions = response.data?.length || 0;
      }
    });
  }

  navigateTo(route: string): void {
    if (route.startsWith('http')) {
      window.open(route, '_blank');
    } else {
      this.router.navigate([route]);
    }
  }

  getGreeting(): string {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }

  getNetworkStatusColor(): string {
    return this.stats.networkStatus === 'Online' ? '#4caf50' : '#f44336';
  }
}
