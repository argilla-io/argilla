<template>
  <div class="theme-switch">
    <div
      class="theme-switch__item"
      v-for="(theme, index) in themes"
      :key="index"
    >
      <input
        type="radio"
        :id="theme"
        :value="theme"
        v-model="colorSchema"
        @input="$colorSchema(theme)"
      />
      <label :for="theme">{{ theme }}</label>
    </div>
  </div>
</template>

<script>
export default {
  name: "ThemeSwitch",
  data() {
    return {
      themes: ["system", "dark", "light"],
      colorSchema: localStorage.getItem("theme") || "system",
    };
  },
};
</script>

<style scoped lang="scss">
.theme-switch {
  display: flex;
  gap: $base-space * 2;
  padding: $base-space * 2 0;
}
input {
  display: none;
}
label {
  padding: 16px;
  background: var(--bg-opacity-4);
  border-radius: 6px;
  border: 1px solid var(--bg-opacity-4);
}
input:checked + label {
  border-color: var(--fg-cuaternary);
}
</style>