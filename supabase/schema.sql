-- Supabase schema for API-Factory backup persistence.
-- Apply with the Supabase SQL editor or `psql` against the project database.

create schema if not exists public;

create table if not exists public.api_key_metadata (
    id text primary key,
    owner text,
    tier text,
    is_admin text,
    quota text,
    usage text,
    disabled text,
    updated_at timestamptz default now()
);

create index if not exists idx_api_key_metadata_owner on public.api_key_metadata (owner);
create index if not exists idx_api_key_metadata_disabled on public.api_key_metadata (disabled);

create table if not exists public.audit_entries (
    entry_hash text primary key,
    timestamp timestamptz not null,
    action text not null,
    user_id text not null,
    resource_id text not null,
    details jsonb not null,
    previous_hash text
);

create index if not exists idx_audit_entries_user_id on public.audit_entries (user_id);
create index if not exists idx_audit_entries_resource_id on public.audit_entries (resource_id);
create index if not exists idx_audit_entries_timestamp on public.audit_entries (timestamp);

create table if not exists public.retention_records (
    data_id text primary key,
    category text not null,
    policy text not null,
    created_at timestamptz not null,
    justification text,
    delete_after timestamptz not null,
    last_persisted_at timestamptz default now()
);

create index if not exists idx_retention_records_category on public.retention_records (category);
create index if not exists idx_retention_records_delete_after on public.retention_records (delete_after);
