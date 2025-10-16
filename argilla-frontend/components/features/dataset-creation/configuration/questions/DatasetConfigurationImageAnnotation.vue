<template>
  <div>
    <!-- Labels Input -->
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

    <!-- Image Field Selector -->
    <DatasetConfigurationFieldSelector
      class="config-card__type"
      :options="imageFields"
      v-model="question.settings.field"
    />
    <Validation v-if="errors.field?.length" :validations="errors.field" />

    <!-- Shape Types Selector -->
    <div class="shape-types-section">
      <label class="shape-types-section__label">
        {{ $t('datasetCreation.questions.imageAnnotation.shapeTypes') }}
      </label>
      <div class="shape-types-section__options">
        <label
          v-for="shapeType in availableShapeTypes"
          :key="shapeType.value"
          class="shape-type-checkbox"
        >
          <input
            type="checkbox"
            :value="shapeType.value"
            :checked="isShapeTypeSelected(shapeType.value)"
            @change="toggleShapeType(shapeType.value)"
          />
          <span class="shape-type-checkbox__label">{{ shapeType.label }}</span>
        </label>
      </div>
    </div>

    <!-- Allow Multiple Checkbox -->
    <BaseCheckbox
      class="config-option"
      :value="question.settings.allow_multiple"
      @input="question.settings.allow_multiple = !question.settings.allow_multiple"
    >
      {{ $t('datasetCreation.questions.imageAnnotation.allowMultiple') }}
    </BaseCheckbox>
  </div>
</template>

<script>
export default {
  data() {
    return {
      errors: {},
      isDirty: false,
      availableShapeTypes: [
        { value: "rectangle", label: "Rectangle (Bounding Box)" },
        { value: "polygon", label: "Polygon" },
      ],
    };
  },
  props: {
    question: {
      type: Object,
      required: true,
    },
    imageFields: {
      type: Array,
      required: true,
    },
    placeholder: {
      type: String,
      default: "",
    },
  },
  watch: {
    "question.settings.field": {
      handler() {
        this.validateOptions();
      },
      immediate: true,
    },
    imageFields: {
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
    isShapeTypeSelected(shapeType) {
      if (!this.question.settings.shape_types) {
        // Default to rectangle and polygon if not set
        this.question.settings.shape_types = ["rectangle", "polygon"];
      }
      return this.question.settings.shape_types.includes(shapeType);
    },
    toggleShapeType(shapeType) {
      if (!this.question.settings.shape_types) {
        this.question.settings.shape_types = ["rectangle", "polygon"];
      }

      const index = this.question.settings.shape_types.indexOf(shapeType);
      if (index > -1) {
        // Remove if already selected (but keep at least one)
        if (this.question.settings.shape_types.length > 1) {
          this.question.settings.shape_types.splice(index, 1);
        }
      } else {
        // Add if not selected
        this.question.settings.shape_types.push(shapeType);
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

.shape-types-section {
  margin-top: $base-space * 2;

  &__label {
    display: block;
    color: var(--fg-secondary);
    @include font-size(12px);
    font-weight: 500;
    margin-bottom: $base-space;
  }

  &__options {
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
}

.shape-type-checkbox {
  display: flex;
  align-items: center;
  gap: $base-space;
  cursor: pointer;
  color: var(--fg-secondary);
  @include font-size(12px);

  input[type="checkbox"] {
    cursor: pointer;
    width: 16px;
    height: 16px;
    border: 1px solid var(--bg-opacity-20);
    border-radius: $border-radius-s;

    &:checked {
      accent-color: var(--fg-cuaternary);
    }
  }

  &__label {
    user-select: none;
  }

  &:hover {
    color: var(--fg-primary);
  }
}

.config-option {
  margin-top: $base-space * 2;
  display: flex;
  gap: $base-space;
  @include font-size(12px);
  flex-flow: row-reverse;
  justify-content: flex-end;

  &:deep(.checkbox__container) {
    margin: 0;
    border-color: var(--bg-opacity-20);
    background: var(--bg-accent-grey-1);
  }
}
</style>
