you cannot run commands on the command line.  if you need to run a command, ask the user to run it for you and provide the output in the chat.

## model.xml Schema Expectations
When working with Cognos `*model.xml` files, keep in mind the following structural rules based on our validation logic:
- **Namespaces:** XML elements typically include namespaces (e.g., `{http://www.developer.cognos.com/schemas/bmt/60/12}tag`).
- **`querySubject` Elements:**
  - Must include a `<definition>` element, which in turn must contain either `<dbQuery>` or `<modelQuery>`.
  - Inside a `<dbQuery>`, there must be a `<sql>` element.
  - Unless it's a `<modelQuery>`, each `querySubject` must have exactly one `<sources>` element.
  - The `<sources>` element must contain at least one `<dataSourceRef>` (having multiple `dataSourceRef`s is considered valid).
- **`dataSource` Elements:**
  - Must have a `<name>` element.
  - Must have exactly one `<cmDataSource>` element.
  - The `<schema>` element is optional (0 or 1 is valid). While missing a schema is allowed, having more than 1 is considered an error.