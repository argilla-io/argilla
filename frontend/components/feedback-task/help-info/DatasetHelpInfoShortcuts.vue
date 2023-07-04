<template>
  <div class="docs-shortcuts">
    <base-spinner v-if="$fetchState.pending" />
    <div v-else-if="!$fetchState.error" class="docs-shortcuts__container">
      <transition v-if="shortcuts.html" name="fade" mode="out-in" appear>
        <BaseRenderHtml v-if="shortcuts" :html="shortcuts.html" />
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      shortcuts: null,
    };
  },
  async fetch() {
    this.shortcuts = this.getShortcutsMd();
  },
  methods: {
    getShortcutsMd() {
      let shortcutsMd = null;
      try {
        console.log();
        shortcutsMd = require(`../../../../docs/_source/_common/shortcuts.md`);
      } catch (e) {
        console.log(e);
      }
      return shortcutsMd;
    },
  },
};
</script>

<style lang="scss" scoped>
.docs-shortcuts {
  min-width: 450px;
  &__container {
    padding: 5px;
  }
}
:deep(table) {
  width: 100%;
  border-collapse: collapse;
  border-radius: $border-radius;
  border-spacing: 0;
  box-shadow: 0 0.2rem 0.5rem rgba(0, 0, 0, 0.05),
    0 0 0.0625rem rgba(0, 0, 0, 0.1);
  td,
  th {
    border-bottom: 1px solid $black-4;
    border-left: 1px solid $black-4;
    border-right: 1px solid $black-4;
    padding: 0 0.25rem;
    height: $base-space * 5;
  }
  th {
    background: $black-4;
    border: none;
  }
  thead tr:last-child th:last-child {
    border-top-right-radius: $border-radius;
  }
  thead tr:first-child th:first-child {
    border-top-left-radius: $border-radius;
  }
  td:last-child,
  th:last-child {
    border-left: none;
    border-right: none;
  }
  td:first-child,
  th:first-child {
    border-left: none;
  }
  code {
    padding: calc($base-space / 2);
    color: palette(crayola);
    border: 1px solid $black-10;
    border-radius: $border-radius;
    background: $black-4;
  }
}
</style>
