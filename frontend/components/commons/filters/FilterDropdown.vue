<template>
  <div
    ref="dropdownMenu"
    v-click-outside="onClickOutside"
    class="dropdown"
    :class="visible ? 'dropdown--open' : ''"
  >
    <div class="dropdown__header" @click="onClick">
      <slot name="dropdown-header" />
      <span
        :class="visible ? 'dropdown__check--open' : ''"
        class="dropdown__check"
        aria-hidden="true"
      />
    </div>
    <div v-show="visible" class="dropdown__content">
      <slot name="dropdown-content" />
    </div>
  </div>
</template>
<script>
import ClickOutside from "v-click-outside";
export default {
  directives: {
    clickOutside: ClickOutside.directive,
  },
  props: {
    visible: {
      default: false,
      type: Boolean,
    },
  },
  methods: {
    onClickOutside() {
      this.$emit("visibility", false);
    },
    onClick() {
      this.$emit("visibility", !this.visible);
    },
  },
};
</script>

<style lang="scss" scoped>
.dropdown {
  position: relative;
  &__header {
    height: 100%;
    width: auto;
    height: 45px;
    border: 2px solid $line-smooth-color;
    display: flex;
    align-items: center;
    padding: 0 1em;
    transition: all 0.2s ease;
    border-radius: 3px;
    &:after {
      content: "";
      border-color: $darker-color;
      border-style: solid;
      border-width: 1px 1px 0 0;
      display: inline-block;
      height: 8px;
      width: 8px;
      -webkit-transform: rotate(133deg);
      transform: rotate(133deg);
      -webkit-transition: all 1.5s ease;
      transition: all 1.5s ease;
      margin-bottom: 2px;
      margin-left: auto;
      margin-right: 0;
    }
    &:hover,
    &:focus {
      border-color: $primary-color;
      background: $lighter-color;
      transition: all 0.3s ease;
      &:after {
        border-color: $primary-color;
      }
    }
    // dropdown selected text
    > span {
      display: inline-block;
      max-width: 90%;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    p {
      display: inline-block;
      margin: 0;
      &:after {
        content: ",";
        position: relative;
        margin-right: 5px;
      }
      &:last-child {
        &:after {
          content: none;
        }
      }
    }
  }
  &__check {
    display: none;
  }
  &__content {
    position: absolute;
    top: 4em;
    left: 0;
    margin-top: 0;
    background: $lighter-color;
    border: 2px solid $primary-color;
    padding: 0 1em 0 1em;
    z-index: 3;
    transform: translate(0);
    right: auto;
    .filter-options {
      border: none;
      outline: none;
      height: 40px;
    }
    ul {
      max-height: 240px;
      overflow-y: auto;
      margin: 0 -1em 0 -1em;
      padding: 0 1em;
    }
    li {
      padding: 0.4em 0;
      list-style: none;
    }
  }
  &--open {
    pointer-events: all;
    .dropdown__content {
      min-width: 220px;
    }
  }
  input {
    left: 0;
    height: 40px;
    width: 100%;
    outline: none;
    z-index: 1;
    border: 0;
  }
  .clean-search {
    z-index: 1;
    display: block;
    position: absolute;
    right: 1em;
    top: 1em;
    cursor: pointer;
  }
}
.dropdown--filter {
  &.highlighted {
    .dropdown__header {
      border: 1px solid $primary-color;
    }
  }
  &.dropdown--open {
    .placeholder {
      display: block;
    }
    .dropdown__header {
      border: 2px solid $primary-color;
      background: $lighter-color;
      &:after {
        visibility: hidden;
      }
      .tag-icon {
        display: none;
      }
    }
  }
  .re-checkbox {
    margin: 0;
    width: 100% !important;
    cursor: default;
  }
}
.dropdown--sortable {
  &.dropdown--open {
    .dropdown {
      &__header {
        &:hover,
        &:focus {
          border: 2px solid $primary-color;
          background: $lighter-color;
        }
      }
    }
  }
  .dropdown {
    &__header {
      min-width: 140px;
    }
    &__selectables {
      display: inline-block !important;
    }
  }
}
</style>
