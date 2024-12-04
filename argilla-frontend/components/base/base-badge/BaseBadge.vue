<template>
  <div class="badge">
    <p v-if="!clickable" v-html="text" />
    <BaseButton @click="onClick" v-else class="--clickable">{{
      text
    }}</BaseButton>
  </div>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
      required: true,
    },
    fontSize: {
      type: String,
      default: "12px",
    },
    color: {
      type: String,
      default: "var(--fg-secondary)",
    },
  },
  data() {
    return {
      clickable: false,
    };
  },
  mounted() {
    if (this.$listeners["on-click"]) {
      this.clickable = true;
    }
  },
  methods: {
    onClick($event) {
      this.$emit("on-click", $event);
    },
  },
};
</script>

<style lang="scss" scoped>
.badge {
  p,
  .button {
    display: flex;
    align-items: center;
    max-height: calc(v-bind(fontSize) * 2);
    width: fit-content;
    padding: 0.8em;
    border: 1px solid v-bind(color);
    border-radius: $border-radius-rounded;
    margin: 0;
    color: v-bind(color);
    font-size: v-bind(fontSize);
    &.--clickable {
      cursor: pointer;
      background-color: var(--bg-opacity-4);
      border: unset;
      &:hover {
        background-color: var(--bg-opacity-10);
      }
    }
  }
}
</style>
