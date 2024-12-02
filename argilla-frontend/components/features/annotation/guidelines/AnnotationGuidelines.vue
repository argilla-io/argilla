<template>
  <MarkdownRenderer
    class="annotation-guidelines --body3"
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

<style lang="scss" scoped>
.annotation-guidelines {
  padding-inline: $base-space * 2;
}
</style>
