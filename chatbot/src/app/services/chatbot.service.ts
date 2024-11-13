import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ChatEndpoints } from './endpoints';
import { IResponseModel } from './iresponse.model';



@Injectable({
  providedIn: 'root'
})
export class ChatService {
    constructor(private http: HttpClient) {}

  // Simulate a chat response
  sendRequest(userMessage: string): Observable<IResponseModel> {
    const headers = new HttpHeaders({
        'Content-Type': 'application/json',
      });
    return this.http.post<IResponseModel>(ChatEndpoints.APP_API, {question: userMessage},{headers});
  }
}