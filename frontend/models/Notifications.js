import { Model } from "@vuex-orm/core";

class Notification extends Model {
  static entity = "notifications";

  static fields() {
    return {
      id: this.uid(() => uuid()),
    };
  }
}

export { Notification };
