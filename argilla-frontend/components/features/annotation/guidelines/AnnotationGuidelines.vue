<template>
  <RenderMarkdownBaseComponent class="--body3" :markdown="guidelines" />
</template>

<script>
import { useAnnotationGuidelinesViewModel } from "./useAnnotationGuidelinesViewModel";
export default {
  props: {
    guidelines: {
      type: String,
      required: true,
    },
  },
  setup() {
    return useAnnotationGuidelinesViewModel();
  },
};
</script>
