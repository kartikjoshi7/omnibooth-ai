import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, Lead } from '../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="dashboard-container" role="main" aria-label="Dashboard Pipeline">
      <header class="glass-panel header-bar" role="banner">
        <h1>OmniBooth CRM Dashboard</h1>
        <button class="btn-primary" aria-label="Refresh Lead Data" (click)="loadLeads()">Refresh Leads</button>
      </header>
      
      <section class="capture-section glass-panel mt-4" aria-label="Knowledge Vault Engine">
        <h2 style="color: var(--accent-color)">Ingest Knowledge Vault (RAG)</h2>
        <textarea class="input-primary mt-3" aria-label="Document Input Textarea" [(ngModel)]="vaultDoc" rows="3" placeholder="Paste technical manuals, product specs, or documentation to align the AI Critic Loop..."></textarea>
        <button class="btn-primary mt-3" aria-label="Initiate Vault Ingestion" (click)="uploadDocs()">Ingest Reference Data</button>
      </section>

      <section class="capture-section glass-panel mt-4" aria-label="Lead Extraction Engine">
        <h2>Enter Exhibitor Notes</h2>
        <div class="form-grid">
          <input class="input-primary" aria-label="Attendee Name TextField" [(ngModel)]="newLeadName" placeholder="Attendee Name (Optional)" />
          <input class="input-primary" aria-label="Attendee Email TextField" [(ngModel)]="newLeadEmail" placeholder="Attendee Email (Optional)" />
        </div>
        <textarea class="input-primary mt-3" aria-label="Attendee Raw Notes" [(ngModel)]="newLeadNotes" rows="3" placeholder="Notes/Voice transcript regarding the technical interaction..."></textarea>
        <button class="btn-primary mt-3" aria-label="Execute AI Extraction" (click)="captureLead()" [disabled]="isParsing || !newLeadNotes.trim()">
          {{ isParsing ? 'Parsing Context via Gemini...' : 'Analyze & Capture Lead' }}
        </button>
      </section>

      <section class="kanban-board mt-4" aria-label="Pipeline Kanban Columns">
        <div class="kanban-column glass-panel hot" role="list" aria-label="Hot Leads Column">
          <h3 aria-hidden="true">🔥 Hot Leads</h3>
          <div class="lead-card" *ngFor="let m of getLeadsBySentiment('Hot')" (click)="expandLead(m)">
            <h4>{{ m.attendee_name || 'Unknown User' }}</h4>
            <p class="summary">{{ m.notes }}</p>
          </div>
        </div>
        
        <div class="kanban-column glass-panel warm" role="list" aria-label="Warm Leads Column">
          <h3 aria-hidden="true">⚡ Warm Leads</h3>
          <div class="lead-card" *ngFor="let m of getLeadsBySentiment('Warm')" (click)="expandLead(m)">
            <h4>{{ m.attendee_name || 'Unknown User' }}</h4>
            <p class="summary">{{ m.notes }}</p>
          </div>
        </div>

        <div class="kanban-column glass-panel cold" role="list" aria-label="Cold Leads Column">
          <h3 aria-hidden="true">❄️ Cold Leads</h3>
          <div class="lead-card" *ngFor="let m of getLeadsBySentiment('Cold')" (click)="expandLead(m)">
            <h4>{{ m.attendee_name || 'Unknown User' }}</h4>
            <p class="summary">{{ m.notes }}</p>
          </div>
        </div>
      </div>

      <div class="modal-overlay" aria-modal="true" role="dialog" aria-label="Exhibitor Card Modal" *ngIf="expandedLead" (click)="expandedLead = null">
        <div class="modal glass-panel" (click)="$event.stopPropagation()">
          <button class="close-btn" aria-label="Close Pipeline Detail Modal" (click)="expandedLead = null">×</button>
          <h2>Lead Details: {{ expandedLead.attendee_name || 'Unknown' }}</h2>
          <div class="modal-content mt-3">
             <h3>Raw Notes</h3>
             <p>{{ expandedLead.notes }}</p>

             <h3 class="mt-3">Action Items</h3>
             <ul>
               <li *ngFor="let action of expandedLead.action_items">{{ action }}</li>
             </ul>
             
             <h3 class="mt-3" style="color: var(--warning)">OmniEngine Verification Status</h3>
             <p>{{ expandedLead.verification_status }}</p>

             <h3 class="mt-3">Auto-Generated Follow-up</h3>
             <textarea class="input-primary" aria-label="Drafted Sales Follow-up Envelope" rows="6" readonly [value]="expandedLead.drafted_email"></textarea>
             
             <button class="btn-primary mt-3" aria-label="Finalize Transmission of Proposal" (click)="sendEmail()">Send Proposal</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container { padding: 40px; max-width: 1400px; margin: 0 auto; min-height: 100vh;}
    .header-bar { display: flex; justify-content: space-between; align-items: center; }
    .mt-3 { margin-top: 15px; }
    .mt-4 { margin-top: 25px; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
    
    .kanban-board {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 25px;
      align-items: start;
    }
    .kanban-column {
      min-width: 0;
    }
    .kanban-column.hot { border-top: 3px solid var(--error); }
    .kanban-column.warm { border-top: 3px solid var(--warning); }
    .kanban-column.cold { border-top: 3px solid #00b3ff; }
    .kanban-column h3 { border-bottom: 1px solid var(--glass-border); padding-bottom: 10px; margin-bottom: 15px;}
    
    .lead-card {
      background: rgba(255,255,255,0.03);
      border: 1px solid var(--glass-border);
      border-radius: 8px;
      padding: 15px;
      margin-bottom: 15px;
      cursor: pointer;
      transition: background 0.2s, border-color 0.2s, transform 0.2s;
    }
    .lead-card:hover {
      background: rgba(255,255,255,0.1);
      border-color: var(--accent-color);
      transform: translateY(-3px);
    }
    .summary {
      color: var(--text-secondary);
      font-size: 0.9em;
      margin-top: 8px;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
      white-space: normal;
    }

    /* Modal */
    .modal-overlay {
      position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.8);
      backdrop-filter: blur(5px);
      display: flex; align-items: center; justify-content: center;
      z-index: 1000;
    }
    .modal { width: 600px; max-width: 90%; max-height: 90vh; overflow-y: auto; position: relative;}
    .close-btn { position: absolute; top: 15px; right: 15px; background: transparent; border: none; font-size: 24px; color: var(--text-primary); cursor: pointer;}
    .modal-content h3 { color: var(--accent-color); font-size: 1.1em; margin-bottom: 5px; }
    .modal-content p { color: #f0f0f0; line-height: 1.5; }
    .modal-content ul { margin-left: 20px; color: var(--text-secondary); list-style-type: square; line-height:1.5; }
  `]
})
export class DashboardComponent implements OnInit {
  leads: Lead[] = [];
  newLeadName = '';
  newLeadEmail = '';
  newLeadNotes = '';
  vaultDoc = '';
  isParsing = false;
  expandedLead: Lead | null = null;

  constructor(private apiService: ApiService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.loadLeads();
  }

  async loadLeads() {
    try {
      this.leads = await this.apiService.getLeads();
      this.cdr.detectChanges();
    } catch (err) {
      console.error(err);
    }
  }

  async uploadDocs() {
     try {
       await fetch('/upload-docs', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ text: this.vaultDoc })
       });
       alert('Knowledge Vault Synced successfully!');
       this.vaultDoc = '';
       this.cdr.detectChanges();
     } catch (err) {
       console.error("Failed to upload RAG docs", err);
     }
  }

  getLeadsBySentiment(sentiment: string) {
    return this.leads.filter(l => l.sentiment === sentiment);
  }

  async captureLead() {
    this.isParsing = true;
    this.cdr.detectChanges();
    try {
      await this.apiService.captureLead(this.newLeadNotes, this.newLeadName, this.newLeadEmail);
      this.newLeadNotes = '';
      this.newLeadName = '';
      this.newLeadEmail = '';
      await this.loadLeads();
    } catch (err) {
      console.error(err);
      alert('Error extracting lead context.');
    } finally {
      this.isParsing = false;
      this.cdr.detectChanges();
    }
  }

  expandLead(lead: Lead) {
    this.expandedLead = lead;
  }
  
  sendEmail() {
    alert("Draft proposal loaded into mail client.");
  }
}
