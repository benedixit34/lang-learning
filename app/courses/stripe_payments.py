from supabase import create_client
from django.conf import settings
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


def get_user_stripe_customer(user):
    result = supabase.schema('stripe').table('customers').select("*").eq("email", str(user.email)).execute()
    return result.data[0] if result.data else None


def get_user_active_subscriptions(user):
    customer = get_user_stripe_customer(user)
    if not customer:
        return []

    
    now_iso = datetime.utcnow().isoformat()

    subscriptions = (
        supabase.schema("stripe").table("subscriptions")
        .select("*")
        .eq("customer", customer["id"])
        .gte("end_date", now_iso) 
        .execute()
    )
    return subscriptions.data

def get_active_products():
    products = supabase.schema("stripe").table("products").select("*").eq("active", True).execute()
    return products.data

def get_product_prices(product_id):
    prices = supabase.schema("stripe").table("prices").select("*").eq("product", product_id).eq("active", True).execute()
    return prices.data
