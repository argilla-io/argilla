<template>
  <div :class="badges.length ? 'metadata-button--active' : 'metadata-button'">
    <BaseButton class="metadata-button__button" v-if="!badges.length"
      >Metadata</BaseButton
    >
    <svgicon v-else name="filter" width="16" height="16" />
    <div class="metadata-button__badges" v-if="badges.length">
      <FilterBadge
        class="metadata-button__badge"
        :active-badge="activeBadge === badge"
        v-for="badge in visibleBadges"
        :key="badge"
        :text="badge"
        @on-click="onClickOnBadge(badge, $event)"
        @on-clear="onClickOnClear(badge, $event)"
      ></FilterBadge>
      <div
        class="metadata-button__badges__collapsed"
        v-click-outside="onClickOutside"
      >
        <BaseBadge
          v-if="badges.length > maxVisibleBadges"
          :text="`+ ${badges.length - maxVisibleBadges}`"
          @on-click="toggleTooltip"
        />
        <FilterTooltip v-if="visibleTooltip">
          <FilterBadge
            class="badge"
            v-for="badge in collapsedbadges"
            :key="badge"
            :text="badge"
            @on-click="onClickOnBadge(badge, $event)"
            @on-clear="onClickOnClear(badge, $event)"
          ></FilterBadge>
        </FilterTooltip>
      </div>
    </div>
    <svgicon
      class="metadata-button__chevron"
      name="chevron-down"
      width="12"
      height="12"
    />
  </div>
</template>

<script>
import "assets/icons/chevron-down";
import "assets/icons/filter";
export default {
  props: {
    badges: {
      type: Array,
      default: [],
    },
    activeBadge: {
      type: String,
    },
    maxVisibleBadges: {
      default: 2,
    },
  },
  data() {
    return {
      visibleTooltip: false,
    };
  },
  computed: {
    visibleBadges() {
      return this.badges.slice(0, this.maxVisibleBadges);
    },
    collapsedbadges() {
      return this.badges.slice(this.maxVisibleBadges, this.badges.length);
    },
  },
  methods: {
    onClickOnBadge(badge, $event) {
      this.$emit("click-on-badge", badge, $event);
    },
    onClickOnClear(badge, $event) {
      this.$emit("click-on-clear", badge, $event);
    },
    toggleTooltip(e) {
      e.stopPropagation();
      this.visibleTooltip = this.visibleTooltip ? false : true;
    },
    onClickOutside() {
      this.visibleTooltip = false;
    },
  },
};
</script>

<styles lang="scss" scoped>
.metadata-button {
  display: flex;
  gap: $base-space;
  align-items: center;
  height: $base-space * 5;
  padding: $base-space $base-space * 2;
  border-radius: $border-radius;
  cursor: pointer;
  &:hover,
  &--active {
    background: $black-4;
    @extend .metadata-button;
  }
  &__badges {
    display: flex;
    gap: calc($base-space / 2);
    &__collapsed {
      position: relative;
    }
  }
  &__badge :deep(.badge__text) {
    max-width: 140px;
  }
  &__button.button {
    padding: 0;
  }
}
</styles>
