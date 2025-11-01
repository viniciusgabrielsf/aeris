# OpenAQ API Key Setup Guide

## Why Do I Need an API Key?

OpenAQ v3 API requires authentication via API key. **Don't worry - it's completely FREE!**

OpenAQ v1 and v2 were retired on January 31, 2025, and v3 requires authentication for access to air quality data worldwide.

## Step-by-Step Setup (5 minutes)

### Step 1: Register for OpenAQ Account

1. Visit: **https://explore.openaq.org/register**
2. Fill in the registration form:
   - Email address
   - Create a password
   - Accept terms of service
3. Check your email for verification link
4. Click the verification link to activate your account

### Step 2: Get Your API Key

1. Go to: **https://explore.openaq.org**
2. **Sign in** with your credentials
3. Click on your profile/account settings (usually top right corner)
4. Navigate to **API Key** or **Settings** section
5. **Copy your API key** (it will look something like: `abc123def456ghi789jkl012mno345pqr678`)

**⚠️ IMPORTANT**: Treat your API key like a password - don't share it publicly or commit it to Git!

### Step 3: Add API Key to Aeris

1. Create a `.env` file in the project root:
   ```bash
   cd /path/to/aeris
   cp .env.example .env
   ```

2. Open `.env` in your text editor:
   ```bash
   nano .env
   # or
   code .env
   # or
   vim .env
   ```

3. Add your API key:
   ```bash
   OPENAQ_API_KEY=your_actual_api_key_here
   ```

   Example:
   ```bash
   OPENAQ_API_KEY=abc123def456ghi789jkl012mno345pqr678
   ```

4. Save and close the file

### Step 4: Verify Setup

Run the test script to verify your API key works:

```bash
source .venv/bin/activate
python test_collection.py
```

Expected output:
```
✓ API connection successful!
✓ Database initialized
✓ Data collected for São Paulo
...
```

## Troubleshooting

### Error: "API key authentication failed"

**Problem**: Your API key is invalid or not properly configured.

**Solutions**:
1. Double-check you copied the entire API key (no spaces, no line breaks)
2. Verify the key in your `.env` file matches the key from OpenAQ
3. Make sure `.env` file is in the project root directory
4. Restart your Python session after updating `.env`

### Error: "OpenAQ API key not configured"

**Problem**: The `.env` file doesn't exist or the key is not set.

**Solutions**:
1. Make sure you created `.env` file (not `.env.example`)
2. Check that `OPENAQ_API_KEY=` line exists in `.env`
3. Don't leave the value as `your_api_key_here` - use your actual key

### Error: "Rate limit exceeded"

**Problem**: You've made too many requests in a short time.

**Solutions**:
1. Wait 10-15 minutes before trying again
2. Reduce the number of cities being queried
3. Increase delays between requests in the code

### Error: "No locations returned for BR"

**Problem**: Either the API key is invalid, or there's no data for the query.

**Solutions**:
1. Verify your API key is working with a simple test
2. Try querying by coordinates instead of country code
3. Check OpenAQ status page for service issues

## API Key Best Practices

### ✅ DO:
- Keep your API key in `.env` file (gitignored)
- Use environment variables for configuration
- Treat it like a password - keep it secret
- Regenerate periodically for security

### ❌ DON'T:
- Commit API keys to Git repositories
- Share your key publicly (GitHub, forums, etc.)
- Hardcode keys in source code
- Use the same key across multiple projects

## Rate Limits

OpenAQ v3 free tier has rate limits (exact limits may vary):
- Check the official documentation for current limits
- Implement delays between requests (0.5-1 second)
- Cache responses to reduce API calls
- Use bulk endpoints when possible

## Getting Help

If you encounter issues:

1. **Check Logs**: Look at `data_storage/aeris.log` for detailed error messages
2. **OpenAQ Docs**: https://docs.openaq.org
3. **OpenAQ Support**: Contact through their website
4. **Project Issues**: Open an issue on the Aeris GitHub repository

## Next Steps

Once your API key is configured:

1. ✅ Run `python test_collection.py` to verify setup
2. ✅ Explore the collected data in the database
3. ✅ Start the Streamlit dashboard (coming soon)
4. ✅ Configure automated data collection

---

**Need More Help?**

- OpenAQ Documentation: https://docs.openaq.org
- OpenAQ Register: https://explore.openaq.org/register
- Aeris README: `README.md` in project root
