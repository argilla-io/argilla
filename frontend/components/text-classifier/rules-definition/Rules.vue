<template>
  <div>
    <div class="rules__container">
      <p class="rules__query">{{query}}</p>
      <rules-annotation-area :dataset="dataset"/>
    </div>
    <p>Records ({{dataset.results.total}})</p>
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
    padding: 20px;
    background: $lighter-color;
    width: 100%;
    border-radius: 5px;
    margin-bottom: 2em;
  }
  &__query {
    color: $font-secondary-dark;
    @include font-size(16px);
    font-weight: 300;
    margin-top: 0;
  }
}
</style>


