# 🗂️ Folder structure

```
.
├── assets
│ ├── fonts
│ ├── icons
│ └── scss
├── database -> Vuex modules (to be removed)
├── models -> Vuex models (to be removed)
├── store -> Vuex store (to be removed)
├── components
│ ├── base -> Base and stateless components
│ ├── features -> Features used in just one page
│ ├── annotation -> Componentes used in Annotation page
│ ├── datasets -> Components to support datasets page
│ ├── global -> Components used in multiple pages ex: UserAvatarComponent
│ ├── login -> Components to support login page
│ └── user-settings -> Components to support user settings page
├── e2e -> E2E tests
├── layouts -> Layout components
├── middleware -> Nuxt middlewares
├── pages -> Nuxt global pages
├── plugins -> Nuxt plugins
├── static -> Static resources
├── translations -> Argilla translation resources
├── v1 -> New architecture
│ ├── di
│ ├── domain
│ ├── infrastructure
│ └── store
│...
├── package.json
├── package-lock.json
└── .gitignore
```
