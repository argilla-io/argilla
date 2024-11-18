<template>
  <div class="language-switch">
    <div
      class="language-switch__item"
      v-for="(language, index) in languages"
      :key="index"
    >
      <input
        type="radio"
        :id="language"
        :value="language"
        v-model="$i18n.locale"
        @input="setLocale(language)"
      />
      <label :for="language"> {{ language }}</label>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      languages: this.$i18n.locales.map((l) => l.code).sort(),
    };
  },
  methods: {
    setLocale(locale) {
      this.$i18n.setLocale(locale);
    },
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
  }
}
input:checked + label {
  border-color: var(--fg-cuaternary);
  color: var(--fg-primary);
}
</style>
