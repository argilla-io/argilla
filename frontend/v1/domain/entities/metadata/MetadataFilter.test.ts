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

      expect(categories).toEqual(["split", "loss", "float"]);
    });
    test("should return empty array if there is no metadata", () => {
      const metadataFilter = new MetadataFilter([]);
      const categories = metadataFilter.categories;

      expect(categories).toEqual([]);
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
      metadataFilter.findByCategory("loss").completeMetadata("0.50");
      const routerParams = metadataFilter.convertToRouteParam();

      expect(routerParams).toEqual(["loss:0.5"]);
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
        "split:test,train+loss:10+float:0.5"
      );

      expect(
        metadataFilter
          .findByCategory("split")
          .selectedOptions.map((option) => option.label)
      ).toEqual(["test", "train"]);
      expect(metadataFilter.findByCategory("loss").value).toEqual(10);
      expect(metadataFilter.findByCategory("float").value).toEqual(0.5);
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
  });
});
