# Order API Documentation

## Overview
Complete Order API implementation supporting both authenticated users and guest checkout.

---

## Endpoints

### 1. List Orders
**GET** `/api/orders/`

Get all orders for the current user (authenticated) or guest (by session).

**Authentication:** Optional
- Authenticated users: Returns their orders
- Guest users: Returns orders created with their session

**Response:**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Orders retrieved successfully",
  "data": {
    "results": [
      {
        "id": 1,
        "order_number": "ORD-1",
        "status": "pending",
        "payment_status": "unpaid",
        "total_items": 3,
        "total_price": "599.97",
        "created_at": "2025-10-27T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 10,
      "per_page": 20,
      "current_page": 1,
      "last_page": 1
    }
  }
}
```

---

### 2. Get Order Details
**GET** `/api/orders/{order_number}/`

Get detailed information about a specific order.

**Authentication:** Optional (must own the order)

**Response:**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Order details retrieved successfully",
  "data": {
    "id": 1,
    "order_number": "ORD-1",
    "status": "pending",
    "payment_status": "unpaid",
    "billing_address": {
      "id": 5,
      "label": "Home",
      "phone": "+1234567890",
      "street": "123 Main St, Apt 4B",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "USA"
    },
    "shipping_address": {
      "id": 6,
      "label": "Office",
      "phone": "+1234567890",
      "street": "456 Oak Ave",
      "city": "Brooklyn",
      "state": "NY",
      "postal_code": "11201",
      "country": "USA"
    },
    "items": [
      {
        "id": 1,
        "product": {
          "id": 5,
          "name": "Mountain Bike",
          "slug": "mountain-bike",
          "primary_image": "https://example.com/media/products/bike.jpg"
        },
        "variant": 10,
        "product_title": "Mountain Bike",
        "variant_sku": "BIKE-XL-RED",
        "variant_attributes": "Size: XL, Color: Red",
        "quantity": 2,
        "unit_price": "249.99",
        "subtotal": "499.98"
      }
    ],
    "subtotal": "599.97",
    "discount": "50.00",
    "shipping_cost": "10.00",
    "total_price": "559.97",
    "total_items": 3,
    "payment_method": "Cash on Delivery",
    "notes": "Please deliver before 5 PM",
    "created_at": "2025-10-27T10:30:00Z",
    "updated_at": "2025-10-27T10:30:00Z"
  }
}
```

---

### 3. Create Order
**POST** `/api/orders/create/`

Create an order from the current cart.

**Authentication:** Optional
- Authenticated users: Can use saved addresses or provide new ones
- Guest users: Must provide complete address details

**Request Body (Authenticated User):**
```json
{
  "billing_address_id": 5,
  "shipping_address_id": 6,
  "discount": 50.00,
  "notes": "Please deliver before 5 PM",
  "payment_method": "cod"
}
```

**Note:** `shipping_cost` is automatically calculated based on shipping city:
- **Dhaka**: 60 TK
- **Outside Dhaka**: 120 TK

You can override by providing `"shipping_cost": <amount>` in the request.

**Request Body (Guest User):**
```json
{
  "guest_billing_address": {
    "label": "Home",
    "phone": "+1234567890",
    "street": "123 Main St, Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  },
  "guest_shipping_address": {
    "label": "Office",
    "phone": "+1234567890",
    "street": "456 Oak Ave",
    "city": "Brooklyn",
    "state": "NY",
    "postal_code": "11201",
    "country": "USA"
  },
  "discount": 0,
  "notes": "",
  "payment_method": "cod"
}
```

**Note:** `shipping_cost` is automatically calculated:
- If shipping city is **"Dhaka"** (case-insensitive): **60 TK**
- If shipping city is **outside Dhaka**: **120 TK**
- You can manually override by including `"shipping_cost": <amount>` in request

**Payment Methods:**
- `cod` - Cash on Delivery
- `card` - Credit/Debit Card
- `bkash` - bKash
- `nagad` - Nagad

**Response:**
```json
{
  "status": true,
  "status_code": 201,
  "message": "Order created successfully",
  "data": {
    "id": 1,
    "order_number": "ORD-1",
    "status": "pending",
    "payment_status": "unpaid",
    "billing_address": {...},
    "shipping_address": {...},
    "items": [...],
    "subtotal": "599.97",
    "discount": "50.00",
    "shipping_cost": "10.00",
    "total_price": "559.97",
    "total_items": 3,
    "payment_method": "Cash on Delivery",
    "notes": "Please deliver before 5 PM",
    "created_at": "2025-10-27T10:30:00Z",
    "updated_at": "2025-10-27T10:30:00Z"
  }
}
```

**Validation:**
- Cart must not be empty
- All items must be in stock
- Addresses are required (either IDs or full details)
- Stock is automatically reduced when order is created
- Cart is cleared after successful order creation

**Shipping Cost Calculation:**
The system automatically calculates shipping cost based on the shipping address city:
- **Dhaka**: 60 TK
- **Outside Dhaka**: 120 TK
- **Override**: Provide `shipping_cost` in request to use custom amount
- **Case-insensitive**: "Dhaka", "dhaka", "DHAKA" all work

Example response with auto-calculated shipping (Dhaka):
```json
{
  "shipping_cost": "60.00",
  "total_price": "609.97"  // subtotal - discount + 60
}
```

Example response with auto-calculated shipping (Outside Dhaka):
```json
{
  "shipping_cost": "120.00",
  "total_price": "669.97"  // subtotal - discount + 120
}
```

---

### 4. Cancel Order
**PATCH** `/api/orders/{order_number}/cancel/`

Cancel an existing order (if eligible).

**Authentication:** Optional (must own the order)

**Conditions:**
- Order status must be `pending` or `processing`
- Order must not be `paid`
- Cannot cancel `shipped`, `delivered`, or already `cancelled` orders

**Response:**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Order cancelled successfully",
  "data": {
    "id": 1,
    "order_number": "ORD-1",
    "status": "cancelled",
    "payment_status": "failed",
    ...
  }
}
```

**Stock Restoration:**
When an order is cancelled, product stock is automatically restored.

---

## Order Status Flow

```
pending → processing → shipped → delivered
   ↓
cancelled
```

**Status Values:**
- `pending` - Order placed, awaiting processing
- `processing` - Order is being prepared
- `shipped` - Order has been shipped
- `delivered` - Order delivered to customer
- `cancelled` - Order cancelled

---

## Payment Status

**Status Values:**
- `unpaid` - Payment not yet received
- `paid` - Payment confirmed
- `failed` - Payment failed
- `refunded` - Payment refunded

---

## Guest User Flow

1. **Browse products** (no auth needed)
2. **Add items to cart** (session-based)
3. **Create order** with guest addresses
4. **View order** using order number + session
5. **Cancel order** if needed (before shipping)

**Session Persistence:**
- Guest orders are tied to browser session
- Clear browser data = lose access to guest orders
- Encourage guests to save order number for tracking

---

## Error Responses

**Cart Empty:**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Cart is empty",
  "data": {}
}
```

**Insufficient Stock:**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Insufficient stock for Mountain Bike. Only 2 available.",
  "data": {}
}
```

**Order Not Found:**
```json
{
  "status": false,
  "status_code": 404,
  "message": "Order not found",
  "data": {}
}
```

**Cannot Cancel:**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Cannot cancel order with status: shipped",
  "data": {}
}
```

---

## Testing Checklist

### Authenticated User
- [ ] Create order with saved billing address
- [ ] Create order with saved shipping address
- [ ] Create order with new addresses (guest_billing_address)
- [ ] View order list
- [ ] View order details
- [ ] Cancel pending order
- [ ] Try to cancel shipped order (should fail)
- [ ] Try to cancel paid order (should fail)

### Guest User
- [ ] Add items to cart without login
- [ ] Create order with complete address details
- [ ] View order list (should show only session orders)
- [ ] View order details
- [ ] Cancel order
- [ ] Clear session and try to access order (should fail)

### Stock Management
- [ ] Verify stock reduces after order creation
- [ ] Verify stock restores after order cancellation
- [ ] Try to order more than available stock (should fail)

### Payment Methods
- [ ] Create order with COD
- [ ] Create order with card (payment integration pending)
- [ ] Create order with bKash
- [ ] Create order with Nagad

---

## Notes

1. **Address Storage for Guests:**
   - Guest addresses are stored but not linked to any user
   - Can be cleaned up periodically via admin

2. **Order Number Format:**
   - Auto-generated: `ORD-{id}`
   - Unique and sequential

3. **Payment Integration:**
   - Payment records are created but not processed
   - Actual payment gateway integration needed for card/mobile payments
   - COD orders are marked as unpaid until delivery

4. **Future Enhancements:**
   - Email notifications
   - Order tracking updates
   - Invoice generation
   - Guest order lookup by email + order number
   - Payment gateway integration
