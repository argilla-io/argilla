<template>
  <div class="rules__container">
    <div class="rules__annotation">
        NEW RULE: {{query}}
        <rules-annotation-area :dataset="dataset"/>
    </div>
    <div class="rules__metrics">
        METRICS
    </div>
  </div>
</template>
<script>
export default {
  computed: {
    query() {
      return this.dataset.query.text;
    }
  },
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
  }
};
</script>
<style lang="scss" scoped>
.rules {
  &__container {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  &__annotation {
    padding: 1em;
    background: $lighter-color;
    width: 100%;
    margin-right: 10px;
  }
  &__metrics {
    padding: 1em;
    background: $lighter-color;
    margin-right: 0;
    min-width: 200px;
  }
}
</style>


