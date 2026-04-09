from supabase_client import get_all_users
users = get_all_users()
print('Usuários encontrados:')
for user in users:
    print(f'  Email: {user.get("email")}, Admin: {user.get("is_admin", False)}')