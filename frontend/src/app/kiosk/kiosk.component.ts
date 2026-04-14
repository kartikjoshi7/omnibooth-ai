import { Component, ChangeDetectorRef, ViewChild, ElementRef, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, KioskResponse } from '../services/api.service';

@Component({
  selector: 'app-kiosk',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="kiosk-container">
      <header class="glass-panel text-center" role="banner">
        <h1>OmniBooth Multimodal JARVIS Kiosk</h1>
        <p class="text-secondary">Speak your structural constraints and supply spatial references securely</p>
      </header>

      <main class="main-content" role="main" aria-label="Kiosk Command Matrix">
        <section class="input-section glass-panel" aria-label="Multimodal Data Ingestion Area">
          <textarea
            class="input-primary"
            aria-label="Mechanical Engineering Vector Prompt Input TextField"
            [(ngModel)]="prompt"
            rows="3"
            placeholder="E.g., Modify the attached badge/part for cryogenic 4000 ATM resilience"
          ></textarea>
          
          <div class="mic-controls mt-2" *ngIf="speechRecognition">
             <button class="btn-mic" aria-label="Toggle Voice Control Sequence" [class.pulsing-mic]="isListening" (click)="toggleListening()">
                🎤 {{ isListening ? 'Listening... (Speak Now)' : 'Tap to Speak' }}
             </button>
          </div>
          
          <div class="camera-module mt-3" aria-label="Initiate Visual Subsystem Feed" *ngIf="!cameraStream" (click)="startCamera()" tabindex="0">
             <p>📷 Click to Enable Spatial Scan (Camera API)</p>
          </div>
          
          <div class="camera-active mt-3" *ngIf="cameraStream">
             <video #videoElement autoplay playsinline aria-label="Active Security Camera Feed Monitor" class="video-preview"></video>
             <button class="btn-primary mt-2" aria-label="Capture Secure Spatial Frame" (click)="captureImage()" *ngIf="!capturedImage">Capture Reference</button>
             <div class="captured-preview mt-2" *ngIf="capturedImage">
                 <img [src]="capturedImage" alt="Captured Scene Reference" class="preview-img" />
                 <button class="btn-secondary" aria-label="Purge Captured Visual and Retake" (click)="capturedImage = null">Retake Scan</button>
             </div>
          </div>

          <button class="btn-primary mt-3 w-100" aria-label="Execute Kiosk Reasoning Loop" (click)="generate()" [disabled]="isLoading || (!prompt.trim() && !capturedImage) || isListening">
            {{ isLoading ? 'Rendering Spatial Physics...' : 'Generate Contextual Media' }}
          </button>
        </section>

        <section class="media-container glass-panel mt-4" aria-label="Generation Feedback Sandbox" *ngIf="result || isLoading">
          <div *ngIf="isLoading" class="parsing-metrics pulsing" aria-live="polite">
            <div class="metric">Extracting Vision Vectors...</div>
            <div class="metric">Calculating Spatial Load...</div>
            <div class="metric">Compiling Cross-Reference Simulation...</div>
          </div>
          
          <div *ngIf="result && !isLoading" class="result-view" aria-live="polite">
            <div class="audio-controls mb-2" *ngIf="isSpeaking">
                <button class="btn-secondary" aria-label="Mute TTS Synthetic Output" (click)="stopSpeaking()">🔇 Stop Audio</button>
            </div>
            <img [src]="result.media_url" alt="Simulated Visual Generation Output" class="media-render" />
            <div class="message mt-3">
              <h3>Agentic AI Context:</h3>
              <p>{{ result.message }}</p>
            </div>
          </div>
        </section>
      </main>
      
      <!-- Hidden canvas for capturing frames -->
      <canvas #canvasElement style="display:none;"></canvas>
    </div>
  `,
  styles: [`
    .kiosk-container { padding: 40px; max-width: 900px; margin: 0 auto; min-height: 100vh; display: flex; flex-direction: column; gap: 30px; }
    .text-center { text-align: center; }
    .text-secondary { color: var(--text-secondary); margin-top: 10px; }
    .mt-2 { margin-top: 10px; }
    .mt-3 { margin-top: 15px; }
    .mt-4 { margin-top: 25px; }
    .mb-2 { margin-bottom: 10px; }
    .w-100 { width: 100%; }
    
    .btn-mic { background: transparent; border: 1px solid var(--accent-color); color: var(--accent-color); padding: 10px 15px; border-radius: 8px; cursor: pointer; transition: 0.3s; width: 100%; display: block; font-weight: bold; font-size: 1.1em;}
    .btn-mic:hover { background: rgba(0,255,204,0.1); }
    .pulsing-mic { animation: pulse-mic 1.5s infinite; background: rgba(0,255,204,0.2); border-color: transparent; }
    @keyframes pulse-mic {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(0,255,204,0.4); }
        70% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(0,255,204,0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(0,255,204,0); }
    }
    .audio-controls { text-align: right; }
    
    .camera-module {
      border: 1px dashed var(--accent-color);
      padding: 15px;
      text-align: center;
      cursor: pointer;
      color: var(--accent-color);
      border-radius: 8px;
      transition: background 0.2s;
    }
    .camera-module:hover { background: rgba(0,255,204,0.1); }
    .video-preview { width: 100%; border-radius: 8px; border: 1px solid var(--glass-border); max-height: 250px; object-fit: cover; }
    .preview-img { width: 150px; border-radius: 8px; border: 1px solid var(--accent-color); margin-right: 15px; }
    .captured-preview { display: flex; align-items: center; }
    .btn-secondary { background: transparent; border: 1px solid #ff4d4d; color: #ff4d4d; padding: 5px 15px; border-radius: 4px; cursor: pointer; }
    
    .media-container { min-height: 300px; display: flex; align-items: center; justify-content: center; flex-direction: column; border: 1px dashed var(--glass-border); position: relative; padding: 15px; }
    .parsing-metrics { color: var(--accent-color); font-family: monospace; font-size: 1.1em; display: flex; flex-direction: column; gap: 10px; }
    .result-view { width: 100%; text-align: left; }
    .media-render { width: 100%; height: auto; max-height: 500px; object-fit: cover; border-radius: 8px; border: 1px solid var(--accent-color); }
    .message { background: rgba(0,255,204,0.1); padding: 15px; border-left: 4px solid var(--accent-color); border-radius: 0 8px 8px 0; }
  `]
})
export class KioskComponent implements OnInit, OnDestroy {
  prompt = '';
  isLoading = false;
  result: KioskResponse | null = null;
  
  cameraStream: MediaStream | null = null;
  capturedImage: string | null = null;

  // Web Speech API
  speechRecognition: any = null;
  isListening = false;
  
  synth: SpeechSynthesis = window.speechSynthesis;
  isSpeaking = false;

  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvasElement') canvasElement!: ElementRef<HTMLCanvasElement>;

  constructor(private apiService: ApiService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.initSpeechRecognition();
    // Warm up voice list
    if (this.synth.onvoiceschanged !== undefined) {
       this.synth.onvoiceschanged = () => this.synth.getVoices();
    }
  }

  initSpeechRecognition() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.speechRecognition = new SpeechRecognition();
      this.speechRecognition.continuous = false;
      this.speechRecognition.interimResults = false;
      this.speechRecognition.lang = 'en-US';

      this.speechRecognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        this.prompt = transcript;
        this.cdr.detectChanges();
      };

      this.speechRecognition.onend = () => {
        this.isListening = false;
        this.cdr.detectChanges();
        // Auto-generate if audio was captured and we aren't already loading
        if (this.prompt.trim() && !this.isLoading) {
           this.generate();
        }
      };
      
      this.speechRecognition.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        this.isListening = false;
        this.cdr.detectChanges();
      };
    } else {
      console.warn("Speech Recognition API is not supported in this browser.");
    }
  }

  toggleListening() {
    if (!this.speechRecognition) return;
    
    if (this.isListening) {
      this.speechRecognition.stop();
    } else {
      // Clear the prompt dynamically before new translation
      this.prompt = '';
      try {
        this.speechRecognition.start();
        this.isListening = true;
      } catch (e) {
        console.error("Speech Recognition start failed", e);
      }
    }
    this.cdr.detectChanges();
  }

  speakMessage(text: string) {
    if (!this.synth) return;
    this.synth.cancel(); // Clear any existing queued speech
    
    const utterance = new SpeechSynthesisUtterance(text);
    const voices = this.synth.getVoices();
    
    // Attempt to prioritize natural-sounding assistant voices
    const preferredVoice = voices.find(v => 
       v.name.includes('Female') || 
       v.name.includes('Google') || 
       v.name.includes('Samantha') || 
       v.name.includes('Siri')
    );
    if (preferredVoice) {
       utterance.voice = preferredVoice;
    }
    
    utterance.onstart = () => { this.isSpeaking = true; this.cdr.detectChanges(); };
    utterance.onend = () => { this.isSpeaking = false; this.cdr.detectChanges(); };
    utterance.onerror = () => { this.isSpeaking = false; this.cdr.detectChanges(); };
    
    this.synth.speak(utterance);
  }

  stopSpeaking() {
    if (this.synth) {
       this.synth.cancel();
       this.isSpeaking = false;
       this.cdr.detectChanges();
    }
  }

  async startCamera() {
    try {
      this.cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.cdr.detectChanges();
      
      // Allow view to render the element first
      setTimeout(() => {
        if (this.videoElement) {
          this.videoElement.nativeElement.srcObject = this.cameraStream;
          this.videoElement.nativeElement.play();
        }
      }, 100);
    } catch (err) {
      console.error("Camera access denied", err);
      alert("Please allow camera permissions to use Spatial Scan.");
    }
  }

  captureImage() {
    if (!this.videoElement || !this.canvasElement) return;
    const video = this.videoElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d')?.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Extract base64
    this.capturedImage = canvas.toDataURL('image/jpeg', 0.8);
    this.cdr.detectChanges();
  }

  ngOnDestroy() {
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(track => track.stop());
    }
    this.stopSpeaking();
  }

  async generate() {
    this.isLoading = true;
    this.result = null;
    this.stopSpeaking(); // Stop any currently playing audio on new generation
    this.cdr.detectChanges();
    try {
      this.result = await this.apiService.generateVisual(this.prompt, this.capturedImage || undefined);
      if (this.result && this.result.message) {
         this.speakMessage(this.result.message);
      }
    } catch (err) {
      console.error(err);
      alert('Error generating media.');
    } finally {
      this.isLoading = false;
      this.cdr.detectChanges();
    }
  }
}
