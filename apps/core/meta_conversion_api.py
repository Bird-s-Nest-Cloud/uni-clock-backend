"""
Meta Conversion API Service

Sends server-side events to the Meta Graph API for ad tracking and optimization.
Supports event deduplication with the browser-side Meta Pixel via shared event_id values.
"""
import hashlib
import logging
import time
import threading

import requests

from core.models import SiteSettings

logger = logging.getLogger(__name__)

META_GRAPH_API_URL = 'https://graph.facebook.com/v21.0'


def _hash_value(value):
    """Hash a value using SHA-256 as required by Meta Conversion API."""
    if not value:
        return None
    return hashlib.sha256(str(value).strip().lower().encode('utf-8')).hexdigest()


def _build_user_data(user_data):
    """
    Build the user_data payload with proper hashing.

    Accepts raw values; hashes them per Meta requirements.
    Supports both authenticated and guest users.

    Expected keys (all optional):
        email, phone, first_name, last_name, city, state, zip_code,
        country, client_ip_address, client_user_agent, fbc, fbp
    """
    hashed = {}

    # Fields that must be hashed
    hash_fields = {
        'email': 'em',
        'phone': 'ph',
        'first_name': 'fn',
        'last_name': 'ln',
        'city': 'ct',
        'state': 'st',
        'zip_code': 'zp',
        'country': 'country',
    }
    for src_key, dest_key in hash_fields.items():
        val = user_data.get(src_key)
        if val:
            hashed[dest_key] = _hash_value(val)

    # Fields that are NOT hashed
    for key in ('client_ip_address', 'client_user_agent', 'fbc', 'fbp'):
        val = user_data.get(key)
        if val:
            hashed[key] = val

    return hashed


def send_meta_event(event_name, event_id, user_data, custom_data=None):
    """
    Send a server-side event to Meta Conversion API.

    This function runs the actual HTTP call in a background thread so it
    never blocks order creation or any other caller.

    Args:
        event_name: Event name (e.g. "Purchase", "AddToCart", "InitiateCheckout")
        event_id:   Unique ID shared with the browser Pixel for deduplication
        user_data:  Dict of user identifiers (email, phone, ip, user_agent, etc.)
        custom_data: Dict of event-specific data (value, currency, content_ids, etc.)
    """
    try:
        settings = SiteSettings.load()

        if not settings.enable_conversion_api:
            logger.debug('Meta Conversion API is disabled — skipping event "%s"', event_name)
            return

        if not settings.meta_pixel_id or not settings.meta_access_token:
            logger.warning(
                'Meta Conversion API enabled but Pixel ID or Access Token is missing — '
                'skipping event "%s"',
                event_name,
            )
            return

        event_payload = {
            'event_name': event_name,
            'event_time': int(time.time()),
            'event_id': str(event_id),
            'action_source': 'website',
            'user_data': _build_user_data(user_data or {}),
        }

        if custom_data:
            event_payload['custom_data'] = custom_data

        payload = {
            'data': [event_payload],
            'access_token': settings.meta_access_token,
        }

        # Fire in background thread to avoid blocking the caller
        thread = threading.Thread(
            target=_send_event_request,
            args=(settings.meta_pixel_id, payload, event_name, event_id),
            daemon=True,
        )
        thread.start()

    except Exception:
        logger.exception('Failed to prepare Meta Conversion API event "%s"', event_name)


def send_purchase_event_for_order(
    order,
    client_ip_address='',
    client_user_agent='',
    fbc=None,
    fbp=None,
):
    """Build and send a Purchase event from an order instance."""
    shipping_data = _get_order_shipping_data(order)
    event_id = f'purchase_{order.order_number}'

    user_data = {
        'email': _get_order_email(order),
        'phone': _get_order_phone(order),
        'first_name': _get_order_first_name(order),
        'last_name': _get_order_last_name(order),
        'city': shipping_data.get('city'),
        'state': shipping_data.get('state'),
        'zip_code': shipping_data.get('postal_code'),
        'country': shipping_data.get('country'),
        'client_ip_address': client_ip_address,
        'client_user_agent': client_user_agent,
        'fbc': fbc,
        'fbp': fbp,
    }

    custom_data = {
        'currency': 'BDT',
        'value': float(order.total_price),
        'order_id': order.order_number,
        'content_type': 'product',
        'content_ids': [str(item.product_id) for item in order.items.all() if item.product_id],
        'contents': [
            {
                'id': str(item.product_id),
                'quantity': item.quantity,
                'item_price': float(item.unit_price),
            }
            for item in order.items.all() if item.product_id
        ],
        'num_items': order.get_total_items(),
    }

    send_meta_event('Purchase', event_id, user_data, custom_data)


def _get_order_shipping_data(order):
    if order.shipping_address:
        return {
            'city': order.shipping_address.city,
            'state': order.shipping_address.state,
            'postal_code': order.shipping_address.postal_code,
            'country': order.shipping_address.country,
        }
    return order.guest_shipping_address_data or {}


def _get_order_email(order):
    if order.user and getattr(order.user, 'email', None):
        return order.user.email
    return order.guest_email


def _get_order_phone(order):
    if order.shipping_address and getattr(order.shipping_address, 'phone', None):
        return order.shipping_address.phone
    if order.billing_address and getattr(order.billing_address, 'phone', None):
        return order.billing_address.phone
    return order.guest_phone


def _get_order_first_name(order):
    if order.user and getattr(order.user, 'first_name', None):
        return order.user.first_name
    guest_address = order.guest_shipping_address_data or order.guest_billing_address_data or {}
    if guest_address.get('first_name'):
        return guest_address.get('first_name')
    if guest_address.get('name'):
        return guest_address.get('name', '').split(' ')[0]
    return ''


def _get_order_last_name(order):
    if order.user and getattr(order.user, 'last_name', None):
        return order.user.last_name
    guest_address = order.guest_shipping_address_data or order.guest_billing_address_data or {}
    if guest_address.get('last_name'):
        return guest_address.get('last_name')
    name = guest_address.get('name', '').strip().split(' ')
    return ' '.join(name[1:]) if len(name) > 1 else ''


def _send_event_request(pixel_id, payload, event_name, event_id, max_retries=2):
    """
    Perform the actual HTTP POST to Meta Graph API with retry.

    Runs inside a daemon thread so failures never block the main process.
    """
    url = f'{META_GRAPH_API_URL}/{pixel_id}/events'

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(
                    'Meta CAPI event "%s" (event_id=%s) sent successfully',
                    event_name,
                    event_id,
                )
                return
            else:
                logger.warning(
                    'Meta CAPI event "%s" (event_id=%s) failed — '
                    'HTTP %s: %s (attempt %d/%d)',
                    event_name,
                    event_id,
                    response.status_code,
                    response.text[:300],
                    attempt,
                    max_retries,
                )
        except requests.RequestException as exc:
            logger.warning(
                'Meta CAPI event "%s" (event_id=%s) request error: %s (attempt %d/%d)',
                event_name,
                event_id,
                exc,
                attempt,
                max_retries,
            )

        # Brief back-off before retry
        if attempt < max_retries:
            time.sleep(1)

    logger.error(
        'Meta CAPI event "%s" (event_id=%s) failed after %d attempts',
        event_name,
        event_id,
        max_retries,
    )
