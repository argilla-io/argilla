

<template>
  <span>{{ date | moment('utc') | moment('subtract', `${this.timeDifference} minutes`) | moment('from', 'now') }}</span>
</template>

<script>
export default {
  props: ["date"],
  computed: {
    timeDifference() {
      return new Date().getTimezoneOffset();
    }
  },
};
</script>
