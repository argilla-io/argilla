export default ({ $auth, route, redirect }) => {
  if (!route.path.includes("/login")) {
    if (!$auth.loggedIn) {
      const REDIRECT_URL = "/login?redirect=" + route.path;
      redirect(REDIRECT_URL);
    } 
  }
};
