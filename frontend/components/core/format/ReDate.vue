<template>
  <span>{{ date | moment("from", "now") }}</span>
</template>

<script>
export default {
  props: ["date"],
  data: () => ({}),
};
</script>
