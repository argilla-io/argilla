<template>
  <div class="rule-query-token" :style="cssVars">
    <div class="rule-query-token__title-area">
      <h2 class="title">{{ title }}</h2>
      <span v-if="recordsValue">
        Records: <b>{{ recordsValue }}</b>
      </span>
    </div>
    <div class="rule-query-token__labels">
      <div class="label-item"><ButtonLabel /></div>
      <div class="label-item"><ButtonLabel /></div>
      <div class="label-item"><ButtonLabel /></div>
    </div>
  </div>
</template>

<script>
import ButtonLabel from "./ButtonLabel.component.vue";
export default {
  name: "RulesQueryToken",
  components: {
    ButtonLabel,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    recordsValue: {
      type: Number,
    },
    textColor: {
      type: String,
      default: () => "#000",
    },
    backgroundColor: {
      type: String,
      default: () => "#fff",
    },
    backgroundLabelColor: {
      type: String,
      default: () => "#fff",
    },
  },
  computed: {
    cssVars() {
      return {
        "--text-color": this.textColor,
        "--background-color": this.backgroundColor,
        "--background-label-color": this.backgroundLabelColor,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
* {
  margin: inherit;
}
.rule-query-token {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 2em;
  gap: 2em;
  color: var(--text-color);
  background-color: var(--background-color);
  border: 1px solid #e9eaed;
  border-radius: 10px;
  &__title-area {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: baseline;
    .title {
      padding-bottom: 0;
      margin-top: 0;
      @include font-size(22px);
      line-height: 22px;
      font-weight: bold;
    }
  }
  &__labels {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 10px;
  }
}

.label-item {
  display: inline-flex;
  border-radius: 8px;
  background-color: var(--background-label-color);
}
</style>
