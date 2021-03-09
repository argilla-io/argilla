<template>
  <div class="filters__title">
    <h2 class="filters__title__info">
      <svgicon name="datasource" width="20" height="14" />
      <span class="filters__title__datasource">{{ dataset.name }}</span>
      <span class="filters__title__records"
        >({{ dataset.results.total }} Records)</span
      >
    </h2>
  </div>
</template>

<script>
import "assets/icons/datasource";
export default {
  props: {
    dataset: {
      default: () => { },
      type: Object,
    },
  },
};
</script>
<style lang="scss" scoped>
.filters {
  &__title {
    margin-right: auto;
    &__action {
      @include font-size(18px);
      font-weight: normal;
      font-family: $sff;
      color: $font-medium-color;
    }
    &__info {
      font-family: $ff !important;
      font-weight: 300;
      @include font-size(13px);
      color: $font-medium-color;
      white-space: nowrap;
      display: flex;
      margin: 0.83em 0;
      align-items: center;
      span {
        display: inline;
      }
    }
    &__datasource {
      @include font-size(13px);
      margin-right: 1em;
      margin-left: 0.5em;
      font-weight: 600;
      // max-width: 20vw;
      display: inline-block;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    &__model {
      @include font-size(13px);
      color: $font-dark-color;
      border: 1px solid $darker-color;
      border-radius: 3px;
      margin-right: 1em;
      margin-left: 1em;
      font-weight: 600;
      padding: 0.1em 0.3em;
      max-width: 17vw;
      overflow: hidden;
      display: inline-block;
      text-overflow: ellipsis;
    }
    &__records {
      @include font-size(14px);
      color: $secondary-color;
      font-weight: 600;
    }
    &__project {
      color: $primary-color;
      text-decoration: none;
      @include font-size(13px);
    }
  }
}
</style>
