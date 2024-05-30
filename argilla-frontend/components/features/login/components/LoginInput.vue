<template>
  <div class="input-field">
    <Validation :validations="showValidations ? translatedValidations : []">
      <label class="input-field__label" v-text="name" :for="name" />
      <span class="input-field__container">
        <input
          :aria-labelledby="name"
          v-model="inputValue"
          class="input-field__input"
          :name="name"
          :type="inputType"
          :placeholder="placeholder"
          :autofocus="autofocus"
          :autocomplete="autocomplete"
          :disabled="disabled"
          @keydown="onKeyDown"
          @blur="isBlurred = true"
        />
        <BaseButton
          v-if="type === 'password' && !!value"
          @on-click="toggleVisibility"
          class="input-field__toggle-visibility"
          >{{
            isPasswordVisible ? $t("login.hide") : $t("login.show")
          }}</BaseButton
        >
      </span>
    </Validation>
  </div>
</template>

<script>
export default {
  name: "InputField",
  props: {
    name: {
      type: String,
      default: "",
    },
    autofocus: {
      type: Boolean,
      default: false,
    },
    value: {
      type: String,
      default: "",
    },
    type: {
      type: String,
      default: "text",
    },
    placeholder: {
      type: String,
      default: "",
    },
    autocomplete: {
      type: String,
      default: "off",
    },
    validations: {
      type: Array,
      default: () => [],
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      originalValue: this.value,
      inputValue: this.value,
      isTouched: false,
      isBlurred: false,
      isPasswordVisible: false,
    };
  },
  model: {
    prop: "value",
    event: "input",
  },
  watch: {
    inputValue(newValue) {
      this.$emit("input", newValue);
    },
    value(newValue) {
      this.inputValue = newValue;
    },
    wasModified(newValue) {
      if (newValue) this.isTouched = true;
    },
  },
  computed: {
    wasModified() {
      return this.originalValue !== this.inputValue;
    },
    translatedValidations() {
      return this.validations.map((v) => this.$t(v));
    },
    showValidations() {
      return this.isTouched && this.isBlurred;
    },
    inputType() {
      return this.type === "password"
        ? this.isPasswordVisible
          ? "text"
          : "password"
        : this.type;
    },
  },
  methods: {
    toggleVisibility() {
      this.isPasswordVisible = !this.isPasswordVisible;
    },
    onKeyDown() {
      this.isTouched = true;
    },
  },
};
</script>

<style lang="scss" scoped>
.input-field {
  width: 100%;
  &__container {
    position: relative;
    display: block;
  }
  &__label {
    display: block;
    margin-bottom: calc($base-space / 2);
    color: $black-87;
    font-weight: 500;
  }
  &__input {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 100%;
    height: $base-space * 5.5;
    padding: $base-space * 2;
    background: palette(white);
    border: 1px solid $black-20;
    border-radius: $border-radius;
    outline: 0;
    @include font-size(16px);
    @include input-placeholder {
      color: $black-37;
      @include font-size(16px);
    }
    &:focus {
      border: 1px solid $primary-color;
    }
  }
  &__toggle-visibility.button {
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    padding: $base-space $base-space * 2;
    color: $primary-color;
    @include font-size(12px);
  }
}
.--has-error input {
  border-color: $black-20;
  &:focus {
    border-color: $primary-color;
  }
}

input,
textarea,
select {
  &:-webkit-autofill {
    &,
    &:hover,
    &:focus {
      -webkit-text-fill-color: $black-87;
      -webkit-box-shadow: 0 0 0px 1000px palette(white) inset;
      box-shadow: 0 0 0px 1000px palette(white) inset;
      transition: background-color 5000s ease-in-out 0s;
    }
  }
}
</style>
