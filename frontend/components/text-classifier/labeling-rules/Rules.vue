<template>
  <div>
    <div class="rules__container">
      <p class="rules__query">{{query}}</p>
      <rules-annotation-area :currentRule="currentRule" :dataset="dataset" @update-rule="updateRule"/>
    </div>
    <p>Records ({{dataset.results.total}})</p>
  </div>
</template>
<script>
import { mapActions } from "vuex";
export default {
  computed: {
    query() {
      return this.dataset.query.text;
    }
  },
  data: () => {
    return {
      currentRule: undefined,
    }
  },
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
  },
  async fetch() {
    this.currentRule = await this.getRule({
      dataset: this.dataset,
      query: this.query
    });
  },
  watch: {
    query(n, o) {
      if (o !== n) {
        this.$fetch()
      }
    }
  },
  methods: {
    updateRule() {
      this.$fetch()
    },
    ...mapActions({
      getRule: "entities/text_classification/getRule",
    }),
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


