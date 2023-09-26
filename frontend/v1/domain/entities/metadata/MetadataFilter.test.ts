import { createMetadataMock } from "../__mocks__/metadata/mock";
import { MetadataFilter } from "./MetadataFilter";

describe("MetadataFilter ", () => {
  describe("Find by Category", () => {
    test("should return the metadata by category", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      const metadata = metadataFilter.findByCategory("split");

      expect(metadata).toEqual(createMetadataMock()[0]);
    });

    test("should return undefined if the category does not exist", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      const metadata = metadataFilter.findByCategory("not-exist");

      expect(metadata).toBeUndefined();
    });
  });

  describe("Categories", () => {
    test("should return the categories", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      const categories = metadataFilter.categories;

      expect(categories).toEqual([
        "split",
        "loss",
        "float",
        "split_2",
        "split_3",
      ]);
    });
    test("should return empty array if there is no metadata", () => {
      const metadataFilter = new MetadataFilter([]);
      const categories = metadataFilter.categories;

      expect(categories).toEqual([]);
    });
  });

  describe("FilteredCategories", () => {
    test("should return the categories", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      const categories = metadataFilter.filteredCategories;

      expect(categories).toEqual([]);
    });

    test("should return empty array if there is no metadata", () => {
      const metadataFilter = new MetadataFilter([]);
      const categories = metadataFilter.filteredCategories;

      expect(categories).toEqual([]);
    });

    test("should return the categories with selected options", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      metadataFilter.findByCategory("split").completeMetadata("test,train");
      const categories = metadataFilter.filteredCategories;

      expect(categories).toEqual(["split"]);
    });
  });

  describe("Convert to Router Parameter", () => {
    test("should return the router params for answered filters for terms", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      metadataFilter.findByCategory("split").completeMetadata("test,train");
      const routerParams = metadataFilter.convertToRouteParam();

      expect(routerParams).toEqual(["split:test,train"]);
    });

    test("should return the router params for answered filters for numbers", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      metadataFilter
        .findByCategory("loss")
        .completeMetadata(JSON.stringify({ from: 10, to: 20 }));
      const routerParams = metadataFilter.convertToRouteParam();

      // eslint-disable-next-line quotes
      expect(routerParams).toEqual(['loss:{"from":10,"to":20}']);
    });

    test("should return the router params for answered filters", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      const routerParams = metadataFilter.convertToRouteParam();

      expect(routerParams).toEqual([]);
    });
  });

  describe("Complete By Route Parameter", () => {
    test("should complete the metadata filter by route params", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      metadataFilter.completeByRouteParams(
        // eslint-disable-next-line quotes
        'split:test,train+loss:{"from":10,"to":20}+float:{"from":0.5,"to":0.6}'
      );

      expect(
        metadataFilter
          .findByCategory("split")
          .selectedOptions.map((option) => option.label)
      ).toEqual(["test", "train"]);
      expect(metadataFilter.findByCategory("loss").value).toEqual({
        from: 10,
        to: 20,
      });

      expect(metadataFilter.findByCategory("float").value).toEqual({
        from: 0.5,
        to: 0.6,
      });
    });

    test("no modify anything when the param does not contain the option", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      metadataFilter.completeByRouteParams("");

      expect(
        metadataFilter
          .findByCategory("split")
          .selectedOptions.map((option) => option.label)
      ).toEqual([]);
    });

    test("no modify anything when the meta does not exist", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      metadataFilter.completeByRouteParams("not-exist:10");

      expect(
        metadataFilter
          .findByCategory("split")
          .selectedOptions.map((option) => option.label)
      ).toEqual([]);
    });

    test("set settings value when the json is not valid", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      metadataFilter.completeByRouteParams("loss:invalid");

      expect(metadataFilter.findByCategory("loss").value).toEqual({
        from: 0,
        to: 2,
      });
    });
  });

  describe("Has Filters", () => {
    test("should return true if there is filters", () => {
      const metadataFilter = new MetadataFilter(createMetadataMock());
      metadataFilter.completeByRouteParams("split:test,train");

      expect(metadataFilter.hasFilters).toBeTruthy();
    });

    test("should return false if there is no filters", () => {
      const metadataFilter = new MetadataFilter([]);

      expect(metadataFilter.hasFilters).toBeFalsy();
    });
  });
});
