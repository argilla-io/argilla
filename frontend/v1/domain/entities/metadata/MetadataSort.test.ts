import { createMetadataMock } from "../__mocks__/metadata/mock";
import { MetadataSortList } from "./MetadataSort";

describe("MetadataSort ", () => {
  describe("Select", () => {
    test("should be able to select a category", () => {
      const metadataSort = new MetadataSortList(createMetadataMock());

      metadataSort.select("split");

      expect(
        metadataSort.selected.map((m) => m.name).includes("split")
      ).toBeTruthy();
      expect(
        metadataSort.noSelected.map((m) => m.name).includes("split")
      ).toBeFalsy();
    });
  });

  describe("Unselect", () => {
    test("should be able to unselect a category", () => {
      const metadataSort = new MetadataSortList(createMetadataMock());
      metadataSort.select("split");

      metadataSort.unselect("split");

      expect(metadataSort.selected).toHaveLength(0);
      expect(
        metadataSort.noSelected.map((m) => m.name).includes("split")
      ).toBeTruthy();
    });
  });

  describe("Replace", () => {
    test("should be able to replace a category", () => {
      const metadataSort = new MetadataSortList(createMetadataMock());
      metadataSort.select("loss");
      expect(metadataSort.selected[0].name).toEqual("loss");

      metadataSort.replace("loss", "split");

      expect(
        metadataSort.noSelected.map((m) => m.name).includes("loss")
      ).toBeTruthy();
      expect(
        metadataSort.selected.map((m) => m.name).includes("split")
      ).toBeTruthy();
    });
  });

  describe("Clear", () => {
    test("should be able to clear all selected categories", () => {
      const metadataSort = new MetadataSortList(createMetadataMock());
      metadataSort.select("loss");
      expect(
        metadataSort.selected.map((m) => m.name).includes("loss")
      ).toBeTruthy();
      expect(
        metadataSort.noSelected.map((m) => m.name).includes("loss")
      ).toBeFalsy();

      metadataSort.clear();

      expect(metadataSort.selected).toHaveLength(0);
      expect(
        metadataSort.noSelected.map((m) => m.name).includes("loss")
      ).toBeTruthy();
    });
  });

  describe("toggleSort", () => {
    test("should be able to toggle sort", () => {
      const metadataSort = new MetadataSortList(createMetadataMock());
      metadataSort.select("loss");
      expect(metadataSort.selected[0].sort).toEqual("asc");

      metadataSort.toggleSort("loss");

      expect(metadataSort.selected[0].sort).toEqual("desc");
    });
  });

  describe("Convert to Router Params", () => {
    test("should be able to convert to router params", () => {
      const metadataSort = new MetadataSortList(createMetadataMock());
      metadataSort.select("loss");
      metadataSort.select("split");
      metadataSort.toggleSort("loss");

      const param = metadataSort.convertToRouteParam();

      expect(param).toEqual(["metadata.loss:desc", "metadata.split:asc"]);
    });

    test("should be able to convert to router params for record sort", () => {
      const metadataSort = new MetadataSortList(createMetadataMock());
      metadataSort.select("loss");
      metadataSort.select("inserted_at");
      metadataSort.toggleSort("loss");

      const param = metadataSort.convertToRouteParam();

      expect(param).toEqual(["metadata.loss:desc", "inserted_at:asc"]);
    });
  });

  describe("Complete by Route Params", () => {
    test("should be able to complete by route params", () => {
      const metadataSort = new MetadataSortList(createMetadataMock());
      metadataSort.completeByRouteParams(
        "metadata.loss:desc,metadata.split:asc"
      );

      expect(metadataSort.selected[0].name).toEqual("loss");
      expect(metadataSort.selected[0].sort).toEqual("desc");
      expect(metadataSort.selected[1].name).toEqual("split");
      expect(metadataSort.selected[1].sort).toEqual("asc");
    });

    test("should be able to complete record sort", () => {
      const metadataSort = new MetadataSortList(createMetadataMock());
      metadataSort.completeByRouteParams("metadata.loss:desc,inserted_at:desc");

      expect(metadataSort.selected[0].name).toEqual("loss");
      expect(metadataSort.selected[0].sort).toEqual("desc");
      expect(metadataSort.selected[1].name).toEqual("inserted_at");
      expect(metadataSort.selected[1].sort).toEqual("desc");
    });
  });
});
