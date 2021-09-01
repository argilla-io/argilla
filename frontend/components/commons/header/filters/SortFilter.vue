<template>
  <div class="sort">
    <FilterDropdown
      :class="{ highlighted: visible }"
      :visible="visible"
      @visibility="onVisibility"
    >
      <span slot="dropdown-header">
        <span v-if="selectedField">{{ selectedField.name }}</span>
        <span v-else>Sort by</span>
      </span>
      <div slot="dropdown-content">
        <ul>
          <span v-for="option in sortOptions" :key="option.text">
            <ul @click="addField(option)">
              <li>
                {{ option.name }}
              </li>
            </ul>
          </span>
        </ul>
      </div>
    </FilterDropdown>
    <p
      v-if="selectedField"
      title="sort direction"
      class="sort__direction"
      @click="selectSortDirection()"
    >
      {{ defaultSortedByDir === "asc" ? "↑" : "↓" }}
    </p>
    <svgicon
      v-if="selectedField"
      title="remove field"
      class="sort__remove-button"
      name="cross"
      width="14"
      height="14"
      @click="removeField()"
    />
  </div>
</template>

<script>
import "assets/icons/cross";
export default {
  props: {
    sortOptions: {
      type: Array,
      required: true,
    },
    selectedField: {
      type: Object,
      default: undefined,
    },
  },
  data: () => ({
    visible: false,
    defaultSortedBy: undefined,
    defaultSortedByDir: "asc",
  }),
  mounted() {
    this.getSortDirection();
  },
  updated() {
    this.getSortDirection();
  },
  methods: {
    onVisibility(value) {
      this.visible = value;
    },
    getSortDirection() {
      if (this.selectedField) {
        this.defaultSortedByDir = this.selectedField.order;
      }
    },
    selectSortDirection() {
      this.defaultSortedByDir === "asc"
        ? (this.defaultSortedByDir = "desc")
        : (this.defaultSortedByDir = "asc");
      this.$emit("addSortField", this.selectedField, this.defaultSortedByDir);
    },
    removeField() {
      this.$emit("removeSortField");
    },
    addField(currentSort) {
      this.visible = false;
      this.defaultSortedBy = currentSort;
      this.$emit("addSortField", currentSort, this.defaultSortedByDir);
    },
  },
};
</script>

<style lang="scss" scoped>
.sort {
  display: flex;
  align-items: center;
  &__remove-button {
    margin-left: 1em;
    cursor: pointer;
  }
  &__direction {
    padding: 0.5em;
    @include font-size(20px);
    margin: 0 0 0 0.5em;
    background: palette(grey, light);
    border-radius: 5px;
    min-width: 50px;
    text-align: center;
    cursor: pointer;
  }
  .dropdown {
    width: 100%;
    max-width: 280px;
  }
}
</style>
