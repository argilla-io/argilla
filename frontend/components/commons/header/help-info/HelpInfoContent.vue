<template>
  <div class="help-info__content" v-if="helpContents">
    <ul class="help-info__tabs">
      <li
        class="help-info__tab"
        :class="isActiveTab(helpContent.component)"
        v-for="helpContent in helpContents"
        :key="helpContent.id"
      >
        <base-button
          class="help-info__button"
          @click="getSelectedHelpComponent(helpContent.id)"
        >
          {{ helpContent.name }}
        </base-button>
      </li>
    </ul>
    <transition name="fade" mode="out-in" appear>
      <component :is="visibleComponent" :key="selectedComponent" />
    </transition>
    <ul class="help-info__bullets">
      <li
        class="help-info__bullet"
        :class="isActiveTab(helpContent.component)"
        @click="getSelectedHelpComponent(helpContent.id)"
        v-for="helpContent in helpContents"
        :key="helpContent.id"
      ></li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedComponent: null,
      similarity: {
        id: "similarity",
        name: "Similarity Search",
        component: "helpInfoSimilarity",
      },
      explain: {
        id: "explain",
        name: "Colors in token attributions",
        component: "helpInfoExplain",
      },
    };
  },
  computed: {
    helpContents() {
      return [
        ...this.setHelpContent(this.similarity, true),
        ...this.setHelpContent(this.explain, true),
      ];
    },
    visibleComponent() {
      return this.selectedComponent || this.helpContents[0].component;
    },
  },
  methods: {
    getSelectedHelpComponent(id) {
      this.selectedComponent = this.helpContents.find(
        (help) => help.id === id
      )?.component;
    },
    setHelpContent(obj, condition) {
      return condition ? [obj] : [];
    },
    isActiveTab(name) {
      return this.visibleComponent === name ? "--active" : null;
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
  &__tabs {
    margin: 0 -2.5em;
    padding: 0 2.5em;
    border-bottom: 1px solid $black-10;
    display: flex;
    list-style: none;
    overflow-y: auto;
    @extend %hide-scrollbar;
  }
  &__tab {
    border-bottom: 2px solid transparent;
    transition: border-color 0.3s ease-in-out;
    &.--active {
      border-color: $primary-color;
      transition: border-color 0.3s ease-in-out;
    }
    &.--active,
    &:hover {
      #{$this}__button {
        color: $black-87;
        transition: color 0.2s ease-in-out;
      }
    }
  }
  &__button {
    color: $black-54;
    transition: color 0.2s ease-in-out;
    @include font-size(13px);
    padding: $base-space;
  }
  &__bullets {
    display: flex;
    gap: $base-space;
    justify-content: center;
    padding: 0;
    list-style: none;
  }
  &__bullet {
    height: $base-space;
    width: $base-space;
    background: $black-10;
    border-radius: 50%;
    cursor: pointer;
    &.--active {
      background: $black-54;
      cursor: default;
    }
  }
}
</style>
