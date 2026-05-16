# gluestack-ui v3 Setup

Use the official gluestack CLI from the project root. Check the current docs before running commands because v3 package names and generated paths may change.

## Bootstrap

Initialize gluestack-ui:

```sh
npx gluestack-ui init
```

If the CLI asks for a framework, select Expo / React Native. If it asks where to place components, prefer `components/ui` unless the project already has a clear convention.

## Starter Components

Install a practical starter set:

```sh
npx gluestack-ui add box vstack hstack text heading button card input badge divider icon toast
```

If a component name has changed, use the current CLI suggestions and keep the intent of the starter set:

- Layout: Box, VStack, HStack
- Typography: Text, Heading
- Action: Button
- Form: Input
- Display: Card, Badge, Divider
- Feedback: Toast or Alert
- Media/icon: Icon

Do not install every component unless the user asks for a kitchen-sink starter.

## Provider Wiring

After init, inspect generated files and wire the provider exactly as the CLI expects. Common locations include:

- `components/ui/gluestack-ui-provider`
- `components/ui/gluestack-ui-provider/index.tsx`
- generated CSS/theme files

For Expo Router, the provider normally belongs in `app/_layout.tsx` around the root `Stack`.

Also ensure `global.css` is imported before rendering UI.

## Placeholder Screen

Use `examples/placeholder-screen.tsx` as a structure, but adjust import paths to match the generated component files. If the generated API differs, prefer the current generated component API over the example.
