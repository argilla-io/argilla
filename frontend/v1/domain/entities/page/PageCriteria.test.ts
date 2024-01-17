import { PageCriteria } from "./PageCriteria";

describe("PageCriteria", () => {
  describe("next", () => {
    it("should return the next page", () => {
      const pageCriteria = new PageCriteria();

      pageCriteria.client = {
        page: 1,
        many: 10,
      };

      expect(pageCriteria.next).toEqual(2);
    });
  });

  describe("previous", () => {
    test("should return the previous page", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.client = {
        page: 2,
        many: 10,
      };

      expect(pageCriteria.previous).toEqual(1);
    });
  });

  describe("urlParams", () => {
    it("should return the url params for focus", () => {
      const pageCriteria = new PageCriteria();

      pageCriteria.focusMode();

      expect(pageCriteria.urlParams).toEqual("1");
    });

    it("should return the url params for bulk", () => {
      const pageCriteria = new PageCriteria();

      pageCriteria.bulkMode();

      expect(pageCriteria.urlParams).toEqual("1~10");
    });
  });

  describe("complete", () => {
    it("should set page and many from url params", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.complete("1~10");
      expect(pageCriteria.client).toEqual({
        page: 1,
        many: 10,
      });
    });

    it("should set default page and many from url params", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.complete("1~");
      expect(pageCriteria.client).toEqual({
        page: 1,
        many: 10,
      });
    });

    it("should set the default page and many from url params when the `many` no exists in options", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.complete("1~11");
      expect(pageCriteria.client).toEqual({
        page: 1,
        many: 10,
      });
    });
  });

  describe("reset", () => {
    test("should reset the client page criteria", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.client = {
        page: 1,
        many: 25,
      };

      pageCriteria.reset();

      expect(pageCriteria.client).toEqual({
        page: 1,
        many: 10,
      });
    });

    test("should reset the server page criteria", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.client = {
        page: 10,
        many: 25,
      };

      pageCriteria.synchronizePagination({
        from: 9,
        many: 25,
      });

      pageCriteria.reset();

      expect(pageCriteria.server).toEqual({
        from: 1,
        many: 10,
      });
    });
  });

  describe("goToFirst", () => {
    test("should set the client page to 1", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.client = {
        page: 10,
        many: 10,
      };

      pageCriteria.goToFirst();

      expect(pageCriteria.client).toEqual({
        page: 1,
        many: 10,
      });
    });
  });

  describe("isFirstPage", () => {
    test("should return true when the client page is 1", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.client = {
        page: 1,
        many: 25,
      };

      expect(pageCriteria.isFirstPage()).toBeTruthy();
    });

    test("should return false when the client page is not 1", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.client = {
        page: 2,
        many: 25,
      };

      expect(pageCriteria.isFirstPage()).toBeFalsy();
    });
  });
});
