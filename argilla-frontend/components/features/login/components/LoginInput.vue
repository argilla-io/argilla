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
          :autocomplete="autocomplete"
          :disabled="disabled"
          @keydown="onKeyDown"
          @blur="isBlurred = true"
          @animationstart="checkAnimation"
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
    checkAnimation(e) {
      if (e.animationName == "onAutoFillStart") {
        this.$emit("onCheckAutoFilled", true);
      } else if (e.animationName == "onAutoFillCancel") {
        this.$emit("onCheckAutoFilled", false);
      }
    },
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
    color: var(--fg-primary);
    font-weight: 500;
  }
  &__input {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 100%;
    height: $base-space * 5.5;
    padding: $base-space * 2;
    background: var(--bg-accent-grey-2);
    color: var(--fg-primary);
    border: 1px solid var(--bg-opacity-20);
    border-radius: $border-radius;
    outline: 0;
    @include font-size(16px);
    @include input-placeholder {
      color: var(--fg-tertiary);
      @include font-size(16px);
    }
    &:focus {
      border: 1px solid var(--fg-cuaternary);
    }
  }
  &__toggle-visibility.button {
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    padding: $base-space $base-space * 2;
    color: var(--fg-cuaternary);
    @include font-size(12px);
  }
}
.--has-error input {
  border-color: var(--bg-opacity-20);
  &:focus {
    border-color: var(--fg-cuaternary);
  }
}

input,
textarea,
select {
  &:-webkit-autofill {
    &,
    &:hover,
    &:focus {
      -webkit-text-fill-color: var(--fg-primary);
      -webkit-box-shadow: 0 0 0px 1000px var(--bg-accent-grey-2) inset;
      box-shadow: 0 0 0px 1000px var(--bg-accent-grey-2) inset;
      transition: background-color 5000s ease-in-out 0s;
    }
  }
}
:-webkit-autofill {
  animation-name: onAutoFillStart;
}
:not(:-webkit-autofill) {
  animation-name: onAutoFillCancel;
}
</style>

<style>
@keyframes onAutoFillStart {
  from {
    /**/
  }
  to {
    /**/
  }
}
@keyframes onAutoFillCancel {
  from {
    /**/
  }
  to {
    /**/
  }
}
</style>
