<template>
  <div>
    <div
      :class="{ '--error': errors.options?.length }"
      class="dataset-config-rating__input-container"
    >
      <input
        type="number"
        min="0"
        max="10"
        step="1"
        :value="
          question.settings.options.length
            ? question.settings.options.length - 1
            : 0
        "
        @input="onInput($event.target.value)"
        @focus.stop="onFocus"
        @blur="onBlur"
        :placeholder="placeholder"
        class="dataset-config-rating__input"
      />
    </div>
    <Validation v-if="errors.options?.length" :validations="errors.options" />
  </div>
</template>

<script>
export default {
  data() {
    return {
      errors: {},
      isDirty: false,
    };
  },
  props: {
    question: {
      type: Object,
      required: true,
    },
    placeholder: {
      type: String,
      default: "",
    },
  },
  methods: {
    validateOptions() {
      this.errors = this.question.validate();
    },
    onFocus() {
      this.$emit("is-focused", true);
    },
    onBlur() {
      this.isDirty = true;
      this.validateOptions();
      this.$emit("is-focused", false);
    },
    onInput(inputValue) {
      let value = parseInt(inputValue);
      value = Math.max(1, Math.min(value, 10));

      const valuesArray = Array.from({ length: value + 1 }, (_, i) => ({
        value: i,
      }));

      this.question.settings.options = valuesArray;

      if (this.isDirty) {
        this.validateOptions();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-config-rating__input-container {
  width: 100px;
  padding: 0 $base-space;
  border-radius: $border-radius;
  border: 1px solid var(--bg-opacity-10);
  background: var(--bg-accent-grey-1);
  &:focus-within {
    border-color: var(--fg-cuaternary);
  }
}
.dataset-config-rating__input {
  height: calc($base-space * 4 - 2px);
  padding: 0;
  border: none;
  background: none;
  width: 100%;
  outline: none;
  color: var(--fg-secondary);
  @include font-size(12px);
  @include input-placeholder {
    color: var(--fg-tertiary);
  }
}
</style>
