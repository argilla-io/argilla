<script>
export default {
  props: {
    html: {
      type: String,
      required: true,
    },
  },
  render(h) {
    return h({
      template: `<div>${this.html}</div>`,
    });
  },
};
</script>
