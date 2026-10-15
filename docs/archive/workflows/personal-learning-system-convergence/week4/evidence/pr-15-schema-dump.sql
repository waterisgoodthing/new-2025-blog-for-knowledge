                          Table "public.webauthn_challenges"
     Column     |           Type           | Collation | Nullable |      Default      
----------------+--------------------------+-----------+----------+-------------------
 id             | uuid                     |           | not null | gen_random_uuid()
 challenge      | character varying(128)   |           | not null | 
 challenge_hash | character varying(64)    |           | not null | 
 purpose        | character varying(32)    |           | not null | 
 session_id     | character varying(255)   |           |          | 
 user_id        | uuid                     |           |          | 
 created_at     | timestamp with time zone |           | not null | now()
 expires_at     | timestamp with time zone |           | not null | 
 consumed_at    | timestamp with time zone |           |          | 
Indexes:
    "webauthn_challenges_pkey" PRIMARY KEY, btree (id)
    "idx_webauthn_challenges_challenge_hash" btree (challenge_hash)
    "idx_webauthn_challenges_expires" btree (expires_at) WHERE consumed_at IS NULL
    "idx_webauthn_challenges_purpose_session" btree (purpose, session_id) WHERE session_id IS NOT NULL
    "idx_webauthn_challenges_purpose_user" btree (purpose, user_id) WHERE user_id IS NOT NULL
Check constraints:
    "ck_webauthn_challenges_purpose" CHECK (purpose::text = ANY (ARRAY['registration'::character varying, 'authentication'::character varying, 'operator_registration'::character varying]::text[]))
Foreign-key constraints:
    "fk_webauthn_challenges_user_id" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

