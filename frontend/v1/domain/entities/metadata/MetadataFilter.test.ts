import {
  createMetadataMock,
  createMetadataWithNoValuesMock,
} from "../__mocks__/metadata/mock";
import { MetadataFilterList } from "./MetadataFilter";

describe("MetadataFilter ", () => {
  describe("Find by Category", () => {
    test("should return the metadata by category", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = metadataFilter.findByCategory("split");

      expect(metadata.name).toEqual(createMetadataMock()[0].name);
    });

    test("should return undefined if the category does not exist", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = metadataFilter.findByCategory("not-exist");

      expect(metadata).toBeUndefined();
    });
  });

  describe("Categories", () => {
    test("should return the categories", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const categories = metadataFilter.categories;

      expect(categories.map((n) => n.name)).toEqual([
        "split",
        "loss",
        "float",
        "split_2",
        "split_3",
      ]);
    });
    test("should return empty array if there is no metadata", () => {
      const metadataFilter = new MetadataFilterList([]);
      const categories = metadataFilter.categories;

      expect(categories).toEqual([]);
    });
  });

  describe("FilteredCategories", () => {
    test("should return the categories", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());

      metadataFilter.commit();

      expect(metadataFilter.filteredCategories).toEqual([]);
    });

    test("should return empty array if there is no metadata", () => {
      const metadataFilter = new MetadataFilterList([]);

      metadataFilter.commit();

      expect(metadataFilter.filteredCategories).toEqual([]);
    });

    test("should return the categories with selected options", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.findByCategory("split").completeMetadata("test,train");

      metadataFilter.commit();

      expect(metadataFilter.filteredCategories.map((f) => f.name)).toEqual([
        "split",
      ]);
    });
  });

  describe("commit Parameter", () => {
    test("should return the router params for answered filters for terms", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.findByCategory("split").completeMetadata("test,train");

      const committedFilters = metadataFilter.commit();

      expect(committedFilters).toEqual(["split:test,train"]);
    });

    test("should return the router params for answered filters for numbers", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter
        .findByCategory("loss")
        .completeMetadata(JSON.stringify({ ge: 10, le: 20 }));

      const committedFilters = metadataFilter.commit();

      // eslint-disable-next-line quotes
      expect(committedFilters).toEqual(['loss:{"ge":10,"le":20}']);
    });

    test("should return the router params for answered filters", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());

      const committedFilters = metadataFilter.commit();

      expect(committedFilters).toEqual([]);
    });

    test("should return the filtered metadata in the same order answered by the user", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter
        .findByCategory("loss")
        .completeMetadata(JSON.stringify({ ge: 10, le: 20 }));

      // First search
      metadataFilter.commit();
      metadataFilter.findByCategory("split").completeMetadata("test,train");

      // Second search
      const committedFilters = metadataFilter.commit();

      expect(committedFilters).toEqual([
        // eslint-disable-next-line quotes
        'loss:{"ge":10,"le":20}',
        "split:test,train",
      ]);
    });
  });

  describe("Initialize With", () => {
    test("should complete the metadata filter by route params", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.initializeWith([
        "split:test,train",
        // eslint-disable-next-line quotes
        'loss:{"ge":10,"le":20}',
        // eslint-disable-next-line quotes
        'float:{"ge":0.5,"le":0.6}',
      ]);

      expect(
        metadataFilter
          .findByCategory("split")
          .selectedOptions.map((option) => option.label)
      ).toEqual(["test", "train"]);
      expect(metadataFilter.findByCategory("loss").value).toEqual({
        ge: 10,
        le: 20,
      });
      expect(metadataFilter.findByCategory("float").value).toEqual({
        ge: 0.5,
        le: 0.6,
      });
    });

    test("should not support duplicated filtered categories", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.initializeWith(["split:test,train"]);

      metadataFilter.initializeWith(["split:test,train"]);

      expect(metadataFilter.filteredCategories.map((f) => f.name)).toEqual([
        "split",
      ]);
    });

    test("the user can see the filtered categories in the same order that he/she selected", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.initializeWith([
        // eslint-disable-next-line quotes
        'loss:{"ge":10,"le":20}',
        // eslint-disable-next-line quotes
        'float:{"ge":0.5,"le":0.6}',
        "split:test,train",
      ]);

      expect(metadataFilter.filteredCategories.map((f) => f.name)).toEqual([
        "loss",
        "float",
        "split",
      ]);
    });

    test("no modify anything when the param does not contain the option", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.initializeWith([]);

      expect(
        metadataFilter
          .findByCategory("split")
          .selectedOptions.map((option) => option.label)
      ).toEqual([]);
    });

    test("no modify anything when the meta does not exist", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.initializeWith(["not-exist:10"]);

      expect(
        metadataFilter
          .findByCategory("split")
          .selectedOptions.map((option) => option.label)
      ).toEqual([]);
    });

    test("set settings value when the json is not valid", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.initializeWith(["loss:invalid"]);

      expect(metadataFilter.findByCategory("loss").value).toEqual({
        ge: 0,
        le: 2,
      });
    });
  });

  describe("Has Filters", () => {
    test("should return true if there is filters", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.initializeWith(["split:test", "train"]);

      expect(metadataFilter.hasFilters).toBeTruthy();
    });

    test("should return false if there is no filters", () => {
      const metadataFilter = new MetadataFilterList([]);

      expect(metadataFilter.hasFilters).toBeFalsy();
    });
  });

  describe("Complete metadata", () => {
    test("should complete the metadata when is terms", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = metadataFilter.findByCategory("split");

      metadata.completeMetadata("test,train");

      expect(metadata.selectedOptions.map((option) => option.label)).toEqual([
        "test",
        "train",
      ]);
    });
    test("should complete the metadata when is integer", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = metadataFilter.findByCategory("loss");

      metadata.completeMetadata(JSON.stringify({ ge: 10, le: 20 }));

      expect(metadata.value).toEqual({ ge: 10, le: 20 });
    });
  });

  describe("Clear", () => {
    test("should clear the metadata when is terms", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = metadataFilter.findByCategory("split");

      metadata.clear();

      expect(metadata.selectedOptions.map((option) => option.label)).toEqual(
        []
      );
    });

    test("should clear the metadata when is integer set the settings max and min values", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = metadataFilter.findByCategory("loss");
      metadata.completeMetadata(JSON.stringify({ ge: 10, le: 20 }));
      metadata.clear();

      expect(metadata.value).toEqual({ ge: 0, le: 2 });
    });
  });

  describe("Can Filter", () => {
    test("should return true if the metadata has values", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = metadataFilter.findByCategory("split");

      expect(metadata.canFilter).toBeTruthy();
    });

    test("should return false if terms metadata has no values", () => {
      const metadataFilter = new MetadataFilterList(
        createMetadataWithNoValuesMock()
      );
      const metadata = metadataFilter.findByCategory("split");

      expect(metadata.canFilter).toBeFalsy();
    });

    test("should return false if integer metadata has no values", () => {
      const metadataFilter = new MetadataFilterList(
        createMetadataWithNoValuesMock()
      );
      const metadata = metadataFilter.findByCategory("loss");

      expect(metadata.canFilter).toBeFalsy();
    });

    test("should return false if float metadata has no values", () => {
      const metadataFilter = new MetadataFilterList(
        createMetadataWithNoValuesMock()
      );
      const metadata = metadataFilter.findByCategory("float");

      expect(metadata.canFilter).toBeFalsy();
    });
  });
});
