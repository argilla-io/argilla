// ~/plugins/multiTabState.client.js
import createMultiTabState from 'vuex-multi-tab-state';

export default ({ store }) => {
  createMultiTabState()(store);
};