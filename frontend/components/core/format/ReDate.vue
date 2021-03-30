

<template>
  <span>{{ date | moment('timezone', 'Europe/Madrid', 'LLLL ss') | moment('from', 'now') }}</span>
</template>

<script>
export default {
  props: ["date"],
  // computed: {
  //   timeZoneDate() {
  //     this.data | moment('timezone', 'Europe/Madrid', 'LLLL ss')
  //   }
  // },
  data: () => ({}),
};
</script>
