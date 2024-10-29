<template>
  <div class="dataset-config-ranking">
    <div
      class="dataset-config-ranking__input-container"
      v-for="(item, index) in value"
      :key="index"
    >
      <input
        type="text"
        :value="item.value"
        @input="onInput(index, $event.target.value)"
        @focus="$emit('is-focused', true)"
        @blur="$emit('is-focused', false)"
        :placeholder="placeholder"
        class="dataset-config-ranking__input"
      />
      <BaseButton
        v-if="value.length >= 3"
        @click="removeOption(item)"
        class="dataset-config-ranking__remove-button"
      >
        <svgicon name="close" width="12" color="var(--fg-tertiary)" />
      </BaseButton>
    </div>
    <BaseButton
      @click="addOption"
      class="secondary small dataset-config-ranking__add-button"
      ><svgicon name="plus" width="12" color="var(--fg-secondary)" /> Include
      option</BaseButton
    >
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: Array,
      required: true,
    },
    placeholder: {
      type: String,
      default: "",
    },
  },
  model: {
    prop: "value",
    event: "on-value-change",
  },
  methods: {
    removeOption(item) {
      const newValue = this.value.filter((value) => value !== item);
      this.$emit("on-value-change", newValue);
    },
    addOption() {
      const newValue = [
        ...this.value,
        {
          value: `option ${this.value.length + 1}`,
          text: `option ${this.value.length + 1}`,
        },
      ];
      this.$emit("on-value-change", newValue);
    },
    onInput(index, value) {
      const newValue = this.value.map((item, i) =>
        i === index ? { ...item, value } : item
      );
      this.$emit("on-value-change", newValue);
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-config-ranking {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  &__input-container {
    display: flex;
    align-items: center;
    align-content: space-between;
    width: 100%;
    padding: 0 $base-space;
    border-radius: $border-radius;
    border: 1px solid var(--bg-opacity-10);
    background: var(--bg-accent-grey-1);
    &:focus-within {
      border-color: var(--fg-cuaternary);
    }
  }
  &__input {
    height: calc($base-space * 4 - 2px);
    padding: 0;
    border: none;
    background: none;
    width: 100%;
    outline: none;
    color: var(--fg-secondary);
    @include input-placeholder {
      color: var(--fg-tertiary);
    }
  }
  &__remove-button.button {
    padding: 0;
  }
  &__add-button {
    margin-right: auto;
  }
}
</style>
