/**
 * Copyright 2017 PokitDok, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ------------------------------------------------------------------------------
 */

import * as _ from 'lodash';

import { environment } from '../../../environments/environment';

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';
import { map, catchError, timeout } from 'rxjs/operators';

/**
 * Service to assist in retrieving data from a RESTful API.
 */
@Injectable()
export class APIService {

  // url used to reach the API
  apiURL: string;

  // defaults for paging settings
  pagingDefaults = {
    pageSize: 20,
    pageIndex: 0
  };

  // milliseconds before service times out
  apiTimeout = 10000;

  /**
   * @param http {HttpClient} - service for making HTTP requests
   */
  constructor(public http: HttpClient) {
    // set url from environment variables
    this.apiURL = environment.apiURL;

    // if API timeout specified, update
    if (environment.apiTimeout)
      this.apiTimeout = environment.apiTimeout;
  }

  /**
   * Simple GET request to API
   * @param endpoint {string} - API endpoint to call
   * @return {Observable} - observable watching the results of the API request
   */
  get(endpoint: string): Observable<any> {
    return this.http.get(`${this.apiURL}/${endpoint}`)
      .pipe(
        timeout(this.apiTimeout),
        catchError(err => throwError(() => err))
      );
  }

  /**
   * Retrieve paged list of items from an API.
   * @param resourceName {string} - name of the resource (what it's called in
   *   the API endpoint) to fetch from the API
   * @param params {object} - optional parameters to be passed to API to control
   *   things like paging
   * @param params.pageSize {number} - number of items returned in the API
   *   request as a page
   * @param params.pageIndex {number} - offset for items from API
   * @return {Observable} - observable watching the results of the API request
   */
  getItems(resourceName: string, params?: any): Observable<any[]> {
    let options: any = _.defaults(params, this.pagingDefaults);
    let url = this.apiURL + '/' + resourceName + '?limit=' + options['pageSize'];
    if (params && params['head']) {
      url += '&head=' + params['head'];
    }
    if (params && params['start']) {
      url += '&start=' + params['start'];
    }

    return this.http.get<any>(url)
      .pipe(
        timeout(this.apiTimeout),
        catchError(err => throwError(() => err))
      );
  }

  /**
   * Retrieve an item from the API by its unique identifier.
   * @param resourceName {string} - name of the resource (what it's called in
   *   the API endpoint) to fetch from the API
   * @param id {string} - unique identifier for retrieving the item from the API
   * @return {Observable} - observable watching the results of the API request
   */
  getItemByID(resourceName: string, id: string): Observable<any> {
    return this.http.get(`${this.apiURL}/${resourceName}/${id}`)
      .pipe(
        timeout(this.apiTimeout),
        map((response: any) => response.data),
        catchError(err => throwError(() => err))
      );
  }

}
