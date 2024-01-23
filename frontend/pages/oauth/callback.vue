<script>
export default {
  mounted() {
    const { query } = this.$route;
    if (query.code) {
    }

    this.$router.push("/datasets");
  },
};
</script>
