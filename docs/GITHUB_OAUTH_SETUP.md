# GitHub OAuth Setup Guide for Pulse-Hub

**Complete guide to configuring GitHub OAuth authentication for pulse-hub multi-service platform**

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Difficulty**: Beginner
**Estimated Time**: 30 minutes

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [OAuth Application Creation](#oauth-application-creation)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [Security Best Practices](#security-best-practices)
8. [Advanced Topics](#advanced-topics)

---

## Overview

### What is GitHub OAuth?

GitHub OAuth is an authentication protocol that allows pulse-hub to:

- **Authenticate users** using their GitHub accounts (no password management required)
- **Access user data** such as repositories, issues, pull requests (with user permission)
- **Perform actions** on behalf of users (create issues, manage repositories)

### Authentication Flow

```
┌──────────┐                                      ┌──────────┐
│  User    │                                      │  GitHub  │
└────┬─────┘                                      └────┬─────┘
     │                                                 │
     │  1. Click "Sign in with GitHub"                │
     ├──────────────────────────────────────────────► │
     │                                                 │
     │  2. Redirect to GitHub OAuth authorization     │
     │ ◄────────────────────────────────────────────┤ │
     │                                                 │
     │  3. User authorizes application                │
     ├──────────────────────────────────────────────► │
     │                                                 │
     │  4. Redirect back with authorization code      │
     │ ◄────────────────────────────────────────────┤ │
     │                                                 │
┌────▼─────┐                                          │
│ Pulse-Hub│  5. Exchange code for access token       │
│ Backend  ├──────────────────────────────────────────►│
└────┬─────┘                                          │
     │  6. Receive access token                       │
     │ ◄────────────────────────────────────────────┤ │
     │                                                 │
     │  7. Use access token to fetch user info        │
     ├──────────────────────────────────────────────► │
     │                                                 │
     │  8. Create session, redirect to dashboard      │
     │                                                 │
```

### Why OAuth Instead of Passwords?

**Security Benefits**:
- No password storage required
- User passwords never sent to pulse-hub
- Revocable access (users can revoke at any time)
- Scoped permissions (request only needed access)

**User Experience Benefits**:
- Single sign-on (use existing GitHub account)
- No registration form required
- Automatic profile information (name, avatar, email)

---

## Prerequisites

### Required Accounts

1. **GitHub Account** with admin access to create OAuth Apps
   - Personal account: Create OAuth App in Settings
   - Organization: Requires owner/admin role

2. **Pulse-Hub Deployment**
   - Deployed to DigitalOcean App Platform
   - Production URL known (e.g., `https://pulse-hub-web-abc123.ondigitalocean.app`)

### Required Information

Before starting, gather:

- **Application Name**: Pulse-Hub (or your custom name)
- **Homepage URL**: Your pulse-hub production URL
- **Callback URL**: `<production-url>/api/auth/callback/github`
- **Application Description**: Brief description for users

### Access Verification

```bash
# Verify GitHub CLI access
gh auth status

# Or verify manual access
# Navigate to: https://github.com/settings/developers
# Should see "Developer settings" option
```

---

## OAuth Application Creation

### Step 1: Access GitHub Developer Settings

#### For Personal Account

1. Navigate to GitHub Settings:
   - Click your profile picture (top-right)
   - Select **Settings**
   - Scroll to **Developer settings** (bottom-left)
   - Click **OAuth Apps**

2. Direct link: https://github.com/settings/developers

#### For Organization

1. Navigate to Organization Settings:
   - Go to your organization page
   - Click **Settings** tab
   - Select **Developer settings** (left sidebar)
   - Click **OAuth Apps**

2. Direct link: `https://github.com/organizations/<org-name>/settings/applications`

**Note**: Organization OAuth Apps require owner/admin role

### Step 2: Create New OAuth App

1. Click **New OAuth App** button

2. Fill in Application Information:

   **Application name**: `Pulse-Hub`
   - This name is shown to users during authorization
   - Should be descriptive and recognizable

   **Homepage URL**: `https://pulse-hub-web-abc123.ondigitalocean.app`
   - Your production deployment URL
   - Must be a valid HTTPS URL
   - Can be updated later if deployment URL changes

   **Application description** (optional):
   ```
   Pulse-Hub is a GitHub-integrated analytics and workflow management platform
   providing real-time insights, AI-powered tools, and business intelligence
   dashboards for development teams.
   ```

   **Authorization callback URL**: `https://pulse-hub-web-abc123.ondigitalocean.app/api/auth/callback/github`
   - **Critical**: Must match exactly what your app expects
   - **Format**: `<homepage-url>/api/auth/callback/github`
   - **NextAuth.js**: Uses `/api/auth/callback/github` by default
   - Can register multiple callback URLs (development + production)

   **Enable Device Flow**: ❌ Leave unchecked
   - Not required for web applications

3. Click **Register application**

### Step 3: Generate Client Credentials

After creating the OAuth App:

1. **Client ID** is automatically generated and displayed
   - Format: `Ov23liXXXXXXXXXXXXXX` (20 characters)
   - **Copy this value** - you'll need it for configuration

2. **Generate Client Secret**:
   - Click **Generate a new client secret**
   - Secret is shown **only once** - copy immediately
   - Format: `1234567890abcdef1234567890abcdef12345678` (40 characters)
   - **Store securely** - cannot be retrieved later

3. **Save Credentials** to secure location:
   ```bash
   # Add to ~/.zshrc (local development)
   echo "export GITHUB_OAUTH_CLIENT_ID=Ov23liXXXXXXXXXXXXXX" >> ~/.zshrc
   echo "export GITHUB_OAUTH_CLIENT_SECRET=1234567890abcdef1234567890abcdef12345678" >> ~/.zshrc
   source ~/.zshrc
   ```

### Step 4: Verify OAuth App Configuration

Review the created OAuth App:

| Field | Expected Value | Notes |
|-------|----------------|-------|
| Client ID | `Ov23li...` (20 chars) | Public identifier, safe to commit in non-secret files |
| Client Secret | `1234567890abcdef...` (40 chars) | **Secret**, never commit to git |
| Homepage URL | `https://pulse-hub-web-...` | Production deployment URL |
| Callback URL | `https://pulse-hub-web-.../api/auth/callback/github` | Must match NextAuth.js route |
| Active | ✅ | OAuth App should be active (not revoked) |

---

## Configuration

### Environment Variable Mapping

Pulse-hub requires three OAuth-related environment variables:

| Variable | Source | Purpose | Example |
|----------|--------|---------|---------|
| `GITHUB_OAUTH_CLIENT_ID` | OAuth App Client ID | Public identifier for OAuth App | `Ov23liABC123XYZ789` |
| `GITHUB_OAUTH_CLIENT_SECRET` | OAuth App Client Secret | Private secret for token exchange | `1234567890abcdef...` |
| `NEXTAUTH_URL` | Deployment URL | OAuth callback base URL | `https://pulse-hub-web-abc123.ondigitalocean.app` |

### Development Environment Setup

#### Local Development (localhost)

1. **Create Development OAuth App** (separate from production):
   - Application name: `Pulse-Hub (Development)`
   - Homepage URL: `http://localhost:3000`
   - Callback URL: `http://localhost:3000/api/auth/callback/github`

2. **Configure Environment Variables**:

   Create `.env.local` in project root:
   ```bash
   # GitHub OAuth (Development)
   GITHUB_OAUTH_CLIENT_ID=Ov23liDEV123456789
   GITHUB_OAUTH_CLIENT_SECRET=dev1234567890abcdefghijklmnopqrstuvwxyz123
   NEXTAUTH_URL=http://localhost:3000

   # NextAuth.js
   NEXTAUTH_SECRET=<random-32-char-secret>  # Generate with: openssl rand -base64 32
   ```

3. **Generate NextAuth Secret**:
   ```bash
   # Generate random secret
   openssl rand -base64 32

   # Or use Node.js
   node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
   ```

4. **Test Local OAuth**:
   ```bash
   # Start development server
   npm run dev

   # Open browser to http://localhost:3000
   # Click "Sign in with GitHub"
   # Should redirect to GitHub authorization page
   ```

### Production Environment Setup

#### DigitalOcean App Platform

1. **Production OAuth App** (already created in previous steps):
   - Use production deployment URL from DigitalOcean

2. **Set Environment Variables in App Spec**:

   Edit `infra/pulse-hub/app-spec.yaml`:
   ```yaml
   services:
     - name: pulse-hub-web
       envs:
         # Public variables (can be in spec file)
         - key: GITHUB_OAUTH_CLIENT_ID
           value: Ov23liPROD123456789  # Production Client ID

         # Secrets (set via doctl or DO dashboard)
         - key: GITHUB_OAUTH_CLIENT_SECRET
           scope: RUN_TIME
           type: SECRET

         - key: NEXTAUTH_SECRET
           scope: RUN_TIME
           type: SECRET

         # Auto-generated from deployment URL
         - key: NEXTAUTH_URL
           value: ${APP_URL}  # DigitalOcean replaces with actual URL
   ```

3. **Set Secrets via doctl CLI**:
   ```bash
   # Get app ID
   APP_ID=$(doctl apps list --format ID,Spec.Name | grep pulse-hub | awk '{print $1}')

   # Set OAuth secret
   doctl apps update "$APP_ID" \
     --app-component-name pulse-hub-web \
     --env "GITHUB_OAUTH_CLIENT_SECRET=$GITHUB_OAUTH_CLIENT_SECRET"

   # Set NextAuth secret
   NEXTAUTH_SECRET=$(openssl rand -base64 32)
   doctl apps update "$APP_ID" \
     --app-component-name pulse-hub-web \
     --env "NEXTAUTH_SECRET=$NEXTAUTH_SECRET"
   ```

4. **Alternative: Set via DigitalOcean Dashboard**:
   - Navigate to: Apps → pulse-hub → Settings → pulse-hub-web → Environment Variables
   - Add encrypted environment variables:
     - `GITHUB_OAUTH_CLIENT_SECRET`: Paste secret, mark as encrypted
     - `NEXTAUTH_SECRET`: Paste secret, mark as encrypted

### OAuth Scopes Configuration

**Default Scopes** (for pulse-hub):
```typescript
// lib/auth.ts (NextAuth.js configuration)
import GitHubProvider from "next-auth/providers/github";

export const authOptions = {
  providers: [
    GitHubProvider({
      clientId: process.env.GITHUB_OAUTH_CLIENT_ID!,
      clientSecret: process.env.GITHUB_OAUTH_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: "repo workflow",  // Request these scopes
        },
      },
    }),
  ],
};
```

**Scope Meanings**:

| Scope | Access Level | Purpose | Required? |
|-------|-------------|---------|-----------|
| `repo` | Full repository access | Read/write repos, issues, PRs, code | ✅ Yes |
| `workflow` | GitHub Actions | Read/write Actions workflows, runs | ✅ Yes |
| `admin:repo_hook` | Webhooks | Create/manage webhooks | ⛔️ Only if needed |
| `read:user` | User profile | Read user profile info | Auto-granted |
| `user:email` | Email addresses | Read user email addresses | Auto-granted |

**Minimal Scopes** (if only reading data):
```typescript
scope: "repo:status repo:invite workflow"
// repo:status - Read commit statuses
// repo:invite - Read repository invites
// workflow - Read workflows (no write access)
```

**⚠️ Important**: Always request minimum required scopes (principle of least privilege)

---

## Testing

### Manual Testing Workflow

#### Step 1: Test Authentication Flow

1. **Navigate to Pulse-Hub**:
   ```bash
   # Development
   open http://localhost:3000

   # Production
   open https://pulse-hub-web-abc123.ondigitalocean.app
   ```

2. **Initiate OAuth Flow**:
   - Click "Sign in with GitHub" button
   - Should redirect to GitHub authorization page

3. **Verify Authorization Page**:
   - Application name matches OAuth App name
   - Scopes listed match requested permissions
   - Callback URL shown is correct

4. **Authorize Application**:
   - Click "Authorize <app-name>"
   - Should redirect back to pulse-hub

5. **Verify Successful Login**:
   - Should land on dashboard or intended page
   - User profile visible (name, avatar)
   - No error messages

#### Step 2: Verify Session Persistence

1. **Check Session Cookie**:
   - Open browser DevTools (F12)
   - Navigate to Application → Cookies
   - Verify `next-auth.session-token` cookie exists
   - Cookie should have:
     - `HttpOnly`: ✅ (security)
     - `Secure`: ✅ (HTTPS only)
     - `SameSite`: Lax or Strict

2. **Test Session Persistence**:
   - Refresh page - should remain logged in
   - Close tab and reopen - should remain logged in
   - Session should expire after configured timeout (default: 30 days)

#### Step 3: Test Authorization Scopes

1. **Verify Repository Access**:
   ```bash
   # Test API endpoint that uses GitHub data
   curl -H "Cookie: next-auth.session-token=<token>" \
     https://pulse-hub-web-abc123.ondigitalocean.app/api/github/repos

   # Should return list of user repositories
   ```

2. **Verify Workflow Access**:
   ```bash
   # Test Actions API endpoint
   curl -H "Cookie: next-auth.session-token=<token>" \
     https://pulse-hub-web-abc123.ondigitalocean.app/api/github/workflows

   # Should return list of workflows
   ```

3. **Verify Scope Limits**:
   - Try accessing data outside granted scopes
   - Should receive permission denied error

#### Step 4: Test Logout Flow

1. **Logout**:
   - Click "Logout" or "Sign out" button
   - Should redirect to login page

2. **Verify Session Cleared**:
   - Check DevTools → Cookies
   - `next-auth.session-token` should be deleted
   - Attempting to access protected pages should redirect to login

### Automated Testing

#### Unit Tests (Jest + NextAuth.js)

```typescript
// __tests__/auth.test.ts
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";

describe("GitHub OAuth", () => {
  it("should configure GitHub provider correctly", () => {
    const githubProvider = authOptions.providers.find(
      (p) => p.id === "github"
    );

    expect(githubProvider).toBeDefined();
    expect(githubProvider?.name).toBe("GitHub");
  });

  it("should request correct OAuth scopes", () => {
    const githubProvider = authOptions.providers[0];
    const authorizationParams = githubProvider.authorization?.params;

    expect(authorizationParams?.scope).toContain("repo");
    expect(authorizationParams?.scope).toContain("workflow");
  });

  it("should validate environment variables", () => {
    expect(process.env.GITHUB_OAUTH_CLIENT_ID).toBeDefined();
    expect(process.env.GITHUB_OAUTH_CLIENT_SECRET).toBeDefined();
    expect(process.env.NEXTAUTH_URL).toBeDefined();
    expect(process.env.NEXTAUTH_SECRET).toBeDefined();
  });
});
```

#### Integration Tests (Playwright)

```typescript
// e2e/auth.spec.ts
import { test, expect } from "@playwright/test";

test.describe("GitHub OAuth Flow", () => {
  test("should complete OAuth login flow", async ({ page, context }) => {
    // Navigate to pulse-hub
    await page.goto("http://localhost:3000");

    // Click "Sign in with GitHub"
    await page.click('button:has-text("Sign in with GitHub")');

    // Should redirect to GitHub
    await expect(page).toHaveURL(/github\.com\/login\/oauth\/authorize/);

    // Fill in GitHub credentials (test account)
    await page.fill('input[name="login"]', process.env.GITHUB_TEST_USERNAME);
    await page.fill('input[name="password"]', process.env.GITHUB_TEST_PASSWORD);
    await page.click('input[type="submit"]');

    // Authorize application (if first time)
    const authorizeButton = page.locator('button:has-text("Authorize")');
    if (await authorizeButton.isVisible()) {
      await authorizeButton.click();
    }

    // Should redirect back to pulse-hub
    await expect(page).toHaveURL(/localhost:3000\/dashboard/);

    // Should show user profile
    await expect(page.locator('[data-testid="user-avatar"]')).toBeVisible();
  });

  test("should maintain session after page refresh", async ({ page }) => {
    // Assume already logged in from previous test
    await page.goto("http://localhost:3000/dashboard");

    // Refresh page
    await page.reload();

    // Should still be logged in
    await expect(page.locator('[data-testid="user-avatar"]')).toBeVisible();
  });
});
```

### CI/CD Testing

#### GitHub Actions Workflow

```yaml
# .github/workflows/test-oauth.yml
name: Test OAuth Configuration

on:
  pull_request:
    paths:
      - "lib/auth.ts"
      - ".env.example"
      - "infra/pulse-hub/app-spec.yaml"

jobs:
  test-oauth-config:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install dependencies
        run: npm ci

      - name: Validate OAuth configuration
        env:
          GITHUB_OAUTH_CLIENT_ID: ${{ secrets.GITHUB_OAUTH_CLIENT_ID }}
          GITHUB_OAUTH_CLIENT_SECRET: ${{ secrets.GITHUB_OAUTH_CLIENT_SECRET }}
          NEXTAUTH_URL: http://localhost:3000
          NEXTAUTH_SECRET: test-secret-32-characters-long
        run: |
          npm run test:auth

      - name: Check for hardcoded secrets
        run: |
          if grep -r "Ov23li" --include="*.ts" --include="*.tsx" .; then
            echo "❌ ERROR: Hardcoded Client ID found"
            exit 1
          fi
          if grep -r "[0-9a-f]\{40\}" --include="*.ts" --include="*.tsx" .; then
            echo "⚠️  WARNING: Potential hardcoded secret found"
          fi
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Redirect URI Mismatch" Error

**Symptoms**:
- After authorizing on GitHub, redirect fails with error
- Error message: "The redirect_uri MUST match the registered callback URL for this application."

**Root Causes**:
- Callback URL in OAuth App doesn't match actual redirect URL
- NEXTAUTH_URL environment variable incorrect
- Development vs production URL mismatch

**Diagnosis**:
```bash
# Check configured callback URL in GitHub OAuth App
gh api /user/applications -q '.[].callback_urls'

# Check NEXTAUTH_URL in deployment
doctl apps logs "$APP_ID" --app-component pulse-hub-web | grep NEXTAUTH_URL

# Compare redirect URL from browser:
# GitHub redirects to: https://pulse-hub-web-xyz.ondigitalocean.app/api/auth/callback/github?code=...
# OAuth App has:      https://pulse-hub-web-abc.ondigitalocean.app/api/auth/callback/github
# ❌ Hash mismatch: xyz ≠ abc
```

**Solutions**:

1. **Update GitHub OAuth App callback URL**:
   - Navigate to GitHub → Settings → Developer settings → OAuth Apps → Pulse-Hub
   - Update "Authorization callback URL" to match actual deployment URL
   - Save changes

2. **Update NEXTAUTH_URL environment variable**:
   ```bash
   # Get actual deployment URL
   ACTUAL_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)

   # Update environment variable
   doctl apps update "$APP_ID" \
     --app-component-name pulse-hub-web \
     --env "NEXTAUTH_URL=$ACTUAL_URL"

   # Redeploy
   doctl apps create-deployment "$APP_ID"
   ```

3. **For development**: Use `http://localhost:3000` for both OAuth App and NEXTAUTH_URL

#### Issue 2: "Invalid Client Credentials" Error

**Symptoms**:
- OAuth flow fails with "401 Unauthorized" error
- Error message: "Client authentication failed due to unknown client, no client authentication included, or unsupported authentication method."

**Root Causes**:
- Client ID or Client Secret incorrect
- Environment variables not set or not loaded
- Using wrong OAuth App (development vs production)

**Diagnosis**:
```bash
# Check if environment variables are set
doctl apps logs "$APP_ID" --app-component pulse-hub-web | grep "GITHUB_OAUTH_CLIENT"
# Should show: GITHUB_OAUTH_CLIENT_ID=Ov23li... (redacted secret)

# Verify Client ID format
echo $GITHUB_OAUTH_CLIENT_ID | wc -c
# Should be 21 characters (20 + newline)

# Test credentials manually
curl -X POST https://github.com/login/oauth/access_token \
  -d "client_id=$GITHUB_OAUTH_CLIENT_ID" \
  -d "client_secret=$GITHUB_OAUTH_CLIENT_SECRET" \
  -d "code=test_code" \
  -H "Accept: application/json"
# Should return error about invalid code (not invalid client)
```

**Solutions**:

1. **Verify credentials in GitHub OAuth App**:
   - Navigate to OAuth App settings
   - Compare Client ID with environment variable
   - If Client Secret lost, generate new one and update environment

2. **Update environment variables**:
   ```bash
   # Re-set credentials
   doctl apps update "$APP_ID" \
     --app-component-name pulse-hub-web \
     --env "GITHUB_OAUTH_CLIENT_ID=<correct-client-id>" \
     --env "GITHUB_OAUTH_CLIENT_SECRET=<correct-client-secret>"

   # Redeploy
   doctl apps create-deployment "$APP_ID"
   ```

3. **Check for typos**: Ensure no extra spaces, quotes, or newlines in credentials

#### Issue 3: "Insufficient Scopes" Error

**Symptoms**:
- Can login successfully, but API calls fail with 403 Forbidden
- Error message: "Resource not accessible by integration" or "Requires authentication"

**Root Causes**:
- Requested scopes don't include required permissions
- User denied certain scopes during authorization
- Scope configuration changed but user hasn't re-authorized

**Diagnosis**:
```bash
# Check requested scopes in code
grep -r "scope:" lib/auth.ts
# Should show: scope: "repo workflow"

# Check granted scopes for user session
# (requires authenticated session token)
curl -H "Authorization: token <user-access-token>" \
  https://api.github.com/
# Response header: X-OAuth-Scopes: repo, workflow

# Compare requested vs granted scopes
```

**Solutions**:

1. **Update requested scopes in code**:
   ```typescript
   // lib/auth.ts
   authorization: {
     params: {
       scope: "repo workflow admin:repo_hook",  // Add required scope
     },
   },
   ```

2. **Force user re-authorization**:
   - User logs out and logs back in
   - Or revoke app authorization in GitHub settings and re-authorize

3. **Verify scope syntax**:
   - Scopes are space-separated (not comma-separated)
   - Use exact scope names from GitHub docs
   - Example: `"repo workflow"` not `"repo, workflow"`

#### Issue 4: Session Expiration Issues

**Symptoms**:
- User logged out unexpectedly
- Session expires too quickly or doesn't expire
- Multiple sessions active simultaneously

**Root Causes**:
- Session timeout configuration incorrect
- Cookie settings (HttpOnly, Secure, SameSite) misconfigured
- Database session storage issues (if using database sessions)

**Diagnosis**:
```bash
# Check session configuration
grep -r "session:" lib/auth.ts
# Should show session strategy and maxAge

# Check cookie settings in browser DevTools
# Application → Cookies → next-auth.session-token
# Verify: HttpOnly=true, Secure=true, SameSite=Lax
```

**Solutions**:

1. **Configure session timeout**:
   ```typescript
   // lib/auth.ts
   export const authOptions = {
     session: {
       strategy: "jwt",  // or "database"
       maxAge: 30 * 24 * 60 * 60,  // 30 days in seconds
     },
   };
   ```

2. **Fix cookie settings**:
   ```typescript
   // lib/auth.ts
   export const authOptions = {
     cookies: {
       sessionToken: {
         name: "next-auth.session-token",
         options: {
           httpOnly: true,
           sameSite: "lax",
           path: "/",
           secure: process.env.NODE_ENV === "production",
         },
       },
     },
   };
   ```

3. **Clear existing sessions**:
   ```bash
   # If using database sessions, clear old sessions
   psql "$POSTGRES_URL" -c "DELETE FROM sessions WHERE expires < NOW();"
   ```

### Debug Mode

Enable NextAuth.js debug logging:

```bash
# Development (.env.local)
NEXTAUTH_DEBUG=true

# Production (DigitalOcean)
doctl apps update "$APP_ID" \
  --app-component-name pulse-hub-web \
  --env "NEXTAUTH_DEBUG=true"
```

View debug logs:
```bash
# Development
npm run dev
# Check console for [next-auth] debug messages

# Production
doctl apps logs "$APP_ID" --app-component pulse-hub-web --follow | grep "next-auth"
```

---

## Security Best Practices

### 1. Secret Management

**Never commit secrets to git**:
```bash
# Add to .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore
echo "*.secret" >> .gitignore

# Verify no secrets in git history
git log -p | grep -E "GITHUB_OAUTH_CLIENT_SECRET|NEXTAUTH_SECRET"
# Should return nothing
```

**Use environment variables**:
```bash
# ✅ Good: Load from environment
const clientSecret = process.env.GITHUB_OAUTH_CLIENT_SECRET;

# ❌ Bad: Hardcoded secret
const clientSecret = "1234567890abcdef...";
```

**Rotate secrets regularly**:
```bash
# Generate new Client Secret in GitHub OAuth App
# Update environment variable
# Deploy changes
# Revoke old secret after verification
```

### 2. Scope Minimization

**Request only required scopes**:
```typescript
// ✅ Good: Minimal scopes
scope: "repo:status workflow"

// ❌ Bad: Excessive scopes
scope: "repo admin:org admin:repo_hook delete_repo"
```

**Explain scope usage to users**:
```typescript
// lib/auth.ts - Add custom authorization page
authorization: {
  params: {
    scope: "repo workflow",
  },
  url: "/auth/github-authorization",  // Custom page explaining scopes
},
```

### 3. HTTPS Enforcement

**Production must use HTTPS**:
```typescript
// lib/auth.ts
if (process.env.NODE_ENV === "production" && !process.env.NEXTAUTH_URL?.startsWith("https://")) {
  throw new Error("NEXTAUTH_URL must use HTTPS in production");
}
```

**Secure cookie settings**:
```typescript
cookies: {
  sessionToken: {
    options: {
      secure: process.env.NODE_ENV === "production",  // HTTPS only in production
      httpOnly: true,  // Prevent JavaScript access
      sameSite: "lax",  // CSRF protection
    },
  },
},
```

### 4. State Parameter Validation

NextAuth.js automatically handles CSRF protection via state parameter. Verify it's enabled:

```typescript
// lib/auth.ts
export const authOptions = {
  // State parameter is automatically generated and validated
  // No additional configuration needed
};
```

### 5. Token Storage

**Never expose access tokens to frontend**:
```typescript
// ✅ Good: Store in server-side session
import { getServerSession } from "next-auth";

export async function GET(req: Request) {
  const session = await getServerSession(authOptions);
  const accessToken = session?.accessToken;  // Server-side only
  // Use token to call GitHub API
}

// ❌ Bad: Expose in client component
"use client";
export default function Component() {
  const session = useSession();
  const accessToken = session.data?.accessToken;  // ❌ Exposed to browser
}
```

**Use short-lived tokens**:
- GitHub access tokens don't expire by default
- Consider implementing token refresh logic
- Revoke tokens when no longer needed

### 6. Rate Limiting

**Implement login attempt rate limiting**:
```typescript
// middleware.ts
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "1 h"),  // 10 attempts per hour
});

export async function middleware(request: Request) {
  if (request.nextUrl.pathname.startsWith("/api/auth/signin")) {
    const ip = request.headers.get("x-forwarded-for");
    const { success } = await ratelimit.limit(ip);

    if (!success) {
      return new Response("Too many login attempts", { status: 429 });
    }
  }
}
```

---

## Advanced Topics

### Multiple OAuth Providers

Add additional authentication providers alongside GitHub:

```typescript
// lib/auth.ts
import GitHubProvider from "next-auth/providers/github";
import GoogleProvider from "next-auth/providers/google";
import EmailProvider from "next-auth/providers/email";

export const authOptions = {
  providers: [
    GitHubProvider({
      clientId: process.env.GITHUB_OAUTH_CLIENT_ID!,
      clientSecret: process.env.GITHUB_OAUTH_CLIENT_SECRET!,
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    EmailProvider({
      server: process.env.EMAIL_SERVER,
      from: process.env.EMAIL_FROM,
    }),
  ],
};
```

### Custom Callback Handling

Customize OAuth callback behavior:

```typescript
// lib/auth.ts
export const authOptions = {
  callbacks: {
    async signIn({ user, account, profile }) {
      // Allow only specific organizations
      if (account.provider === "github") {
        const orgs = profile.organizations_url;  // Fetch user orgs
        // Check if user is in allowed organizations
        return true;  // or false to deny access
      }
      return true;
    },

    async jwt({ token, account, profile }) {
      // Store GitHub access token in JWT
      if (account) {
        token.accessToken = account.access_token;
        token.githubId = profile.id;
      }
      return token;
    },

    async session({ session, token }) {
      // Make access token available in session (server-side only)
      session.accessToken = token.accessToken;
      session.user.githubId = token.githubId;
      return session;
    },
  },
};
```

### GitHub App vs OAuth App

**OAuth App** (current setup):
- Simpler to set up
- User-level access
- Lower rate limits (5000 requests/hour per user)
- Best for small to medium projects

**GitHub App**:
- More complex setup
- App-level access (can act on behalf of users or as app)
- Higher rate limits (15000 requests/hour)
- Webhook support
- Best for large-scale integrations

**Migration guide** (OAuth App → GitHub App):

1. Create GitHub App in Settings → Developer settings → GitHub Apps
2. Configure permissions and events
3. Install app to organization/repositories
4. Update code to use GitHub App authentication:
   ```typescript
   import { App } from "@octokit/app";

   const app = new App({
     appId: process.env.GITHUB_APP_ID,
     privateKey: process.env.GITHUB_APP_PRIVATE_KEY,
   });

   const installationToken = await app.getInstallationAccessToken({
     installationId: INSTALLATION_ID,
   });
   ```

### Token Refresh

GitHub OAuth tokens don't expire, but you can implement manual refresh:

```typescript
// lib/github.ts
export async function refreshGitHubToken(refreshToken: string) {
  const response = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: process.env.GITHUB_OAUTH_CLIENT_ID,
      client_secret: process.env.GITHUB_OAUTH_CLIENT_SECRET,
      grant_type: "refresh_token",
      refresh_token: refreshToken,
    }),
  });

  const data = await response.json();
  return data.access_token;
}
```

### Webhook Integration

Use GitHub webhooks to receive real-time updates:

```typescript
// app/api/webhooks/github/route.ts
import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

export async function POST(req: NextRequest) {
  const payload = await req.text();
  const signature = req.headers.get("x-hub-signature-256");

  // Verify webhook signature
  const secret = process.env.GITHUB_WEBHOOK_SECRET;
  const hmac = crypto.createHmac("sha256", secret);
  const digest = `sha256=${hmac.update(payload).digest("hex")}`;

  if (signature !== digest) {
    return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
  }

  // Process webhook event
  const event = JSON.parse(payload);
  console.log("Received webhook:", event);

  return NextResponse.json({ received: true });
}
```

---

## Appendix

### A. Environment Variables Reference

| Variable | Required | Default | Example |
|----------|----------|---------|---------|
| `GITHUB_OAUTH_CLIENT_ID` | ✅ Yes | - | `Ov23liABC123XYZ789` |
| `GITHUB_OAUTH_CLIENT_SECRET` | ✅ Yes | - | `1234567890abcdef...` |
| `NEXTAUTH_URL` | ✅ Yes | - | `https://pulse-hub-web-abc.ondigitalocean.app` |
| `NEXTAUTH_SECRET` | ✅ Yes | - | `<32-char-random-string>` |
| `NEXTAUTH_DEBUG` | ❌ No | `false` | `true` (development only) |

### B. OAuth Scopes Reference

Full list of GitHub OAuth scopes: https://docs.github.com/en/developers/apps/scopes-for-oauth-apps

**Most commonly used**:

| Scope | Description | Use Case |
|-------|-------------|----------|
| `repo` | Full repository access | Read/write code, issues, PRs |
| `repo:status` | Commit status access | CI/CD status checks |
| `public_repo` | Public repository access | Public repos only (more restrictive) |
| `workflow` | GitHub Actions | Manage workflows and runs |
| `read:org` | Organization membership | Read org membership |
| `write:org` | Organization management | Manage org settings |
| `admin:repo_hook` | Webhooks | Create/manage webhooks |

### C. Useful Links

- **NextAuth.js GitHub Provider**: https://next-auth.js.org/providers/github
- **GitHub OAuth Documentation**: https://docs.github.com/en/developers/apps/oauth-apps
- **GitHub API Scopes**: https://docs.github.com/en/developers/apps/scopes-for-oauth-apps
- **OAuth 2.0 Specification**: https://oauth.net/2/
- **DigitalOcean App Platform**: https://docs.digitalocean.com/products/app-platform/

### D. Troubleshooting Checklist

**Before deployment**:
- [ ] GitHub OAuth App created
- [ ] Client ID and Secret saved securely
- [ ] Callback URL matches deployment URL
- [ ] Environment variables configured
- [ ] NextAuth secret generated (32+ characters)
- [ ] Scopes configured correctly

**After deployment**:
- [ ] HTTPS enforced (production)
- [ ] OAuth flow completes successfully
- [ ] Session persists after page refresh
- [ ] API calls work with granted scopes
- [ ] Logout clears session correctly
- [ ] No secrets in git history
- [ ] Rate limiting configured

---

**Document Revision History**:

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-01 | Pulse-Hub Team | Initial release |
