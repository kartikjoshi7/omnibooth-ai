import { Injectable } from '@angular/core';

export interface KioskResponse {
  media_url: string;
  message: string;
}

export interface LeadResponse {
  sentiment: string;
  drafted_email: string;
  action_items: string[];
  verification_status?: string;
}

export interface Lead {
  _id?: string;
  attendee_name?: string;
  attendee_email?: string;
  notes: string;
  sentiment: string;
  drafted_email: string;
  action_items: string[];
  verification_status?: string;
  timestamp?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = '';

  async generateVisual(prompt: string, image_data?: string): Promise<KioskResponse> {
    const payload: any = { prompt };
    if (image_data) payload.image_data = image_data;

    const res = await fetch(`${this.baseUrl}/generate-visual`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to generate visual');
    return res.json();
  }

  async captureLead(notes: string, name?: string, email?: string): Promise<LeadResponse> {
    const res = await fetch(`${this.baseUrl}/capture-lead`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes, attendee_name: name || null, attendee_email: email || null })
    });
    if (!res.ok) throw new Error('Failed to capture lead');
    return res.json();
  }

  async getLeads(): Promise<Lead[]> {
    const res = await fetch(`${this.baseUrl}/leads`);
    if (!res.ok) throw new Error('Failed to load leads');
    return res.json();
  }
}
