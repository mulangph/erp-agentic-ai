# User Management & Access

## Adding a New User
1. Go to **Admin > Users > New User**.
2. Enter Username, Full Name, and Email Address.
3. Assign an initial Role (e.g., Requester, Approver, Admin).
4. Click **Create User** — the user receives a welcome email with a temporary password.

Note: If self-service user creation is disabled for your company, submitting "add new user" requests through the helpdesk creates a data change request ticket that is applied by an administrator.

## Granting Module Permissions
1. Open the user's profile at **Admin > Users > [User]**.
2. Go to the **Permissions** tab.
3. Select the module (e.g., Purchasing, Inventory, Finance) and the permission level (View, Edit, Approve, Admin).
4. Click **Save Permissions**. Changes take effect immediately after the user's next login.

## Roles vs. Direct Permissions
- **Roles** are permission bundles assigned to many users at once (e.g., "Warehouse Clerk" grants View+Edit on Inventory).
- **Direct Permissions** override role permissions for a specific user and module, useful for one-off exceptions.

## Resetting a Password
Administrators can trigger a password reset from **Admin > Users > [User] > Reset Password**, which emails the user a reset link valid for 24 hours.

## Deactivating a User
Deactivating a user (Admin > Users > [User] > Deactivate) immediately revokes login access but preserves their historical records (POs created, invoices approved, etc.) for audit purposes.

## Common Permission Errors
- **"Access Denied" on a module**: The user's role or direct permissions do not include Edit/View for that module. Check **Permissions** tab.
- **"Approval not available"**: The user has View/Edit but not Approve-level permission on that module.
