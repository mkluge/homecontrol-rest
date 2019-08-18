import { Injectable } from '@angular/core';
import { Http } from '@angular/http';

import { map } from 'rxjs/operators';
import { Configuration } from './app.constants';

@Injectable()
export class DataService {
  config: Configuration;
  http: Http;
  url: string;
  constructor(http: Http) {
    this.http = http;
    this.url = this.config.SatApiUrl+"/power";
  }

  getData() {
    const observable = this.http.get(this.url);
    const jsonObservable = observable.pipe(map((response) => response.json().data));
    return jsonObservable;
  }
}
