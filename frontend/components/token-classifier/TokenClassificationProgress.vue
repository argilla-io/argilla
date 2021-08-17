<template>
  <SidebarProgress :dataset="dataset">
    <div v-if="annotationsProgress" class="labels">
      <div v-for="(counter, label) in getInfo" :key="label">
        <div v-if="counter > 0" class="info">
          <label
            :class="[
              `color_${entities.filter((e) => e.text === label)[0].colorId}`,
              'entity',
            ]"
            >{{ label }}</label
          >
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
      return this.dataset.results.aggregations.annotated_as;
    },
    annotationsProgress() {
      return AnnotationProgress.find(this.dataset.name + this.dataset.task);
    },
    entities() {
      return this.dataset.entities;
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
$colors: 50;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(
    ($colors * $i) + ($hue * $i / $colors),
    100% - $i / 2,
    82% - ($colors % $i),
    1
  );
  .color_#{$i - 1} {
    background: $rcolor;
  }
}
</style>
