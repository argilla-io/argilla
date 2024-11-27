<template>
  <div>
    <div
      class="dataset-config-label__input-container"
      :class="{ '--error': errors.options?.length || errors.field?.length }"
    >
      <input
        type="text"
        :value="optionsJoinedByCommas"
        @input="onInput($event.target.value)"
        @focus="onFocus"
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

    <DatasetConfigurationFieldSelector
      class="config-card__type"
      :options="textFields"
      v-model="question.settings.field"
    />
    <Validation v-if="errors.field?.length" :validations="errors.field" />
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
    textFields: {
      type: Array,
      required: true,
    },
    placeholder: {
      type: String,
      default: "",
    },
  },
  watch: {
    textFields: {
      handler() {
        this.validateOptions();
      },
      immediate: true,
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
        color: this.$color.generate(text),
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
