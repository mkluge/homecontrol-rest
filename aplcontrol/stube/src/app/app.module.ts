import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';

import { AppComponent } from './app.component';
import { StatusViewComponent } from './status-view/status-view.component';
import { DataService } from './data.service';

@NgModule({
  declarations: [
    AppComponent,
    StatusViewComponent,
  ],
  imports: [
    HttpClientModule,
    BrowserModule,
    FormsModule,
    HttpModule
  ],
  providers: [DataService],
  bootstrap: [AppComponent]
})
export class AppModule { }
