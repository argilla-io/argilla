export default (context, inject) => {
  // colors range for entities
  inject("entitiesMaxColors", 50);
  // suggestion spark icon
  inject(
    "suggestionIcon",
    "<svg width='12' viewBox='0 0 36 36' fill='none' xmlns='http://www.w3.org/2000/svg'><path d='M34.3469 16.893L25.4479 13.599L22.1249 2.708C21.9969 2.288 21.6079 2 21.1689 2C20.7299 2 20.3409 2.288 20.2129 2.708L16.8909 13.599L7.99089 16.893C7.59789 17.039 7.33789 17.412 7.33789 17.831C7.33789 18.249 7.59789 18.624 7.99089 18.769L16.8859 22.062L20.2099 33.285C20.3359 33.709 20.7259 34 21.1689 34C21.6109 34 22.0019 33.709 22.1279 33.284L25.4519 22.061L34.3479 18.768C34.7389 18.624 34.9999 18.25 34.9999 17.831C34.9999 17.413 34.7389 17.039 34.3469 16.893Z' fill='#FEE075'/><path d='M10.009 6.231L7.645 5.356L6.769 2.991C6.624 2.598 6.25 2.338 5.831 2.338C5.413 2.338 5.039 2.598 4.893 2.991L4.018 5.356L1.653 6.231C1.26 6.377 1 6.751 1 7.169C1 7.587 1.26 7.962 1.653 8.107L4.018 8.982L4.893 11.347C5.039 11.74 5.413 12 5.831 12C6.249 12 6.623 11.74 6.769 11.347L7.644 8.982L10.009 8.107C10.402 7.961 10.662 7.587 10.662 7.169C10.662 6.751 10.402 6.377 10.009 6.231Z' fill='#FEE075'/></svg>"
  );
};
