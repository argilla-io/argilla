/*
 * coding=utf-8
 * Copyright 2021-present, the Recognai S.L. team.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import Vue from "vue";

const styles = {
  container: {
    overflowY: "scroll",
  },
};

export default {
  name: "auto-virtual-scroll-list",
  props: {
    totalHeight: { type: Number, required: true },
    defaultHeight: { type: Number, required: true },
    extraItems: { type: Number, default: 1 },
  },
  data() {
    return {
      offset: 0, // items offset
      heights: [],
      scrollTop: 0,
      numberOfItems: false,
    };
  },
  methods: {
    /** Reset component (variables and scroll) */
    reset() {
      this.offset = 0;
      this.heights = [];
      this.scrollTop = 0;
      this.numberOfItems = false;
      this.$refs.container.scrollTop = 0; // reset scroll
    },
    calculateSpaceBefore() {
      const { scrollTop, heights, defaultHeight } = this;
      let firstItemIndex = 0;
      let spaceBefore = 0;
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const itemHeight = heights[firstItemIndex] || defaultHeight;
        if (spaceBefore + itemHeight > scrollTop) break;
        firstItemIndex += 1;
        spaceBefore += itemHeight;
      }

      this.offset = firstItemIndex; // save to use in tests
      return { spaceBefore, firstItemIndex };
    },
    calculateItems(firstItemIndex, paddingTop) {
      const {
        $slots: { default: defaultItems = [] },
        heights,
        defaultHeight,
        totalHeight,
        extraItems,
        scrollTop,
      } = this;
      const items = [];
      let heightAcc = paddingTop;
      let lastItemIndex = firstItemIndex;
      for (
        ;
        heightAcc - scrollTop < totalHeight &&
        lastItemIndex < defaultItems.length;
        lastItemIndex += 1
      ) {
        items.push(defaultItems[lastItemIndex]);
        heightAcc += heights[lastItemIndex] || defaultHeight;
      }
      // add extra items (from prop)
      for (let i = 0; i < extraItems; i += 1) {
        const item = defaultItems[lastItemIndex];
        if (item === undefined) break;
        items.push(item);
        lastItemIndex += 1;
        heightAcc += heights[lastItemIndex] || defaultHeight;
      }

      return { lastItemIndex, items };
    },
    calculateSpaceAfter(lastItemIndex) {
      const {
        $slots: { default: defaultItems = [] },
        heights,
        defaultHeight,
      } = this;

      return defaultItems
        .slice(lastItemIndex)
        .map((x, i) => heights[i + lastItemIndex] || defaultHeight)
        .reduce((a, b) => a + b, 0);
    },
    readItemsHeight() {
      const {
        $slots: { default: defaultItems = [] },
        numberOfItems,
      } = this;
      // if number of items is unknown set it
      if (!numberOfItems) this.numberOfItems = defaultItems.length;
      // else if number of items changed reset the component
      // else if (numberOfItems !== defaultItems.length) this.reset()

      // nextTick -> need to wait for the offset to be reloaded if scroll
      // changed (which happens at render)
      Vue.nextTick(() => {
        const {
          $el: { children: htmlChildren },
          offset,
        } = this;
        const htmlAsArray = Array.from(htmlChildren);
        const children = htmlAsArray.slice(1, htmlAsArray.length - 1); // remove empty divs
        const newHeights = this.heights.slice(0); // recomputing heights
        // scrollDiff is used for backward scrolling (where not all items before have known height)
        // let scrollDiff = 0;
        let hasChange = false;

        children.forEach((child, i) => {
          const index = i + offset;
          // if item has been set or updated
          if (newHeights[index] !== child.offsetHeight) {
            // if item is in the space before items, update the scroll
            // if (index <= offset) {
            //   scrollDiff +=
            //     child.offsetHeight - (newHeights[index] || defaultHeight);
            // }
            newHeights[index] = child.offsetHeight;
            hasChange = true;
          }
        });

        // trigger re-render
        if (hasChange) {
          // prevent jump
          // if (this.heights[offset + 1]) this.$refs.container.scrollTop += scrollDiff
          this.heights = newHeights;
        }
      });
    },

    setIndex(index, recursion = true) {
      const {
        $slots: { default: defaultItems = [] },
        defaultHeight,
        heights,
      } = this;
      const parsedIndex =
        index >= defaultItems.length ? defaultItems.length - 1 : index;
      let scrollTop = 1;
      for (let i = 0; i < parsedIndex; i += 1)
        scrollTop += heights[i] || defaultHeight;
      this.$refs.container.scrollTop = scrollTop;
      this.scrollTop = scrollTop;
      if (recursion) setTimeout(() => this.setIndex(index, false), 50);
    },
  },
  /** Sets callback to update the scrollTop variable */
  mounted() {
    this.$refs.container.onscroll = () => {
      const { scrollTop } = this;
      // listen for change only to avoid loop
      const newScroll = this.$refs.container.scrollTop || 0;
      if (newScroll !== scrollTop) this.scrollTop = newScroll;
    };
    this.readItemsHeight();
    this.$emit("updated");
  },
  /** Listen to change in slot items as well as to rendered children height */
  updated() {
    this.readItemsHeight();
    this.$emit("updated");
  },
  render() {
    // eslint-disable-line no-unused-vars
    const { spaceBefore, firstItemIndex } = this.calculateSpaceBefore();
    const { items, lastItemIndex } = this.calculateItems(
      firstItemIndex,
      spaceBefore
    );
    const spaceAfter = this.calculateSpaceAfter(lastItemIndex);

    const { totalHeight } = this;
    return (
      <div
        ref="container"
        style={[styles.container, { height: `${totalHeight}px` }]}
      >
        <div style={{ width: "100%", height: `${spaceBefore}px` }} />
        {items}
        <div style={{ width: "100%", height: `${spaceAfter}px` }} />
      </div>
    );
  },
};
