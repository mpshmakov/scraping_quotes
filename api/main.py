from datetime import timedelta
import json
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import httpx
from starlette import status
import requests


from pydantic import BaseModel
from sqlalchemy import select, update
import stripe
import uvicorn
from api import auth
from configuration import get_configuration
from database.operations import executeOrmStatement, getModelFromTablename, getUserStripeId, toggleAccessForUser, updateStripeIdForUser
from database.schema import Authors, Quotes, Tags, QuotesTagsLink, Users
from fastapi.security import OAuth2PasswordBearer
from database.apilogclass import log
from . import domain, port
from secret import stripe_api_key, stripe_webhook_secret

app = FastAPI()
app.mount("/static", StaticFiles(directory="api/frontend"), name="static")
app.include_router(auth.router)
user_dependency = Annotated[dict, Depends(auth.get_current_user)]
stripe.api_key = stripe_api_key



def check_auth_and_access(user):
    print("check",user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed.')
    if user['access'] == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access check failed.")

@app.patch("/user/toggle_access")
async def toggle_current_user_access(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed.')    
    print(user)
    access = toggleAccessForUser(user['id'])
    async with httpx.AsyncClient() as client:
        print('before res')
        res = await client.post(domain + '/auth/token', json={"email":user['email'], "id":user['id'], "access":access})
        print("res", res.json())
        res = res.json()
        res["access"] = access
        log.info(user['email'], f"Set user's access to {access}")
        return res
    
# # redirect version -> returns 403 forbidden for some reason.
# @app.post("/subscription", response_class=RedirectResponse)
# async def pay_for_subscription(user: user_dependency):
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             line_items=[
#                 {
#                     # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
#                     'price': 'price_1QT1cyF14yvMq6vJlWtCtg6y',
#                     'quantity': 1,
#                 },
#             ],
#             mode='subscription',
#             success_url= domain + '/success.html',
#             cancel_url= domain + '/cancel.html',
#         )
#         print("done")
#         print(checkout_session.url)
#     except Exception as e:
#         return str(e)

#     return str(checkout_session.url)

@app.post("/stripe_webhook")
async def handle_stripe_webhook(request: Request):
    # print("received stripe webhook")

    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_webhook_secret
        )
    except ValueError as e:
        return HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        return HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # print(payment_intent)
        print("event", event)
        print("PaymentIntent was successful!")
        toggleAccessForUser(user_id=None, stripe_id=payment_intent['customer'], access=True)
    elif event['type'] == 'payment_intent.payment_failed':
        print("failed")

    return {"status": "success"}

@app.post("/subscription")
async def pay_for_subscription(user: user_dependency):
    try:
        res = getUserStripeId(user['id'])
        print(res)
        if res is None:
            stripe_customer = stripe.Customer.create(email=user['email'])
            updateStripeIdForUser(user['id'], stripe_customer.id)
            res = stripe_customer.id
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1QT1cyF14yvMq6vJlWtCtg6y',
                    'quantity': 1,
                },
            ],
            customer=res, 
            mode='subscription',
            success_url= domain + '/static/success.html',
            cancel_url= domain + '/static/cancel.html',
            
        )
        print("done")
        print(checkout_session.url)
    except Exception as e:
        return str(e)

    return {"url":str(checkout_session.url)}

def fulfill_checkout(session_id):
  print("Fulfilling Checkout Session", session_id)

  # TODO: Make this function safe to run multiple times,
  # even concurrently, with the same session ID

  # TODO: Make sure fulfillment hasn't already been
  # peformed for this Checkout Session

  # Retrieve the Checkout Session from the API with line_items expanded
  checkout_session = stripe.checkout.Session.retrieve(
    session_id,
    expand=['line_items'],
  )

  # Check the Checkout Session's payment_status property
  # to determine if fulfillment should be peformed
  if checkout_session.payment_status != 'unpaid':
    pass
    # TODO: Perform fulfillment of the line items

    # TODO: Record/save fulfillment status for this
    # Checkout Session

# redirect test
@app.get("/typer", response_class=RedirectResponse)
async def redirect_typer():
    return "https://typer.tiangolo.com"

@app.get("/")
def root(user: user_dependency):
    check_auth_and_access(user)
    return {"User": user}

# get data from db
# @app.get("/{table}")
# def get_quotes(table: str):
#     model = getModelFromTablename(table)
#     res = executeOrmStatement(select(model))
#     # quotes = []
#     # for quote in res.all():
#     #     quotes.append({"quote_uuid" : quote.Quotes.id, "quote_text" :quote.Quotes.text, "quote_author" :quote.Quotes.author})

    # return quotes

@app.get("/quotes")
def get_quotes(user: user_dependency):
    print(user)
    check_auth_and_access(user)
    res = executeOrmStatement(select(Quotes))
    quotes = []
    for quote in res.all():
        quotes.append({"quote_uuid" : quote.Quotes.id, "quote_text" :quote.Quotes.text, "quote_author" :quote.Quotes.author})
    log.info(user['email'], "Retrieved quotes.")
    return quotes

@app.get("/tags")
def get_tags(user: user_dependency):
    check_auth_and_access(user)
    res = executeOrmStatement(select(Tags))
    tags = []
    for tag in res.all():
        tags.append({"0" : tag.Tags.tag}) # matching how to_dict converts dataframe to dict
    log.info(user['email'], "Retrieved tags.")    
    return tags

@app.get("/quotes_tags_link")
def get_quotes_tags_link(user: user_dependency):
    check_auth_and_access(user)
    res = executeOrmStatement(select(QuotesTagsLink))
    quotes_tags_link = []
    for link in res.all():
        quotes_tags_link.append({"quote_uuid" : link.QuotesTagsLink.quote_id, "tag" : link.QuotesTagsLink.tag}) # matching how to_dict converts dataframe to dict
    log.info(user['email'], "Retrieved quotes_tags_link.")
    return quotes_tags_link

@app.get("/authors")
def get_authors(user: user_dependency):
    check_auth_and_access(user)
    res = executeOrmStatement(select(Authors))
    authors = []
    for author in res.all():
        authors.append({"author" : author.Authors.author, "about" : author.Authors.about}) 
    log.info(user['email'], "Retrieved authors.")
    return authors




# get data from json

# @app.get("/quotes")
# def get_quotes():
#     json_filename, json_path = get_configuration(["json_filename", "save_data_path"])
#     with open(f'{json_path}/{json_filename}.json', 'r') as file:
#         data = json.load(file)

#     return data["quotes"]


if __name__ == "__main__":
    uvicorn.run("api.main:app", port=port, reload=True)