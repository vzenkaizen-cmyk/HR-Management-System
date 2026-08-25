# HR Training Dashboard

A Streamlit application for logging and visualizing training programmes
(hours, cost, participants, technical vs. soft-skill split) with sign-up/login
authentication and a PostgreSQL (Neon) backend.

## Features
- **Sign up / log in** with bcrypt-hashed passwords (no plaintext ever stored)
- **Role-based access**: `admin` can delete records and manage users; `user` can add/edit
- **Dashboard**: KPI cards, hours/programme-count trend, Technical vs Soft Skill split,
  cost-by-location, top programmes — all filterable by location, year, month, type
- **Data Entry**: validated form, auto-calculated total hours
- **Records**: searchable table, CSV export, inline edit/delete
- **Excel migration script** to one-time import your existing training log

## Project structure
```
hr-training-dashboard/
├── app.py                     # login/signup gate + landing page
├── requirements.txt
├── migrate_excel.py            # one-time import of your existing xlsx
├── .streamlit/
│   ├── config.toml             # dark theme
│   └── secrets.toml.example    # copy to secrets.toml, fill in your Neon URL
├── database/db.py              # SQLAlchemy engine + schema + init
├── auth/auth.py                # signup/login/session/password logic
├── utils/styles.py             # shared CSS + KPI card component
├── utils/helpers.py            # data access for training_records
└── pages/
    ├── 1_📊_Dashboard.py
    ├── 2_📝_Data_Entry.py
    ├── 3_📁_Records.py
    └── 4_⚙️_My_Account.py
```

## 1. Set up the database (Neon)
1. Create a free project at https://neon.tech
2. Copy the pooled connection string (Dashboard → **Connect** → psql / connection string).
   It should look like:
   `postgresql://user:password@ep-xxxx.neon.tech/dbname?sslmode=require`
3. You do **not** need to run any SQL yourself — `init_db()` creates the tables
   automatically the first time the app starts.

## 2. Local setup
```bash
git clone <your-repo-url>
cd hr-training-dashboard
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Add your secrets
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# then edit .streamlit/secrets.toml with your Neon URL and a temporary admin password

streamlit run app.py
```
Log in with the `first_admin_*` credentials you set in `secrets.toml` on first run,
then change the password from **My Account**. You can blank out the
`first_admin_*` values afterwards — they're only used when the `users` table is empty.

## 3. Import your existing Excel log (optional, one-time)
```bash
python migrate_excel.py "HR_T___A.xlsx" admin
```
(replace `admin` with whatever username you logged in with)

## 4. Put the code on GitHub
```bash
git init
git add .
git commit -m "Initial commit: HR training dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/hr-training-dashboard.git
git push -u origin main
```
`.gitignore` already excludes `secrets.toml` and any `.xlsx` files, so your
credentials and raw HR data never get pushed to GitHub.

## 5. Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io → **New app**
2. Pick your GitHub repo, branch `main`, main file `app.py`
3. Under **Advanced settings → Secrets**, paste the same content as your
   local `.streamlit/secrets.toml` (with your real Neon URL and a strong
   first-admin password)
4. Click **Deploy**

Every `git push` to `main` afterwards will auto-redeploy the app.

## Notes on security
- Passwords are hashed with `bcrypt`; the app never stores or logs plaintext passwords.
- `secrets.toml` (local) and the Streamlit Cloud **Secrets** panel are the only
  places your database URL and first-admin password should ever live.
- Consider disabling/removing the `first_admin_*` values in secrets once you've
  created your real admin account and additional users.
