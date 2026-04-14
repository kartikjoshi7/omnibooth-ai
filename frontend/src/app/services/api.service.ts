import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

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
  /** Dynamically resolves the API base URL for local dev vs Cloud Run production. */
  readonly baseUrl = window.location.port === '4200' ? 'http://localhost:8000' : '';

  constructor(private http: HttpClient) {}

  async generateVisual(prompt: string, image_data?: string): Promise<KioskResponse> {
    const payload: Record<string, string> = { prompt };
    if (image_data) payload['image_data'] = image_data;

    return firstValueFrom(
      this.http.post<KioskResponse>(`${this.baseUrl}/generate-visual`, payload)
    );
  }

  async captureLead(notes: string, name?: string, email?: string): Promise<LeadResponse> {
    return firstValueFrom(
      this.http.post<LeadResponse>(`${this.baseUrl}/capture-lead`, {
        notes,
        attendee_name: name || null,
        attendee_email: email || null
      })
    );
  }

  async getLeads(): Promise<Lead[]> {
    return firstValueFrom(
      this.http.get<Lead[]>(`${this.baseUrl}/leads`)
    );
  }

  async uploadDocs(text: string): Promise<{ message: string }> {
    return firstValueFrom(
      this.http.post<{ message: string }>(`${this.baseUrl}/upload-docs`, { text })
    );
  }

  async getAnalytics(): Promise<any[]> {
    return firstValueFrom(
      this.http.get<any[]>(`${this.baseUrl}/analytics`)
    );
  }
}
