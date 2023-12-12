# Next.js Project Structure

This document provides an overview of the file and folder structure in a Next.js project. It includes details about top-level files and folders, configuration files, and routing conventions within the `app` and `pages` directories.

## Top-level Folders
- `app`: App Router
- `pages`: Pages Router
- `public`: Static assets to be served
- `src`: Optional application source folder

## Top-level Files
- `next.config.js`: Configuration file for Next.js
- `package.json`: Project dependencies and scripts
- `instrumentation.ts`: OpenTelemetry and Instrumentation file
- `middleware.ts`: Next.js request middleware
- `.env`: Environment variables
- `.env.local`: Local environment variables
- `.env.production`: Production environment variables
- `.env.development`: Development environment variables
- `.eslintrc.json`: ESLint configuration file
- `.gitignore`: Git files and folders to ignore
- `next-env.d.ts`: TypeScript declaration file for Next.js
- `tsconfig.json`: TypeScript configuration file
- `jsconfig.json`: JavaScript configuration file

## App Routing Conventions
### Routing Files
- `layout`: .js, .jsx, .tsx - Layout
- `page`: .js, .jsx, .tsx - Page
- `loading`: .js, .jsx, .tsx - Loading UI
- `not-found`: .js, .jsx, .tsx - Not found UI
- `error`: .js, .jsx, .tsx - Error UI
- `global-error`: .js, .jsx, .tsx - Global error UI
- `route`: .js, .ts - API endpoint
- `template`: .js, .jsx, .tsx - Re-rendered layout
- `default`: .js, .jsx, .tsx - Parallel route fallback page

### Nested Routes
- `folder`: Route segment
- `folder/folder`: Nested route segment

### Dynamic Routes
- `[folder]`: Dynamic route segment
- `[...folder]`: Catch-all route segment
- `[[...folder]]`: Optional catch-all route segment

### Route Groups and Private Folders
- `(folder)`: Group routes without affecting routing
- `_folder`: Opt folder and all child segments out of routing

### Parallel and Intercepted Routes
- `@folder`: Named slot
- `(.)folder`: Intercept same level
- `(..)folder`: Intercept one level above
- `(..)(..)folder`: Intercept two levels above
- `(...)folder`: Intercept from root

## Metadata File Conventions
### App Icons
- `favicon`: .ico - Favicon file
- `icon`: .ico, .jpg, .jpeg, .png, .svg - App Icon file
- `icon`: .js, .ts, .tsx - Generated App Icon
- `apple-icon`: .jpg, .jpeg, .png - Apple App Icon file
- `apple-icon`: .js, .ts, .tsx - Generated Apple App Icon

### Open Graph and Twitter Images
- `opengraph-image`: .jpg, .jpeg, .png, .gif - Open Graph image file
- `opengraph-image`: .js, .ts, .tsx - Generated Open Graph image
- `twitter-image`: .jpg, .jpeg, .png, .gif - Twitter image file
- `twitter-image`: .js, .ts, .tsx - Generated Twitter image

### SEO
- `sitemap`: .xml - Sitemap file
- `sitemap`: .js, .ts - Generated Sitemap
- `robots`: .txt - Robots file
- `robots`: .js, .ts - Generated Robots file

## Pages Routing Conventions
### Special Files
- `_app`: .js, .jsx, .tsx - Custom App
- `_document`: .js, .jsx, .tsx - Custom Document
- `_error`: .js, .jsx, .tsx - Custom Error Page
- `404`: .js, .jsx, .tsx - 404 Error Page
- `500`: .js, .jsx, .tsx - 500 Error Page

### Routes
#### Folder Convention
- `index`: .js, .jsx, .tsx - Home page
- `folder/index`: .js, .jsx, .tsx - Nested page

#### File Convention
- `index`: .js, .jsx, .tsx - Home page
- `file`: .js, .jsx, .tsx - Nested page

### Dynamic Routes
#### Folder Convention
- `[folder]/index`: .js, .jsx, .tsx - Dynamic route segment
- `[...folder]/index`: .js, .jsx, .tsx - Catch-all route segment
- `[[...folder]]/index`: .js, .jsx, .tsx - Optional catch-all route segment

#### File Convention
- `[file]`: .js, .jsx, .tsx - Dynamic route segment
- `[...file]`: .js, .jsx, .tsx - Catch-all route segment
- `[[...file]]`: .js, .jsx, .tsx - Optional catch-all route segment
