<template>
  <div class="card-with-tabs">
    <ul class="card-with-tabs__tabs">
      <li
        class="card-with-tabs__tab"
        :class="{ '--active': tab.id === currentTab.id }"
        v-for="tab in tabs"
        :key="tab.id"
      >
        <base-button class="small" @on-click="changeTab(tab)">{{
          tab.name
        }}</base-button>
      </li>
    </ul>
    <div class="card-with-tabs__content">
      <slot :current-component="currentComponent" />
    </div>
  </div>
</template>

<script>
export default {
  name: "BaseCardWithTabs",
  props: {
    tabs: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      currentTab: this.tabs[0],
    };
  },
  computed: {
    currentComponent() {
      return this.currentTab.component;
    },
  },
  methods: {
    changeTab(tab) {
      this.currentTab = tab;
    },
  },
};
</script>

<style lang="scss" scoped>
.card-with-tabs {
  &__tabs {
    display: flex;
    align-items: center;
    margin: 0 0 -1px 0;
    padding: 0;
  }
  &__tab {
    list-style: none;
    border-top-right-radius: $border-radius;
    border-top-left-radius: $border-radius;
    background: palette(grey, 800);
    border-top: 1px solid palette(grey, 600);
    border-left: 1px solid palette(grey, 600);
    border-right: 1px solid palette(grey, 600);
    &:not(.--active) {
      background: palette(grey, 600);
    }
    &:last-child:not(:first-child) {
      margin-left: -1px;
    }
  }
  &__content {
    padding: $base-space * 2;
    border-top-right-radius: $border-radius;
    border-bottom-left-radius: $border-radius;
    border-bottom-right-radius: $border-radius;
    background: palette(grey, 800);
    border: 1px solid palette(grey, 600);
  }
}
</style>
