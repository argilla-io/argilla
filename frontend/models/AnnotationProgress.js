import { Model } from "@vuex-orm/core";

class AnnotationProgress extends Model {
  static entity = "annotation_progress";

  static fields() {
    return {
      id: this.string(null),
      total: this.number(0),
      validated: this.number(0),
      discarded: this.number(0),
      annotatedAs: this.attr(null),
    };
  }
}

export { AnnotationProgress };
