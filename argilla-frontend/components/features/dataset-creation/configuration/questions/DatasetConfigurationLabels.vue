<template>
  <div>
    <div
      :class="{ '--error': errors.options?.length }"
      class="dataset-config-label__input-container"
    >
      <input
        type="text"
        :value="optionsJoinedByCommas"
        @input="onInput($event.target.value)"
        @focus.stop="onFocus"
        @blur="onBlur"
        :placeholder="placeholder"
        class="dataset-config-label__input"
      />
    </div>
    <Validation v-if="errors.options?.length" :validations="errors.options" />
    <label
      v-else
      class="dataset-config-label__label"
      v-text="
        $t('datasetCreation.questions.labelSelection.optionsSeparatedByComma')
      "
    />
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
  computed: {
    optionsJoinedByCommas() {
      return this.question.options.map((item) => item.text).join(",");
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
      const optionsArray = inputValue.split(",");
      const trimmedOptionsArray = optionsArray.map((text) => ({
        value: text.trim(),
        id: text.trim(),
        text: text,
      }));

      this.question.settings.options = trimmedOptionsArray;

      if (this.isDirty) {
        this.validateOptions();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$error-color: hsl(3, 100%, 69%);
.dataset-config-label {
  &__input-container {
    width: 100%;
    padding: 0 $base-space;
    border-radius: $border-radius;
    border: 1px solid var(--bg-opacity-10);
    background: var(--bg-accent-grey-1);
    &.--error {
      border-color: $error-color;
    }
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
    @include font-size(12px);
    @include input-placeholder {
      color: var(--fg-tertiary);
    }
  }
  &__label {
    color: var(--fg-secondary);
    @include font-size(12px);
  }
}
</style>
