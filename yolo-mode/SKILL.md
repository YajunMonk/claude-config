---
name: yolo-mode
description: Use when developing, modifying, or polishing any website, application, backend service, API, serverless function, or other deployable product where the user wants every content or code change deployed directly to the configured production environment and reported with a public URL, endpoint, or deployment link for immediate mobile review. Triggers on phrases such as Yolo Mode, deploy every change, mobile preview, production link, or any development task where this mode is explicitly enabled.
---

# Yolo Mode

## Purpose

Yolo Mode turns development into an immediate production-preview loop: after every meaningful file change, verify what can be verified, deploy to the project's configured production target, and report the public URL, endpoint, or deployment link so the user can open it on a phone.

Use this skill only when the user explicitly enables Yolo Mode or asks for the behavior described above. Once enabled for a task, keep applying it throughout that task until the user disables it.

## Operating Rule

For any deployable product change, treat deployment as part of the change itself.

1. Make the smallest coherent change requested by the user.
2. Run the fastest relevant local check available, such as lint, typecheck, tests, build, or a browser smoke check.
3. Deploy the current project or service to its configured production environment immediately after the check.
4. Report the public production URL, endpoint, or deployment link in the working update or final response.
5. Continue this loop for each later content, UI, behavior, or configuration change.

Do not wait for a batch of unrelated improvements before deploying. If a single user request naturally requires several tightly coupled edits before the app can build, finish that coherent edit set, then deploy once.

## What Counts As A Change

Deploy after changes to:

- UI text, layout, styling, assets, pages, routes, components, or copy.
- Application behavior, backend behavior, API routes, server actions, data fetching, jobs, workers, functions, or state logic.
- Configuration that affects runtime, build output, routing, metadata, environment usage, public assets, or service endpoints.
- Dependency updates or generated files that change the deployed result.

Do not deploy after:

- Pure investigation with no file changes.
- Notes, scratch files, or local-only analysis outside the app/site project.
- Failed edits that have been reverted before any stable state exists.

## Production Deployment Workflow

Use the project's existing deployment setup first. Do not assume a specific hosting provider or invent a new target. Common acceptable paths are:

- A project script such as `npm run deploy`, `pnpm deploy`, `bun run deploy`, or the documented equivalent.
- A configured hosting or cloud CLI for the current project.
- A platform plugin/tool when the current workspace is already linked to that platform.
- A backend rollout path such as serverless function deploy, container/image publish plus rollout, worker deploy, or managed backend release.

Before deploying, confirm the command is targeting the intended project or service directory. If the project is not linked to a production target, use the platform's normal linking flow or available app tools. If authentication, project selection, missing environment variables, unsafe migration state, or missing production configuration blocks deployment, stop and report the exact blocker plus the last successful local check.

## Reporting

Keep the user-facing message short and practical:

- Say what changed.
- Say what check passed or could not be run.
- Provide the public production URL, endpoint, or deployment link.

If a production deployment succeeds but returns both an immutable deployment URL and an aliased production domain, report the production domain first and include the immutable URL only when useful for comparison. For backend-only changes, report the public API endpoint, health URL, dashboard deployment link, or other best available production access point.

## Safety Boundaries

Yolo Mode intentionally deploys to production, so do not ask for extra confirmation each time. Still apply normal engineering discipline:

- Never expose secrets in code, logs, URLs, or screenshots.
- Do not skip obvious build checks when they are quick and available.
- Do not hide deployment failures; report them clearly and keep the local work ready for the next deploy attempt.
- Do not deploy a different directory or service than the product being edited.
