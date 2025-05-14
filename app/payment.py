import requests
import json
import os
import aiohttp

api_key = os.getenv("PTOKEN")
webhook = os.getenv("PAYMENT_WEBHOOK")


async def create_payping_payment(
    amount, description="nedaai payments", phone=None, is_test=False, chat_id=None
):
    """
    Creates a payment request to PayPing.
    Args:
        amount (float): The amount to be paid.
        description (str): A description of the payment.
        phone (str): The phone number associated with the payment.
    Returns:
        dict: The response from the PayPing API as a JSON object.
    """
    try:
        url = "https://wallet.pixiee.io/api/v1/apps/payping/purchases/"

        if chat_id:
            webhook = dict(
                webhook_url="https://n8n.inbeet.tech/webhook-test/nedaai-payments?chat_id="
                + chat_id
            )
        else:
            webhook = dict()

        payload = json.dumps(
            {
                "user_id": "785cf071-1dca-49d0-b0ef-d7de5baf4e8f",
                "wallet_id": "c75ed09b-d2ae-43e9-ba3e-88a12ca515d4",
                "amount": amount,
                "description": description,
                "callback_url": "https://t.me/nedaaibot",
                "phone": phone,
                "is_test": is_test,
            }
            | webhook
        )

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                result = await response.json()
                return result["uid"]

    except aiohttp.ClientError as e:
        print(f"Network error occurred: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        raise


async def get_payment_status(payment_id):
    try:
        url = "https://wallet.pixiee.io/api/v1/apps/payping/purchases/" + payment_id
        headers = {"x-api-key": api_key, "Accept-Encoding": "Identical"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()

    except aiohttp.ClientError as e:
        print(f"Network error occurred while getting payment status: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error occurred while getting payment status: {str(e)}")
        raise
