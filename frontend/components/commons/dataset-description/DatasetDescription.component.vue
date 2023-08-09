<template>
  <div class="description">
    <h2
      class="--heading5 --medium description__title"
      v-text="'Annotation guidelines'"
    />
    <BaseCardWithTabs :tabs="tabs">
      <template v-slot="{ currentComponent }">
        <component
          class="description__content"
          :markdown="sanitizedDescription"
          :value="sanitizedDescription"
          :is="currentComponent"
          :key="currentComponent"
          @change-text="onChangeTextArea"
        />
      </template>
    </BaseCardWithTabs>
  </div>
</template>

<script>
export default {
  props: {
    guidelines: {
      type: String,
    },
  },
  model: {
    prop: "guidelines",
    event: "input",
  },
  data() {
    return {
      tabs: [
        { name: "Write", component: "ContentEditableFeedbackTask" },
        { name: "Preview", component: "RenderMarkdownBaseComponent" },
      ],
    };
  },
  computed: {
    sanitizedDescription() {
      return this.guidelines ?? "";
    },
  },
  methods: {
    onChangeTextArea(newText) {
      this.$emit("input", newText);
    },
  },
};
</script>

<style lang="scss" scoped>
.description {
  &__content {
    min-height: 65px;
    display: block;
    background: palette(white);
    padding: $base-space * 2;
    border-radius: $border-radius;
    border: 1px solid $black-10;
    &:focus-within {
      border-color: $primary-color;
    }
  }
}
</style>
