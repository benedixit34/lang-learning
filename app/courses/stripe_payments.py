from supabase import create_client
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()


supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

def get_user_stripe_customer(user):
    result = supabase.table("stripe_customers").select("*").eq("email", str(user.email)).maybe_single().execute()
    return result.data if result.data else None

def get_user_active_subscriptions(user):
    customer = get_user_stripe_customer(user)
    if not customer:
        return []

    subscriptions = (
        supabase.table("stripe_subscriptions")
        .select("*")
        .eq("customer", customer["id"])
        .eq("status", "active")
        .execute()
    )
    return subscriptions.data

def get_active_products():
    products = supabase.table("stripe_products").select("*").eq("active", True).execute()
    return products.data

def get_product_prices(product_id):
    prices = supabase.table("stripe_prices").select("*").eq("product", product_id).eq("active", True).execute()
    return prices.data
