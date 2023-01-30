<template>
  <div class="help-info__content" v-if="helpContents">
    <ul class="help-info__tabs">
      <li
        v-for="{ id, name, component } in helpContents"
        :key="id"
        class="help-info__tab"
        :class="isActiveTab(component)"
      >
        <base-button
          class="help-info__button"
          @click="getSelectedHelpComponent(id)"
        >
          {{ name }}
        </base-button>
      </li>
    </ul>
    <transition name="fade" mode="out-in" appear>
      <component
        :is="visibleComponent"
        :key="selectedComponent"
        class="help-info__component"
      />
    </transition>
    <ul class="help-info__bullets" v-if="helpContents.length > 1">
      <li
        v-for="{ id, component } in helpContents"
        :key="id"
        class="help-info__bullet"
        :class="isActiveTab(component)"
        @click="getSelectedHelpComponent(id)"
      ></li>
    </ul>
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
    margin: 0 -2.5em 2em -2.5em;
    padding: 0 2.5em;
    border-bottom: 1px solid $black-10;
    display: flex;
    list-style: none;
    overflow-y: auto;
    @extend %hide-scrollbar;
    &:before,
    &:after {
      position: absolute;
      content: "";
      height: 40px;
      width: 30px;
      z-index: 1;
    }
    &:before {
      left: 0;
      background: linear-gradient(to right, palette(white), transparent 100%);
    }
    &:after {
      right: 0;
      background: linear-gradient(to left, palette(white), transparent 100%);
    }
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
  &__component {
    height: calc(100vh - 400px);
    max-height: 500px;
    overflow-y: auto;
    @extend %hide-scrollbar;
  }
}
</style>
