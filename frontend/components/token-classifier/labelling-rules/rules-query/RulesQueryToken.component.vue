<template>
  <div class="rule-query-token" :style="cssVars">
    <div class="rule-query-token__title-area">
      <h2 class="title">{{ title }}</h2>
      <span v-if="entitiesLength">
        Records: <b>{{ entitiesLength }}</b>
      </span>
    </div>
    <div class="rule-query-token__chips">
      <ChipsComponent :chips="entities" />
    </div>
  </div>
</template>

<script>
import ChipsComponent from "./Chips.component.vue";
export default {
  name: "RulesQueryToken",
  components: {
    ChipsComponent,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    entities: {
      type: Array,
      required: true,
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
    entitiesLength() {
      return this.entities.length;
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
  &__chips {
    display: flex;
    flex-direction: row;
    gap: 10px;
  }
}
</style>
