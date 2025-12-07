# Testing Guide for Client-Only Google Sign-In

This guide explains how to test the client-only Google Sign-In feature and the updated CI workflow.

## Prerequisites

1. Google Cloud Console account
2. Node.js 18+ installed
3. Access to repository settings (for CI testing)

## Part 1: Testing Client-Only Google Sign-In

### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Navigate to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth 2.0 Client ID**
5. Configure the OAuth consent screen if prompted:
   - User Type: External (for testing)
   - App name: Your app name
   - User support email: Your email
   - Developer contact: Your email
6. For Application type, select **Web application**
7. Add **Authorized JavaScript origins**:
   - `http://localhost:3000` (for development)
   - `http://localhost:3001` (if using different port)
8. Copy the **Client ID** (looks like: `123456789-abcdefg.apps.googleusercontent.com`)

### Step 2: Configure Frontend

```bash
cd frontend

# Copy environment file
cp .env.example .env

# Edit .env and add your Google Client ID
nano .env  # or use your preferred editor
```

Add this line to `.env`:
```
REACT_APP_GOOGLE_CLIENT_ID=your-actual-client-id-here
```

**Important:** Make sure to replace `your-actual-client-id-here` with the actual Client ID from Step 1.

### Step 3: Run the Application

```bash
# Install dependencies (if not already done)
npm install

# Start the development server
npm start
```

The app should open at `http://localhost:3000`

### Step 4: Test Google Sign-In

1. Navigate to the login page (`/login` or click "Sign In")
2. You should see a warning message: "⚠️ Running in client-only mode (demo)"
3. Click the **Sign in with Google** button
4. Select your Google account
5. You should be redirected to the home page
6. Check the browser's localStorage to see stored user data:
   ```javascript
   // Open browser console (F12) and run:
   localStorage.getItem('google_user')
   localStorage.getItem('google_token')
   ```

### Step 5: Test Standalone HTML Page

For a simpler test without running the full React app:

1. Open `frontend/public/test-google-auth.html` in a text editor
2. Replace `YOUR_GOOGLE_CLIENT_ID` with your actual Client ID
3. Serve the file using a local web server:
   ```bash
   # From the frontend/public directory
   python -m http.server 8080
   # or
   npx serve
   ```
4. Open `http://localhost:8080/test-google-auth.html` in your browser
5. Click "Sign in with Google"
6. After signing in, you should see your profile information

### What to Verify

- ✅ Google Sign-In button appears correctly
- ✅ Clicking the button opens Google's authentication popup
- ✅ After authentication, user data is stored in localStorage
- ✅ User profile information is displayed correctly
- ✅ "Sign Out" functionality clears localStorage
- ✅ No JavaScript errors in browser console
- ✅ Warning message appears indicating client-only mode

## Part 2: Testing CI Workflow Changes

### Test Scenario 1: With SUPABASE_DATABASE_URL Secret

1. Go to your repository on GitHub
2. Navigate to **Settings > Secrets and variables > Actions**
3. Add a new repository secret:
   - Name: `SUPABASE_DATABASE_URL`
   - Value: A valid PostgreSQL connection string (or a test value)
4. Trigger the workflow:
   ```bash
   # Make a change to trigger the workflow
   echo "# Test" >> migrations/test.sql
   git add migrations/test.sql
   git commit -m "Test: trigger migration workflow"
   git push origin main
   ```
5. Go to **Actions** tab and watch the workflow run
6. **Expected Result:** 
   - ✅ Workflow runs all steps successfully
   - ✅ PostgreSQL client is installed
   - ✅ Database connection is verified
   - ✅ Migrations are executed

### Test Scenario 2: Without SUPABASE_DATABASE_URL Secret

1. Go to **Settings > Secrets and variables > Actions**
2. Delete the `SUPABASE_DATABASE_URL` secret (or rename it temporarily)
3. Trigger the workflow again:
   ```bash
   echo "# Test 2" >> README.md
   git add README.md
   git commit -m "Test: workflow without DB secret"
   git push origin main
   ```
4. Go to **Actions** tab and watch the workflow run
5. **Expected Result:**
   - ✅ Workflow completes successfully (does NOT fail)
   - ⚠️ Warning message: "SUPABASE_DATABASE_URL secret is not set!"
   - ⚠️ Message: "Database migration steps will be SKIPPED."
   - ✅ PostgreSQL client installation is skipped
   - ✅ Database connection check is skipped
   - ✅ Migration execution is skipped
   - ✅ Migration summary shows "SKIPPED" status

### What to Verify in CI

- ✅ Workflow runs without errors when secret is missing
- ✅ Clear warning messages are displayed
- ✅ Steps are properly skipped (not failed)
- ✅ Summary page shows correct status
- ✅ No sensitive information is exposed in logs

## Part 3: Manual Verification Checklist

### Code Quality
- [ ] All code follows existing patterns in the repository
- [ ] No console.log statements in production code (except error logging)
- [ ] Environment variables are properly documented
- [ ] No hardcoded secrets or credentials

### Security
- [ ] JWT tokens are validated before parsing
- [ ] User input is sanitized (no XSS vulnerabilities)
- [ ] Sensitive data is not logged in production
- [ ] localStorage is used only for demo purposes (documented)
- [ ] No secrets committed to repository

### Functionality
- [ ] Google Sign-In works in client-only mode
- [ ] Fallback to Supabase works when GOOGLE_CLIENT_ID is not set
- [ ] Sign out functionality clears all stored data
- [ ] CI workflow handles missing secrets gracefully
- [ ] Documentation is clear and accurate

### User Experience
- [ ] Clear warning message in client-only mode
- [ ] Intuitive button placement and styling
- [ ] Error messages are user-friendly
- [ ] Loading states are handled (if applicable)

## Troubleshooting

### Issue: Google Sign-In button doesn't appear

**Solutions:**
1. Check browser console for errors
2. Verify REACT_APP_GOOGLE_CLIENT_ID is set correctly in .env
3. Make sure the value is not the placeholder "your-google-client-id-here"
4. Restart the development server after changing .env

### Issue: "Redirect URI mismatch" error

**Solutions:**
1. Go to Google Cloud Console
2. Navigate to your OAuth credentials
3. Add the correct origin (e.g., `http://localhost:3000`) to Authorized JavaScript origins
4. Wait a few minutes for changes to propagate

### Issue: CI workflow still fails without secret

**Solutions:**
1. Check the workflow file has the correct conditional logic
2. Verify the step IDs match (`steps.check_db_url.outputs.db_url_configured`)
3. Make sure you're testing on the correct branch

### Issue: User data not persisting

**Solutions:**
1. Check browser's localStorage in DevTools
2. Verify no errors in console during sign-in
3. Check that browser allows localStorage (not in private/incognito mode)

## Additional Notes

### Security Considerations

**Client-Only Mode is for Demo/Testing Only:**
- ID tokens are not verified server-side
- User data is stored in browser localStorage
- No database persistence
- For production, always verify tokens on the server

**Best Practices for Production:**
1. Verify Google ID tokens on your backend server
2. Store user data in a secure database
3. Use secure, httpOnly cookies for sessions
4. Implement proper CSRF protection
5. Use HTTPS in production

### Environment Variables

**Frontend (.env):**
```bash
# Optional - enables client-only mode
REACT_APP_GOOGLE_CLIENT_ID=your-client-id

# Required for Supabase mode (if not using client-only)
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
REACT_APP_API_URL=http://localhost:3001/api
```

**GitHub Secrets:**
```
SUPABASE_DATABASE_URL (optional)
SUPABASE_SERVICE_ROLE_KEY (optional)
```

## Success Criteria

Your implementation is working correctly if:

1. ✅ Frontend builds without errors
2. ✅ Google Sign-In works with valid Client ID
3. ✅ User can sign in and see their profile
4. ✅ User can sign out successfully
5. ✅ CI workflow passes with or without DB secret
6. ✅ Clear warnings are shown in both client-only mode and CI
7. ✅ No security vulnerabilities detected
8. ✅ Documentation is clear and complete

## Support

If you encounter issues not covered in this guide:
1. Check the browser console for error messages
2. Review GitHub Actions logs for workflow issues
3. Verify all environment variables are set correctly
4. Consult Google Cloud Console OAuth documentation
5. Check that all authorized origins are configured
