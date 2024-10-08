<template>
  <div>
    <div class="dataset-config-label__input-container">
      <input
        :class="{ error: error }"
        type="text"
        :value="namesJoinedByCommas"
        @input="onInput($event.target.value)"
        @focus="onFocus"
        @blur="onBlur"
        :placeholder="placeholder"
        class="dataset-config-label__input"
      />
    </div>
    <label
      class="dataset-config-label__label --error"
      v-if="error"
      v-text="error"
    />
    <label
      v-else
      class="dataset-config-label__label"
      v-text="`Use coma to separate labels`"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      error: "",
      isDirty: false,
    };
  },
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
  computed: {
    namesJoinedByCommas() {
      return this.value.map((item) => item.name).join(", ");
    },
  },
  watch: {
    error(newValue) {
      if (this.isDirty && newValue) {
        this.validateNames();
      }
    },
  },
  methods: {
    validateNames() {
      const options = this.value.map((item) => item.name);
      console.log(options);
      if (!options.length) {
        this.error = "At least two labels are required";
      } else if (options.some((option) => !option)) {
        this.error = "Empty labels are not allowed";
      } else {
        this.error = "";
      }
    },
    onFocus() {
      this.$emit("is-focused", true);
    },
    onBlur() {
      this.isDirty = true;
      this.validateNames();
      this.$emit("is-focused", false);
    },
    onInput(inputValue) {
      const namesArray = inputValue.split(",");
      const trimmedNamesArray = namesArray.map((name) => ({
        name: name.trim(),
      }));
      this.$emit("on-value-change", trimmedNamesArray);
      if (this.isDirty) {
        this.validateNames();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-config-label {
  &__input-container {
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
  &__label {
    color: var(--fg-tertiary);
    @include font-size(12px);
    &--error {
      color: var(--fg-error);
    }
  }
}
</style>
