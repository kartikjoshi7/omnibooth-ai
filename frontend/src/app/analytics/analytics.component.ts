import { Component, OnInit, ChangeDetectorRef, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="analytics-container" [ngClass]="{'active-engagement': getHotLeadVolume() >= 5}">
      <header class="glass-panel text-center">
        <h1>OmniBooth Vibe Heatmap</h1>
        <p class="text-secondary">Live monitoring of floor engagement across a rolling 10-minute window.</p>
      </header>

      <div class="heatmap-grid mt-4">
        <div class="metric-block hot-block glass-panel">
          <h3>🔥 Hot Leads</h3>
          <div class="volume-display">{{ getCount('Hot') }}</div>
        </div>
        <div class="metric-block warm-block glass-panel">
          <h3>⚡ Warm Leads</h3>
          <div class="volume-display">{{ getCount('Warm') }}</div>
        </div>
        <div class="metric-block cold-block glass-panel">
          <h3>❄️ Cold Leads</h3>
          <div class="volume-display">{{ getCount('Cold') }}</div>
        </div>
      </div>
      
      <div class="glass-panel mt-4 text-center pulse-indicator" *ngIf="getHotLeadVolume() >= 5">
         🚨 HIGH ENGAGEMENT ALERT: 5+ Hot Leads actively tracking!
      </div>
    </div>
  `,
  styles: [`
    .analytics-container { 
        padding: 40px; 
        max-width: 1200px; 
        margin: 0 auto; 
        min-height: 100vh;
        transition: background 0.5s ease;
    }
    .active-engagement {
        background: radial-gradient(circle at center, rgba(0, 255, 204, 0.15) 0%, transparent 60%);
    }
    .text-center { text-align: center; }
    .text-secondary { color: var(--text-secondary); margin-top: 10px; }
    .mt-4 { margin-top: 25px; }
    
    .heatmap-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 30px;
    }
    
    .metric-block {
      padding: 40px;
      text-align: center;
      border-radius: 12px;
      transition: transform 0.3s ease;
    }
    .metric-block:hover { transform: translateY(-5px); }
    
    .hot-block { border-top: 5px solid var(--error); box-shadow: 0 10px 30px rgba(255, 77, 77, 0.1); }
    .warm-block { border-top: 5px solid var(--warning); }
    .cold-block { border-top: 5px solid #00b3ff; }
    
    .volume-display {
      font-size: 5rem;
      font-weight: 800;
      color: white;
      margin-top: 20px;
    }
    
    .pulse-indicator {
      border: 1px solid var(--accent-color);
      color: var(--accent-color);
      font-weight: bold;
      animation: pulse 2s infinite;
      font-size: 1.2rem;
    }
    
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(0, 255, 204, 0.4); }
      70% { box-shadow: 0 0 0 20px rgba(0, 255, 204, 0); }
      100% { box-shadow: 0 0 0 0 rgba(0, 255, 204, 0); }
    }
  `]
})
export class AnalyticsComponent implements OnInit, OnDestroy {
  analyticsData: any[] = [];
  intervalId: any;

  constructor(private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.fetchAnalytics();
    // Poll every 5 seconds for Real-Time UI updates
    this.intervalId = setInterval(() => {
      this.fetchAnalytics();
    }, 5000);
  }

  async fetchAnalytics() {
    try {
      const res = await fetch('http://localhost:8000/analytics');
      if (res.ok) {
        this.analyticsData = await res.json();
        this.cdr.detectChanges();
      }
    } catch (err) {
      console.error('Failed to fetch realtime analytics:', err);
    }
  }

  getCount(sentiment: string): number {
    const record = this.analyticsData.find(item => item._id === sentiment);
    return record ? record.count : 0;
  }
  
  getHotLeadVolume(): number {
    return this.getCount('Hot');
  }

  ngOnDestroy() {
    if (this.intervalId) clearInterval(this.intervalId);
  }
}
