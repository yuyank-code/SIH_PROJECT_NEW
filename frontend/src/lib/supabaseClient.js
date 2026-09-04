import { createClient } from '@supabase/supabase-js';

// Production-safe browser configuration. These values are intentionally public:
// Supabase publishable keys are designed to be embedded in browser applications.
// Environment variables still override them for local/staging deployments.
const url = process.env.REACT_APP_SUPABASE_URL || 'https://ctgyuiopqokenpfupggy.supabase.co';
const anonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || process.env.REACT_APP_SUPABASE_PUBLISHABLE_KEY || 'sb_publishable_XcIhWdLe73rUy7blJuYsRw_OT-NZV5u';

export const supabase = createClient(url, anonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
