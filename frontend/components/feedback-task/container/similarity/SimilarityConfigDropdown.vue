<template>
  <BaseDropdown
    class="similarity-config"
    :visible="dropdownIsVisible"
    @visibility="onVisibility"
    v-if="filteredOptions.length"
  >
    <template slot="dropdown-header">
      {{ value }}<svgicon name="chevron-down" height="8" />
    </template>
    <template slot="dropdown-content">
      <ul class="similarity-config__options">
        <li
          class="similarity-config__option"
          v-for="option in filteredOptions"
          :key="option"
          @click="selectOption(option)"
        >
          {{ option }}
        </li>
      </ul>
    </template>
  </BaseDropdown>
</template>

<script>
export default {
  props: {
    value: {
      type: String,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      dropdownIsVisible: false,
    };
  },
  computed: {
    filteredOptions() {
      return this.options.filter((o) => o !== this.value);
    },
  },
  methods: {
    onVisibility(value) {
      this.dropdownIsVisible = value;
    },
    selectOption(option) {
      this.value = option;
      this.dropdownIsVisible = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.similarity-config {
  &__options {
    list-style: none;
    padding: calc($base-space / 2);
    margin: 0;
  }
  &__option {
    padding: calc($base-space / 2);
    border-radius: $border-radius;
    transition: all 0.2s ease-in;
    cursor: pointer;
    &:hover {
      background: $black-4;
      transition: all 0.2s ease-out;
    }
  }
  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
