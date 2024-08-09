<template>
  <MarkdownRenderer
    class="--body3"
    :markdown="guidelines || $t('noAnnotationGuidelines')"
  />
</template>

<script>
import { useAnnotationGuidelinesViewModel } from "./useAnnotationGuidelinesViewModel";
export default {
  setup() {
    return useAnnotationGuidelinesViewModel();
  },
};
</script>
