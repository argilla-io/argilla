<template>
  <SidebarProgress :dataset="dataset">
    <div v-if="annotationsProgress" class="labels">
      <div v-for="(counter, label) in getInfo" :key="label">
        <div v-if="counter > 0" class="info">
          <label>{{ label }}</label>
          <span class="records-number">{{ counter }}</span>
        </div>
      </div>
    </div>
  </SidebarProgress>
</template>

<script>
import { AnnotationProgress } from "@/models/AnnotationProgress";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    getInfo() {
      return this.annotationsProgress.annotatedAs;
    },
    annotationsProgress() {
      return AnnotationProgress.find(this.dataset.name + this.dataset.task);
    },
  },
};
</script>
<style lang="scss" scoped>
.labels {
  margin-top: 2em;
}
.info {
  position: relative;
  display: flex;
  margin-bottom: 0.7em;
  label {
    margin: 0; // for tagger
    &[class^="color_"] {
      padding: 0.3em;
    }
  }
}
</style>
