/*
 * coding=utf-8
 * Copyright 2021-present, the Recognai S.L. team.
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
 */

import { Model } from "@vuex-orm/core";

class Pagination extends Model {
  static entity = "pagination_settings";

  static fields() {
    return {
      id: this.string(null),
      size: this.number(5),
      page: this.number(1),
      pageSizeOptions: this.attr([1, 5, 10, 20]),
      allowKeyboardPagination: this.boolean(true),
    };
  }

  get from() {
    return (this.page - 1) * this.size;
  }
}

export default class DatasetViewSettings extends Model {
  static entity = "view_settings";

  static fields() {
    return {
      id: this.string(null),
      pagination: this.hasOne(Pagination, "id"),
      annotationEnabled: this.boolean(false),
      loading: this.boolean(false),
      headerHeight: this.number(140),
    };
  }
}

export { Pagination, DatasetViewSettings };
