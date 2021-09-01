<template>
  <form @submit.prevent="submit(query)">
    <div
      v-click-outside="collapse"
      :class="['searchbar__container', { active: query.length }]"
    >
      <ReInputContainer class="searchbar">
        <ReInput
          ref="input"
          v-model="query"
          class="searchbar__input"
          placeholder="Search records"
          @focus="activeDropdown()"
        />
        <svgicon v-if="!query.length" name="search" width="20" height="40" />
        <svgicon
          v-else
          class="searchbar__button"
          name="cross"
          width="14"
          height="14"
          @click="query = ''"
        />
      </ReInputContainer>
      <div
        v-if="
          allowSearchByField &&
          areVariousFields &&
          query.length &&
          visibleDropdown
        "
        class="searchbar__dropdown"
      >
        <ul v-for="group in structureGroupFields" :key="group.index">
          <span v-if="group.title" class="searchbar__dropdown__title">{{
            group.title
          }}</span>
          <li
            v-for="field in group.fields"
            :key="field.index"
            class="searchbar__dropdown__item"
          >
            <a href="#" @click="submit(query, [field.id])"
              ><strong>"{{ query }}"</strong> in
              <span>{{ field.name }}</span></a
            >
          </li>
        </ul>
        <a href="#" class="searchbar__dropdown__item" @click="submit(query)"
          ><strong>"{{ query }}"</strong> in all fields</a
        >
      </div>
    </div>
  </form>
</template>

<script>
import ClickOutside from "v-click-outside";
import "assets/icons/cross";
import "assets/icons/search";

export default {
  directives: {
    clickOutside: ClickOutside.directive,
  },
  props: {
    allowSearchByField: {
      type: Boolean,
      default: true,
    },
    searchFilter: {
      type: Object,
      default: () => ({ query: "" }),
    },
  },
  data: () => ({
    visibleDropdown: false,
    queryFields: [],
    queryText: null,
  }),
  computed: {
    query: {
      get() {
        return this.queryText === null
          ? this.searchFilter.query
          : this.queryText;
      },
      set(val) {
        this.queryText = val;
      },
    },
    areVariousFields() {
      if (this.queryFields && this.queryFields.length > 1) {
        return true;
      }
      return false;
    },
    structureGroupFields() {
      if (this.areVariousFields) {
        let titles = [];
        if (this.queryFields.length) {
          this.queryFields.forEach((f) => {
            if (f.includes(".")) {
              titles.push(f.substring(0, f.indexOf(".")));
            }
          });
          titles = titles.filter(
            (title, index) => titles.indexOf(title) === index
          );
        }
        if (titles.length > 1) {
          const groupFields = titles.map((title) => {
            const filteredFieldsByTitle = [];
            this.queryFields.forEach((f) => {
              if (f.includes(title)) {
                filteredFieldsByTitle.push(f);
              }
            });
            filteredFieldsByTitle.forEach((field, index) => {
              filteredFieldsByTitle[index] = {
                id: field,
                name: field.replace(`${title}.`, ""),
              };
            });
            return {
              title,
              fields: filteredFieldsByTitle,
            };
          });
          return groupFields;
        }
        const queryFieldsObject = [...this.queryFields];
        queryFieldsObject.forEach((field, index) => {
          queryFieldsObject[index] = {
            fields: [
              {
                id: field,
                name: field,
              },
            ],
          };
        });
        return queryFieldsObject;
      }
      return false;
    },
  },
  methods: {
    activeDropdown() {
      this.visibleDropdown = true;
    },
    collapse() {
      if (this.visibleDropdown === true) {
        this.visibleDropdown = false;
      }
    },
    submit(query, fields) {
      this.$refs.input.$el.blur();
      this.visibleDropdown = false;
      this.$emit("submit", query, fields);
    },
  },
};
</script>

<style lang="scss" scoped>
.searchbar {
  background: $lighter-color;
  width: 285px;
  min-height: 43px;
  border: none;
  padding: 0 1em;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  margin-right: 0;
  margin-left: auto;
  pointer-events: all;
  border-radius: 5px;
  .fixed-header & {
    height: 40px;
  }
  &__container {
    position: relative;
    max-width: 280px;
    margin-right: auto;
    margin-left: 0;
  }
  &__dropdown {
    position: absolute;
    pointer-events: all;
    top: 4em;
    left: 0;
    right: 0;
    margin-top: 0;
    background: $lighter-color;
    border: 2px solid $primary-color;
    padding: 0 1em 0 1em;
    z-index: 3;
    max-height: 224px;
    overflow-y: auto;
    ul {
      padding: 0;
      list-style: none;
      li {
        border-bottom: 1px solid $font-medium-color;
      }
    }
    &__title {
      color: $font-medium-color;
      text-transform: uppercase;
      margin-bottom: 1em;
      margin-top: 1em;
      font-weight: 600;
      display: block;
    }
    &__item {
      padding: 1em 0;
      display: block;
      strong {
        margin-right: 1em;
      }
      span {
        text-transform: uppercase;
        font-weight: lighter;
      }
    }
    a {
      text-decoration: none;
      outline: none;
      &:hover {
        color: $secondary-color;
      }
    }
  }
  // &.re-input-focused {
  //   border: 2px solid $secondary-color;
  //   .svg-icon {
  //     fill: $secondary-color;
  //   }
  // }
  .svg-icon {
    fill: $primary-color;
    margin: auto;
    order: 2;
  }
  &__button {
    cursor: pointer;
    &--expand {
      display: none;
      .fixed-header & {
        cursor: pointer;
        display: block;
      }
    }
  }
}
</style>
