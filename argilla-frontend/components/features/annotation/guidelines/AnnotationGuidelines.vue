<template>
  <RenderMarkdownBaseComponent class="--body3" :markdown="guidelines" />
</template>

<script>
import { useAnnotationGuidelinesViewModel } from "./useAnnotationGuidelinesViewModel";
export default {
  setup() {
    return useAnnotationGuidelinesViewModel();
  },
};
</script>
