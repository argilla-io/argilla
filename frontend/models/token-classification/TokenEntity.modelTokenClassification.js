import { Model } from "@vuex-orm/core";
class TokenEntity extends Model {
  static entity = "tokenEntities";

  static fields() {
    return {
      id: this.uid(),
      record_id: this.string(null),
      agent: this.string(null),
      label: this.attr(null),
      start: this.attr(null),
      end: this.attr(null),
      score: this.attr(null),
      entitable_id: this.attr(null),
      entitable_type: this.attr(null),

      // relationship
      token_entitable: this.morphTo("entitable_id", "entitable_type"),
    };
  }
}

export { TokenEntity };
