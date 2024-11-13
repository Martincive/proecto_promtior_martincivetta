import { Component } from '@angular/core';
import { ChatService } from './services/chatbot.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { OnInit } from '@angular/core';

interface Message {
  text: string;
  user: boolean;
  error: boolean;
}

@Component({
  selector: 'app-component',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
  ]
})
export class AppComponent implements OnInit {
  messages: Message[] = [];
  userMessage: string = '';
  isResponding: boolean = false;
  canSend: boolean = false;

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.messages.push({ text: "Hello! I am a chatbot designed to answer questions about Promtior ai. Ask me what you want!", user: false, error: false });
  }
  sendMessage(): void {
    if (!this.canSend) return;

    // Add the user's message to the chat
    this.messages.push({ text: this.userMessage, user: true, error: false });

  
    const messageToSend = this.userMessage;
    this.userMessage = '';
    this.isResponding = true;
    this.canSend = false;  

    this.chatService.sendRequest(messageToSend).subscribe({
      next: (response) => {
        this.messages.push({ text: response.answer, user: false, error: false });
        this.isResponding = false;
      },
      error: () => {
        this.messages.push({ text: "There has been an error connecting to the server", user: false, error: true });
        this.isResponding = false;
      }
    });
  }

  onMessageChange() {
    this.canSend = this.userMessage.trim() !== '';  
  }
}
