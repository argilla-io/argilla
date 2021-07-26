import { Model } from "@vuex-orm/core";

class Pagination extends Model {
  static entity = "pagination_settings";

  static fields() {
    return {
      id: this.string(null),
      size: this.number(20),
      page: this.number(1),
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
    };
  }
}

export { Pagination, DatasetViewSettings };
