CREATE TABLE accounts (
    id UUID PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE
);
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY,
    account_id UUID NOT NULL UNIQUE,
    name VARCHAR(255),
    address VARCHAR(255)
);
CREATE INDEX ix_user_profiles_account_id ON user_profiles (account_id);
CREATE TABLE otps (
    session_id UUID PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    attempts_count INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    is_used BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX ix_otps_phone_number ON otps (phone_number);
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY,
    account_id UUID NOT NULL,
    refresh_token VARCHAR(512) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX ix_refresh_tokens_account_id ON refresh_tokens (account_id);
CREATE TABLE courier_profiles (
    id UUID PRIMARY KEY,
    account_id UUID NOT NULL UNIQUE,
    full_name VARCHAR(255),
    inn VARCHAR(12) UNIQUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL DEFAULT 'OFFLINE'
);
CREATE INDEX ix_courier_profiles_account_id ON courier_profiles (account_id);
CREATE INDEX ix_courier_profiles_inn ON courier_profiles (inn);
CREATE TABLE outbox_message (
    id UUID PRIMARY KEY,
    type VARCHAR(512) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 5,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX ix_outbox_message_status ON outbox_message (status);