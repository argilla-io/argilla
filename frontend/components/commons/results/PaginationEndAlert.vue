<template>
  <div class="results-pagination-end">
    <svgicon width="40" height="40" name="row-last" />
    <div class="desc">
      <p>
        You cannot go through more than {{ limit | formatNumber }} records. If
        you want to explore more records, you can combine queries, filters, and
        sorting to fine-grain your search. For more info about queries, visit
        the
        <a
          href="https://docs.argilla.io/en/latest/guides/features/queries.html?highlight=queries#"
          target="_blank"
        >
          docs</a
        >. If you want, you can configure this limit at the cost of potential
        performance loss. For more details about this limit, see
        <a
          href="https://docs.argilla.io/en/latest/reference/webapp/pages.html#dataset"
          target="_blank"
        >
          here
        </a>
      </p>
    </div>
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
  display: flex;
  animation: fade 1s;
  padding: 3em 3em 0 3em;
  align-items: center;
  color: $black-54;
  .svg-icon {
    margin-right: 2em;
  }
  .desc {
    flex: 1;
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
