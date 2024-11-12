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
        v-model="currentTheme"
        @input="$colorSchema.setTheme(theme)"
      />
      <label :for="theme">
        <svgicon width="20" height="20" :name="`${theme}-theme`" />
        {{ theme }}</label
      >
    </div>
  </div>
</template>

<script>
import "assets/icons/light-theme";
import "assets/icons/dark-theme";
import "assets/icons/system-theme";
import "assets/icons/high-contrast-theme";
export default {
  name: "ThemeSwitch",
  data() {
    return {
      themes: ["system", "dark", "light", "high-contrast"],
      currentTheme: this.$colorSchema.currentTheme,
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
  display: flex;
  flex-direction: column;
  gap: $base-space;
  align-items: center;
  min-width: 124px;
  padding: $base-space * 2;
  background: var(--bg-opacity-4);
  border-radius: 6px;
  border: 1px solid var(--bg-opacity-4);
  color: var(--fg-secondary);
  .svg-icon {
    fill: var(--fg-secondary);
  }
  &:hover {
    transition: color 0.3s ease;
    color: var(--fg-primary);
    .svg-icon {
      transition: fill 0.3s ease;
      fill: var(--fg-primary);
    }
  }
}
input:checked + label {
  border-color: var(--fg-cuaternary);
  color: var(--fg-primary);
  .svg-icon {
    fill: var(--fg-primary);
  }
}
</style>
