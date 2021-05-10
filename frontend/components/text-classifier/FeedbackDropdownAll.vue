<template>
  <div>
    <FilterDropdown
      class="selector"
      :visible="visible"
      @visibility="onVisibility"
    >
      <template v-slot:dropdown-header>
        <span class="dropdown__text">Annotate as...</span>
      </template>
      <template v-slot:dropdown-content>
        <input type="text" v-model="searchText" autofocus placeholder="Search label...">
        <svgicon
          v-if="searchText != undefined"
          @click="cleanSearchText"
          class="clean-search"
          name="cross"
          width="10"
          height="10"
          color="#9b9b9b"
        ></svgicon>
        <ul v-if="multiLabel" class="selector__list">
          <li :title="option" class="selector__option" v-for="option in filterSearch(
              options,
              searchText
            )" :key="option">
            <ReCheckbox class="re-checkbox--dark" :id="option" :value="option" v-model="selectedOptions">
              {{ option }}
            </ReCheckbox>
          </li>
        </ul>
        <ul v-else class="selector__list">
          <li class="selector__option" @click="selected([option])" v-for="option in filterSearch(options, searchText)" :key="option.index">
            <span
            :data-title="option">
            {{option | truncate(30)}}
            </span>
          </li>
        </ul>
        <div v-if="!filterSearch(options, searchText).length" class="selector__new-label">
          <p v-if="!addnewLabelVisible" class="selector__new-label__button"
            @click="openAddLabel()"
          >
            + New Label
          </p>
          <div v-if="addnewLabelVisible" class="selector__new-label__input">
            <input
              ref="addLabelInput"
              v-model="newLabel"
              type="text"
              placeholder="New label"
              @keyup.enter="addNewLabel(newLabel)"
            />
            <svgicon name="cross" @click="addnewLabelVisible = false" />
          </div>
        </div>
        <div v-if="multiLabel && filterSearch(options, searchText).length" class="filter__buttons">
          <ReButton class="button-tertiary--small button-tertiary--outline" @click="onVisibility(false)">
            Cancel
          </ReButton>
          <ReButton class="button-primary--small" @click="selected(selectedOptions)">
            Apply
          </ReButton>
        </div>
      </template>
    </FilterDropdown>
  </div>
</template>
<script>

import 'assets/icons/ignore';

export default {
  props: {
    record: Object,
    options: Array,
    multiLabel: Boolean,
  },
  data: () => ({
    visible: false,
    searchText: undefined,
    showTooltipOnHover: false,
    selectedOptions: [],
    newLabel: undefined,
    addnewLabelVisible: false,
  }),
  filters: {
    truncate(string, value) {
      if (string.length > value) {
        return `${string.substring(0, value)}...`;
      }
      return string;
    },
  },
  methods: {
    openAddLabel() {
      let text = this.searchText;
      this.newLabel = text
      this.addnewLabelVisible = true;
      this.$nextTick(() => this.$refs.addLabelInput.focus());
    },
    addNewLabel(newLabel) {
      if (!this.options.some(option => option === newLabel)) {
        this.$emit('addNewLabel', newLabel)
      }
      this.addnewLabelVisible = false;
    },
    onVisibility(value) {
      this.visible = value;
      this.searchText = undefined;
      this.addnewLabelVisible = false;
    },
    selected(labels) {
      this.$emit('selected', labels);
      this.addnewLabelVisible = false;
      this.visible = false;
      this.selectedOptions = [];
    },
    
    cleanSearchText() {
      this.searchText = undefined;
      this.addnewLabelVisible = false;
    },
    filterSearch(options, text) {
      if (text === undefined) {
        return options;
      }
      return options.filter(item => item.toLowerCase().match(text.toLowerCase()));
    },
    showTooltip(data, e) {
      const { tooltip } = this.$refs;
      const el = e.currentTarget;
      if (e.currentTarget && data.length >= 30) {
        tooltip.innerHTML = data;
        this.showTooltipOnHover = true;
        const offset = el.getBoundingClientRect().top - el.offsetParent.getBoundingClientRect().top;
        tooltip.style.top = `${offset - 35}px`;
      } else {
        this.showTooltipOnHover = false;
      }
    },
  },
};
</script>
<style lang="scss" scoped>
// @import "@recognai/re-commons/src/assets/scss/components/tooltip.scss";
.selector {
  &__new-label {
    &__button {
      cursor: pointer;
    }
    &__input {
      display: flex;
      align-content: center;
      input {
        @include input-placeholder {
          color: $font-secondary;
        }
      }
      .svg-icon {
        margin: auto;
        cursor: pointer;
      }
    }
  }
  &__option {
    display: block;
    padding: 0.5em 0;
    text-align: left;
    font-weight: 400;
    .re-checkbox {
      margin: 0;
      display: flex;
      ::v-deep label {
        max-width: 140px;
        display: block;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
    }
    cursor: pointer;
    &:hover {
      color : $secondary-color;
    }
  }
  ::v-deep .dropdown__content {
    transform: translate 0;
  }
}
</style>
