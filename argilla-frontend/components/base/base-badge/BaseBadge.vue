<template>
  <p v-if="!clickable" class="badge" v-html="text" />
  <BaseButton @click="onClick" v-else class="badge --clickable">{{
    text
  }}</BaseButton>
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
.badge.button,
.badge {
  display: flex;
  align-items: center;
  height: calc(v-bind(fontSize) * 2);
  width: fit-content;
  padding: 0.8em;
  border: 1px solid var(--fg-tertiary);
  border-radius: $border-radius-rounded;
  margin: 0;
  color: var(--fg-secondary);
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
</style>
