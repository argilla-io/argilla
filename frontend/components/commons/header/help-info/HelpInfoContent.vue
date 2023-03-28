<template>
  <div class="help-info__content" v-if="helpContents">
    <base-tabs
      class="help-info__tabs"
      :tabs="helpContents"
      :active-tab="visibleTab"
      @change-tab="getSelectedHelpComponent"
    />
    <transition name="fade" mode="out-in" appear>
      <component
        :is="visibleComponent"
        :key="visibleComponent"
        class="help-info__component"
      />
    </transition>
  </div>
</template>

<script>
export default {
  props: {
    helpContents: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      selectedComponent: null,
    };
  },
  computed: {
    visibleTab() {
      return this.selectedComponent || this.helpContents[0];
    },
    visibleComponent() {
      return this.visibleTab.component;
    },
  },
  methods: {
    getSelectedHelpComponent(id) {
      this.selectedComponent = this.helpContents.find((help) => help.id === id);
    },
  },
};
</script>

<style lang="scss" scoped>
.help-info {
  $this: &;
  &__content {
    margin-bottom: 2em;
    @include font-size(13px);
    a {
      color: $primary-color;
      text-decoration: none;
      &:hover {
        color: darken($primary-color, 20%);
      }
    }
  }
  &__component {
    height: calc(100vh - 400px);
    max-height: 500px;
    overflow-y: auto;
    @extend %hide-scrollbar;
  }
  &__tabs {
    margin: 0 -2.5em 2em -2.5em;
    padding: 0 2.5em;
  }
}
</style>
