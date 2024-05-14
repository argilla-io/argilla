import {
  createMetadataMock,
  createMetadataWithNoValuesMock,
} from "../__mocks__/metadata/mock";
import { SortList } from "./SortList";

describe("SortList ", () => {
  describe("Select", () => {
    test("should be able to select a category", () => {
      const categoriesSort = new SortList(createMetadataMock(), []);

      categoriesSort.select({ key: "metadata", name: "split" });

      expect(
        categoriesSort.selected.map((m) => m.name).includes("split")
      ).toBeTruthy();
      expect(
        categoriesSort.noSelected.map((m) => m.name).includes("split")
      ).toBeFalsy();
    });
  });

  describe("Unselect", () => {
    test("should be able to unselect a category", () => {
      const categoriesSort = new SortList(createMetadataMock(), []);
      categoriesSort.select({ key: "metadata", name: "split" });

      categoriesSort.unselect({ key: "metadata", name: "split" });

      expect(categoriesSort.selected).toHaveLength(0);
      expect(
        categoriesSort.noSelected.map((m) => m.name).includes("split")
      ).toBeTruthy();
    });
  });

  describe("Replace", () => {
    test("should be able to replace a category", () => {
      const categoriesSort = new SortList(createMetadataMock(), []);
      categoriesSort.select({ key: "metadata", name: "loss" });
      expect(categoriesSort.selected[0].name).toEqual("loss");

      categoriesSort.replace(
        { key: "metadata", name: "loss" },
        { key: "metadata", name: "split" }
      );

      expect(
        categoriesSort.noSelected.map((m) => m.name).includes("loss")
      ).toBeTruthy();
      expect(
        categoriesSort.selected.map((m) => m.name).includes("split")
      ).toBeTruthy();
    });
  });

  describe("Clear", () => {
    test("should be able to clear all selected categories", () => {
      const categoriesSort = new SortList(createMetadataMock(), []);
      categoriesSort.select({ key: "metadata", name: "loss" });
      expect(
        categoriesSort.selected.map((m) => m.name).includes("loss")
      ).toBeTruthy();
      expect(
        categoriesSort.noSelected.map((m) => m.name).includes("loss")
      ).toBeFalsy();

      categoriesSort.clear();

      expect(categoriesSort.selected).toHaveLength(0);
      expect(
        categoriesSort.noSelected.map((m) => m.name).includes("loss")
      ).toBeTruthy();
    });
  });

  describe("toggleSort", () => {
    test("should be able to toggle sort", () => {
      const categoriesSort = new SortList(createMetadataMock(), []);
      categoriesSort.select({ key: "metadata", name: "loss" });
      expect(categoriesSort.selected[0].sort).toEqual("asc");

      categoriesSort.toggleSort({ key: "metadata", name: "loss" });

      expect(categoriesSort.selected[0].sort).toEqual("desc");
    });
  });

  describe("commit should", () => {
    test("be able to convert to router params", () => {
      const categoriesSort = new SortList(createMetadataMock(), []);
      categoriesSort.select({ key: "metadata", name: "loss" });
      categoriesSort.select({ key: "metadata", name: "split" });
      categoriesSort.toggleSort({ key: "metadata", name: "loss" });

      const param = categoriesSort.commit();

      expect(param[0].entity).toEqual("metadata");
      expect(param[0].name).toEqual("loss");
      expect(param[0].order).toEqual("desc");

      expect(param[1].entity).toEqual("metadata");
      expect(param[1].name).toEqual("split");
      expect(param[1].order).toEqual("asc");
    });
  });

  describe("Complete by Route Params", () => {
    test("should be able to complete by route params", () => {
      const categoriesSort = new SortList(createMetadataMock(), []);
      categoriesSort.complete([
        { entity: "metadata", name: "loss", order: "desc" },
        { entity: "record", name: "inserted_at", order: "asc" },
      ]);

      expect(categoriesSort.selected[0].key).toEqual("metadata");
      expect(categoriesSort.selected[0].name).toEqual("loss");
      expect(categoriesSort.selected[0].sort).toEqual("desc");
      expect(categoriesSort.selected[1].key).toEqual("record");
      expect(categoriesSort.selected[1].name).toEqual("inserted_at");
      expect(categoriesSort.selected[1].sort).toEqual("asc");
    });
  });

  describe("Can sort should", () => {
    test("return true if the metadata sort has value", () => {
      const categoriesSort = new SortList(createMetadataMock(), []);

      categoriesSort.noSelected.forEach((categoriesSort) => {
        expect(categoriesSort.canSort).toBeTruthy();
      });
    });

    test("return false if the metadata sort has value", () => {
      const metadataForSortingWithoutValues = createMetadataWithNoValuesMock();
      const categoriesSort = new SortList(metadataForSortingWithoutValues, []);

      categoriesSort.noSelected
        .filter((n) =>
          metadataForSortingWithoutValues.some((m) => m.name === n.name)
        )
        .forEach((metadata) => {
          expect(metadata.canSort).toBeFalsy();
        });
    });

    test("return always true for metadata hardcoded like inserted at and updated at", () => {
      const metadataForSortingWithoutValues = createMetadataWithNoValuesMock();
      const categoriesSort = new SortList(metadataForSortingWithoutValues, []);

      categoriesSort.select({
        key: "record",
        name: "inserted_at",
      });
      categoriesSort.select({ key: "record", name: "updated_at" });

      categoriesSort.selected.forEach((categoriesSort) => {
        expect(categoriesSort.canSort).toBeTruthy();
      });
    });
  });
});
