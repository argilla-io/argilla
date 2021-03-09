<template>
  <ul class="breadcrumbs">
    <li>
      <NuxtLink
        v-for="breadcrumb in breadcrumbs"
        :key="breadcrumb.name"
        class="breadcrumbs__item"
        :to="breadcrumb.link"
      >
        {{ breadcrumb.name }}
      </NuxtLink>
    </li>
  </ul>
</template>

<script>
export default {
  props: {
    breadcrumbs: {
      type: Array,
    },
  },
};
</script>

<style lang="scss" scoped>
.breadcrumbs {
  margin-right: auto;
  margin-left: 1em;
  display: inline-block;
  list-style: none;
  padding-left: 0;
  &__item {
    margin: auto 0.5em auto auto;
    color: $primary-color;
    text-decoration: none;
    outline: none;
    &:not(:last-child):after {
      content: "/";
      margin-left: 0.5em;
    }
    &:hover,
    &:focus {
      transition: $swift-ease-in-out;
      color: $primary-darken-color;
    }
    &:last-child {
      font-weight: bold;
    }
  }
}
</style>
