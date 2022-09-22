<template>
  <div class="results-pagination-end">
    <svgicon width="40" height="40" name="row-last" />
    <p>
      You have reached the current record limit ({{ limit | formatNumber }}). To
      view more records please refine your query
    </p>
  </div>
</template>
<script>
import "assets/icons/row-last";
export default {
  props: {
    limit: {
      type: Number,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.results-pagination-end {
  animation: fade 1s;
  padding: 3em 3em 0 3em;
  display: flex;
  align-items: center;
  color: $font-medium;
  .svg-icon {
    margin-right: 2em;
  }
}
@keyframes fade {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}
</style>
