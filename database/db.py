def _seed_first_admin(engine):
    import bcrypt

    admin_password = "Admin@123"

    password_hash = bcrypt.hashpw(
        admin_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO users
                    (username, email, name, full_name, password_hash, role)
                VALUES
                    (:username, :email, :name, :full_name, :password_hash, 'admin')
                ON CONFLICT (username) DO NOTHING
            """),
            {
                "username": "admin",
                "email": "admin@example.com",
                "name": "System Administrator",
                "full_name": "System Administrator",
                "password_hash": password_hash,
            },
        )
