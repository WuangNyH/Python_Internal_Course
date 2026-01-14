class JwtClaims:

    # ===== Standard JWT =====
    SUBJECT = "sub" # user_id
    ISSUER = "iss"
    AUDIENCE = "aud"
    ISSUED_AT = "iat"
    EXPIRES_AT = "exp"

    # ===== Custom / domain =====
    TOKEN_VERSION = "tv" # token_version (revoke-all)
    TENANT_ID = "tid" # multi-tenant
