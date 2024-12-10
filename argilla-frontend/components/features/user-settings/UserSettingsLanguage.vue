<template>
  <div class="language-switch">
    <BaseTooltip
      class="language-switch__item"
      v-for="{ code, name } in languages"
      :key="code"
      :text="name"
      :minimalist="false"
    >
      <input
        type="radio"
        :id="code"
        :value="code"
        v-model="$i18n.locale"
        @input="change(code)"
      />
      <label :for="code"> {{ code }}</label>
    </BaseTooltip>
  </div>
</template>

<script>
import { useUserSettingsLanguageViewModel } from "./useUserSettingsLanguageViewModel";

export default {
  setup() {
    return useUserSettingsLanguageViewModel();
  },
};
</script>

<style scoped lang="scss">
.language-switch {
  display: flex;
  gap: $base-space * 2;
  padding: $base-space * 2 0;
}
input {
  display: none;
}
label {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  align-items: center;
  min-width: 40px;
  padding: $base-space * 2;
  background: var(--bg-opacity-4);
  border-radius: 6px;
  border: 1px solid var(--bg-opacity-4);
  color: var(--fg-secondary);
  text-transform: uppercase;
  &:hover {
    transition: color 0.3s ease;
    color: var(--fg-primary);
    cursor: pointer;
  }
}
input:checked + label {
  border-color: var(--fg-cuaternary);
  color: var(--fg-primary);
}
</style>
