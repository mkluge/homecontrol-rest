import { Injectable } from '@angular/core';

@Injectable()
export class Configuration {
    public MediaRestServer = 'http://192.168.178.38:5000/';
    public SatUrl = 'sat/';
    public SatApiUrl = this.MediaRestServer + this.SatUrl;
}
