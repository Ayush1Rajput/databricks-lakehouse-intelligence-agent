# Olist Source Data Model

## 1. Overview

The project uses the Brazilian E-Commerce Public Dataset by Olist as
the source dataset for the Databricks Lakehouse Intelligence Agent.

The source layer contains 9 CSV datasets covering:

- customers
- orders
- order items
- payments
- reviews
- products
- sellers
- geolocation
- product category translation

The Lakehouse architecture follows a medallion-style approach:

```text
Source CSV Files
      |
      v
   BRONZE
      |
      | source-faithful ingestion
      v
   SILVER
      |
      | typed + standardized + quality flags
      v
    GOLD
      |
      | business-ready analytical model
      v
 Business Analytics Agent
```

---

# 2. Source Tables

| Source Table | Business Purpose | Approx. Rows | Primary / Business Key |
|---|---|---:|---|
| customers | Customer and location information | 99,441 | customer_id |
| orders | Order lifecycle information | 99,441 | order_id |
| order_items | Products and sellers associated with orders | 112,650 | order_id + order_item_id |
| order_payments | Payment transactions associated with orders | 103,886 | order_id + payment_sequential |
| order_reviews | Customer reviews associated with orders | 99,224 | review_id is not reliably unique |
| products | Product attributes | 32,951 | product_id |
| sellers | Seller information | 3,095 | seller_id |
| geolocation | ZIP-code geographic information | 1,000,163 | no single validated source key |
| category_translation | Portuguese-to-English product category mapping | 71 | product_category_name |

---

# 3. Source Table Grain

Understanding table grain is a core requirement before building the
Silver and Gold layers.

## 3.1 Customers

**Grain:** One source customer record identified by `customer_id`.

Important fields:

- customer_id
- customer_unique_id
- customer_zip_code_prefix
- customer_city
- customer_state

Important observation:

`customer_id` is unique in the source dataset.

`customer_unique_id` is not unique and can map to multiple
`customer_id` records.

Therefore, the two identifiers must not be treated as interchangeable.

### Modeling Rule

- `customer_id` represents the source customer record.
- `customer_unique_id` represents a business-level customer identity candidate.
- Order-level relationships use `customer_id`.
- Repeat-customer analysis can use `customer_unique_id`.

---

## 3.2 Orders

**Grain:** One record per order.

Key:

```text
order_id
```

Important fields:

- order_id
- customer_id
- order_status
- order_purchase_timestamp
- order_approved_at
- order_delivered_carrier_date
- order_delivered_customer_date
- order_estimated_delivery_date

The order table represents the lifecycle of an order from purchase
through fulfillment.

---

## 3.3 Order Items

**Grain:** One product line within an order.

Composite key:

```text
order_id + order_item_id
```

Important fields:

- order_id
- order_item_id
- product_id
- seller_id
- shipping_limit_date
- price
- freight_value

An order can contain multiple order-item records.

---

## 3.4 Order Payments

**Grain:** One payment record/sequence associated with an order.

Composite key:

```text
order_id + payment_sequential
```

Important fields:

- order_id
- payment_sequential
- payment_type
- payment_installments
- payment_value

An order can have multiple payment records.

---

## 3.5 Order Reviews

**Grain:** One source review record.

Important fields:

- review_id
- order_id
- review_score
- review_comment_title
- review_comment_message
- review_creation_date
- review_answer_timestamp

Important data-quality observation:

`review_id` is not reliably unique in the source data.

Duplicate `review_id` values can occur across different orders.

Therefore, `review_id` must not be blindly treated as a standalone
primary key or used as the sole deduplication key.

---

## 3.6 Products

**Grain:** One product.

Key:

```text
product_id
```

Important fields:

- product_id
- product_category_name
- product_name_lenght
- product_description_lenght
- product_photos_qty
- product_weight_g
- product_length_cm
- product_height_cm
- product_width_cm

Some product attributes contain missing values.

---

## 3.7 Sellers

**Grain:** One seller.

Key:

```text
seller_id
```

Important fields:

- seller_id
- seller_zip_code_prefix
- seller_city
- seller_state

---

## 3.8 Geolocation

**Grain:** One geolocation source record.

Important fields:

- geolocation_zip_code_prefix
- geolocation_lat
- geolocation_lng
- geolocation_city
- geolocation_state

The source contains exact duplicate rows and therefore requires
special handling before it can be used as a clean analytical dimension.

---

## 3.9 Category Translation

**Grain:** One product-category translation mapping.

Key:

```text
product_category_name
```

Important fields:

- product_category_name
- product_category_name_english

This table provides the mapping between the source category name and
its English representation.

---

# 4. Source Table Relationships

The source datasets form the following logical relationship structure:

```text
customers
    |
    | customer_id
    v
orders
    |
    +-----------------> order_items
    |                       |
    |                       +---------> products
    |                       |
    |                       +---------> sellers
    |
    +-----------------> order_payments
    |
    +-----------------> order_reviews

products
    |
    +-----------------> category_translation
```

## 4.1 Customer -> Orders

```text
customers.customer_id
        |
        v
orders.customer_id
```

Logical relationship:

```text
customers 1 ---- N orders
```

Source-data observation:

Each `customer_id` in the source dataset is associated with one order
record.

However, this should be treated as a property of this particular
source dataset rather than a universal business rule.

---

## 4.2 Orders -> Order Items

```text
orders.order_id
        |
        v
order_items.order_id
```

Relationship:

```text
orders 1 ---- N order_items
```

An order can contain multiple product lines.

The combination:

```text
order_id + order_item_id
```

is unique in the source data.

---

## 4.3 Products -> Order Items

```text
products.product_id
        |
        v
order_items.product_id
```

Relationship:

```text
products 1 ---- N order_items
```

A product can appear in many order-item records.

---

## 4.4 Sellers -> Order Items

```text
sellers.seller_id
        |
        v
order_items.seller_id
```

Relationship:

```text
sellers 1 ---- N order_items
```

A seller can be associated with many order-item records.

---

## 4.5 Orders -> Payments

```text
orders.order_id
        |
        v
order_payments.order_id
```

Relationship:

```text
orders 1 ---- N order_payments
```

An order can have multiple payment records.

The combination:

```text
order_id + payment_sequential
```

is unique in the source data.

---

## 4.6 Orders -> Reviews

```text
orders.order_id
        |
        v
order_reviews.order_id
```

Relationship:

```text
orders 1 ---- N order_reviews
```

The source data can contain multiple review records associated with
the same order.

`review_id` is not treated as a reliable standalone primary key.

---

## 4.7 Products -> Category Translation

```text
products.product_category_name
        |
        v
category_translation.product_category_name
```

The translation dataset provides an English representation of the
source product category.

The source validation showed that the category mapping key is unique
within the translation dataset.

---

# 5. Source Data Quality Constraints

The source data was profiled before Lakehouse transformation.

The following observations must be preserved in the data model.

## 5.1 Customer Identity

`customer_id` is unique.

`customer_unique_id` is not unique and can map to multiple
`customer_id` values.

Therefore:

- `customer_id` is the source customer-record identifier.
- `customer_unique_id` is a business-level customer identity candidate.
- Repeat-customer analysis should use `customer_unique_id`.
- Order-level joins should use `customer_id`.

---

## 5.2 Review Identifier

`review_id` is not reliably unique.

Duplicate review identifiers were observed across different orders.

Therefore:

- do not blindly deduplicate reviews using `review_id`;
- preserve the source records;
- investigate review identity during Silver-layer modeling;
- document the chosen analytical grain explicitly.

---

## 5.3 Geolocation Duplicates

The geolocation source contains exact duplicate rows.

Therefore, the Bronze layer will preserve the source data while the
Silver layer will define a deterministic treatment for duplicate
geolocation records.

---

## 5.4 Missing Values

Important source-level missing values include:

- order approval timestamp
- carrier delivery timestamp
- customer delivery timestamp
- product category
- product descriptive attributes
- product physical attributes
- review comment title
- review comment message

Missing values will not automatically be converted into fabricated
business values.

---

## 5.5 Order Lifecycle Anomalies

The source contains chronological inconsistencies.

Observed conditions include:

```text
carrier date < approval date
delivery date < carrier date
```

The source also contains:

```text
delivered status + missing customer delivery date
non-delivered status + customer delivery date
```

These records will not be silently deleted.

Instead, Silver will preserve the original timestamps and add explicit
data-quality flags.

---

# 6. Source Data Quality Findings

The profiling and validation phase identified the following findings.

| Finding | Result | Treatment |
|---|---:|---|
| customers.customer_id uniqueness | PASS | Use as source customer key |
| customers.customer_unique_id uniqueness | FAIL | Treat as business identity candidate |
| orders.order_id uniqueness | PASS | Use as order key |
| order_items (order_id, order_item_id) uniqueness | PASS | Use as item key |
| payments (order_id, payment_sequential) uniqueness | PASS | Use as payment key |
| reviews.review_id uniqueness | FAIL | Do not use alone as PK |
| products.product_id uniqueness | PASS | Use as product key |
| sellers.seller_id uniqueness | PASS | Use as seller key |
| category translation key uniqueness | PASS | Use as translation mapping key |
| Foreign-key relationships | PASS | Preserve relationships |
| Geolocation exact duplicates | Present | Handle deterministically in Silver |
| Order timeline anomalies | Present | Preserve + flag |
| Missing source values | Present | Preserve/standardize in Silver |

---

# 7. Order Lifecycle Quality Rules

The order lifecycle contains the following conceptual timestamps:

```text
order_purchase_timestamp
        |
        v
order_approved_at
        |
        v
order_delivered_carrier_date
        |
        v
order_delivered_customer_date
```

The estimated delivery date is used as a reference point:

```text
order_estimated_delivery_date
```

The source data does not always satisfy the expected chronological
ordering.

Therefore, Silver will not overwrite the original timestamps.

Instead, the following derived quality flags will be created.

---

## 7.1 Carrier Before Approval

Condition:

```text
carrier_before_approval =
    order_delivered_carrier_date < order_approved_at
```

Observed records:

```text
1,359
```

The observed records contained:

- 1,350 delivered orders
- 9 shipped orders

All observed records had a populated approval timestamp.

Treatment:

```text
preserve source timestamps
+
carrier_before_approval = true
```

---

## 7.2 Delivery Before Carrier

Condition:

```text
delivery_before_carrier =
    order_delivered_customer_date < order_delivered_carrier_date
```

Observed records:

```text
23
```

All observed records were marked as delivered.

Treatment:

```text
preserve source timestamps
+
delivery_before_carrier = true
```

---

## 7.3 Delivered Without Customer Delivery Date

Condition:

```text
order_status = 'delivered'
AND order_delivered_customer_date IS NULL
```

Observed records:

```text
8
```

Treatment:

```text
preserve source record
+
delivered_without_date = true
```

No delivery timestamp will be fabricated.

---

## 7.4 Non-Delivered With Customer Delivery Date

Condition:

```text
order_status != 'delivered'
AND order_delivered_customer_date IS NOT NULL
```

Observed records:

```text
6
```

All observed records had `canceled` status.

Treatment:

```text
preserve source record
+
non_delivered_with_date = true
```

---

## 7.5 Combined Timeline Anomaly

A record is considered to have a timeline anomaly when either of the
following conditions is true:

```text
carrier_before_approval
OR
delivery_before_carrier
```

Observed records:

```text
1,382
```

This flag indicates a source-data timeline inconsistency.

It does not automatically mean that the entire order record is invalid.

---

# 8. Bronze Layer Design

The Bronze layer is the raw ingestion layer.

Its primary objective is to preserve the source data faithfully and
provide traceability.

## Bronze Principles

1. Preserve source records.
2. Avoid business-rule transformations.
3. Retain source column meaning.
4. Add ingestion metadata where appropriate.
5. Keep source lineage observable.
6. Do not silently remove anomalies.
7. Do not fabricate missing values.

---

## 8.1 Bronze Tables

The initial Bronze layer will contain the following logical tables:

```text
bronze_customers
bronze_orders
bronze_order_items
bronze_order_payments
bronze_order_reviews
bronze_products
bronze_sellers
bronze_geolocation
bronze_category_translation
```

The Bronze layer mirrors the source datasets as closely as practical.

---

# 9. Silver Layer Design

The Silver layer is the cleaned, typed, standardized and quality-aware
layer.

Silver transformations will be deterministic and documented.

The Silver layer will:

- standardize data types;
- normalize timestamp columns;
- standardize column naming where appropriate;
- preserve source identifiers;
- create derived business fields;
- create data-quality flags;
- handle known duplicate patterns;
- preserve source anomalies rather than silently deleting them.

---

## 9.1 Silver Orders

Target:

```text
silver_orders
```

Core fields:

```text
order_id
customer_id
order_status
order_purchase_timestamp
order_approved_at
order_delivered_carrier_date
order_delivered_customer_date
order_estimated_delivery_date
```

Derived fields:

```text
delivery_delay_days
is_late_delivery
carrier_before_approval
delivery_before_carrier
delivered_without_date
non_delivered_with_date
timeline_anomaly
```

### Delivery Delay

Conceptually:

```text
delivery_delay_days =
    delivered_customer_date - estimated_delivery_date
```

This metric is only calculated when the required dates are available.

### Late Delivery

Conceptually:

```text
is_late_delivery =
    delivery_delay_days > 0
```

A missing delivery date does not automatically mean the order was late.

---

## 9.2 Silver Customers

Target:

```text
silver_customers
```

Core fields:

```text
customer_id
customer_unique_id
customer_zip_code_prefix
customer_city
customer_state
```

The distinction between `customer_id` and `customer_unique_id` will be
preserved.

---

## 9.3 Silver Order Items

Target:

```text
silver_order_items
```

Core fields:

```text
order_id
order_item_id
product_id
seller_id
shipping_limit_date
price
freight_value
```

The grain remains:

```text
one row per order item
```

---

## 9.4 Silver Payments

Target:

```text
silver_order_payments
```

Core fields:

```text
order_id
payment_sequential
payment_type
payment_installments
payment_value
```

The grain remains:

```text
one row per payment sequence
```

---

## 9.5 Silver Reviews

Target:

```text
silver_order_reviews
```

Core fields:

```text
review_id
order_id
review_score
review_comment_title
review_comment_message
review_creation_date
review_answer_timestamp
```

The source review identity issue will be preserved and explicitly
documented.

No blind `drop_duplicates()` operation will be applied solely using
`review_id`.

---

## 9.6 Silver Products

Target:

```text
silver_products
```

Core fields:

```text
product_id
product_category_name
product_name_lenght
product_description_lenght
product_photos_qty
product_weight_g
product_length_cm
product_height_cm
product_width_cm
```

Missing product attributes will remain explicitly missing unless a
documented transformation rule is introduced.

---

## 9.7 Silver Sellers

Target:

```text
silver_sellers
```

Core fields:

```text
seller_id
seller_zip_code_prefix
seller_city
seller_state
```

---

## 9.8 Silver Geolocation

Target:

```text
silver_geolocation
```

The Silver layer will define a deterministic strategy for handling
exact duplicate geolocation rows.

The strategy must avoid arbitrary selection when duplicate records
contain conflicting geographic attributes.

---

## 9.9 Silver Category Translation

Target:

```text
silver_category_translation
```

Core fields:

```text
product_category_name
product_category_name_english
```

---

# 10. Gold Layer Design

The Gold layer is the business-facing analytical layer.

Unlike Bronze and Silver, Gold will not simply mirror the source files.

Gold tables will be designed around analytical use cases and business
questions.

The primary analytical model will follow a star-schema pattern.

---

# 11. Gold Star Schema

Initial conceptual model:

```text
                         dim_customer
                              |
                              |
                              v
dim_date ----------------> fact_sales <---------------- dim_product
                              |
                              |
                              v
                         dim_seller
                              |
                              |
                              v
                         dim_region
```

The exact physical schema will be finalized after the Silver layer
implementation and metric validation.

---

## 11.1 Fact Sales

Target:

```text
gold_fact_sales
```

Proposed grain:

```text
one row per order item
```

Potential keys:

```text
order_id
order_item_id
```

Potential dimensions:

```text
customer_key
product_key
seller_key
date_key
region_key
```

Potential measures:

```text
item_price
freight_value
gross_item_value
```

The fact table will provide the foundation for business analytics
such as sales, order value, product performance and seller performance.

---

## 11.2 Customer Dimension

Target:

```text
gold_dim_customer
```

Potential attributes:

```text
customer_key
customer_id
customer_unique_id
customer_city
customer_state
customer_zip_code_prefix
```

The dimension will support customer-level analytical questions.

---

## 11.3 Product Dimension

Target:

```text
gold_dim_product
```

Potential attributes:

```text
product_key
product_id
product_category_name
product_category_name_english
product_weight_g
product_length_cm
product_height_cm
product_width_cm
product_photos_qty
```

---

## 11.4 Seller Dimension

Target:

```text
gold_dim_seller
```

Potential attributes:

```text
seller_key
seller_id
seller_city
seller_state
seller_zip_code_prefix
```

---

## 11.5 Date Dimension

Target:

```text
gold_dim_date
```

Potential attributes:

```text
date_key
calendar_date
year
quarter
month
month_name
week
day
day_name
```

The date dimension will allow consistent time-based analytics.

---

## 11.6 Region Dimension

Target:

```text
gold_dim_region
```

Potential attributes may include:

```text
region_key
state
city
zip_code_prefix
```

The exact structure will depend on the finalized geolocation
transformation.

---

# 12. Business Metrics

The Gold layer will support business metrics required by the
Lakehouse Intelligence Agent.

Initial candidate metrics include:

```text
revenue
orders
average_order_value
freight_value
product_sales
seller_sales
customer_sales
late_delivery_rate
average_delivery_delay
review_score
```

Additional metrics may be introduced after the Gold model is validated.

Metric definitions must be documented before being exposed through the
Agent.

---

# 13. Analytical Grain Rules

The project will explicitly distinguish between different grains.

```text
orders
    = one row per order

order_items
    = one row per order item

payments
    = one row per order payment sequence

reviews
    = one source review record

products
    = one row per product

sellers
    = one row per seller

fact_sales
    = one row per order item
```

This distinction is important because incorrect joins between
different grains can produce double-counting.

For example:

```text
order
  x
order_items
  x
payments
```

can multiply records if payments are joined directly to item-level
sales without appropriate aggregation.

Therefore, Gold metric definitions must explicitly account for table
grain.

---

# 14. Data Quality Strategy

Data-quality handling follows three principles:

## Preserve

Raw source information remains available in Bronze.

## Flag

Known quality conditions are represented explicitly in Silver.

## Transform

Only documented and deterministic transformations are applied.

The project will avoid silently deleting records simply because they
contain anomalies.

---

# 15. Data Lineage

The intended lineage is:

```text
Olist CSV
   |
   v
Bronze Delta Table
   |
   v
Silver Delta Table
   |
   v
Gold Analytical Table
   |
   v
MCP Tool
   |
   v
AI Agent
   |
   v
Natural-Language Answer
```

The Agent should be able to trace an analytical answer back through
the Gold and Silver layers when required.

---

# 16. Agent-Oriented Data Design

The Gold layer is designed specifically for the future
Lakehouse Intelligence Agent.

The Agent should not need to understand every raw source-table
complexity for common business questions.

For example, a user may ask:

```text
"Which product categories generated the highest revenue?"
```

The Agent should primarily discover and query business-ready Gold
tables rather than manually reconstructing the entire source model.

Similarly:

```text
"How many orders were delivered late last month?"
```

should use the documented delivery and lateness definitions rather
than inventing a new calculation.

---

# 17. MCP and Data Model Boundary

MCP tools will expose controlled access to the analytical model.

Conceptually:

```text
AI Agent
   |
   v
MCP Server
   |
   +-- search_schema()
   +-- get_table_schema()
   +-- get_business_metrics()
   +-- validate_sql()
   +-- execute_readonly_sql()
   +-- explain_query()
          |
          v
   Gold / Silver Databricks Tables
```

The Agent should discover table and column information through
controlled MCP tools rather than relying entirely on hardcoded schema
knowledge.

---

# 18. Governance Considerations

The analytical data model must support governed access.

Initial principles:

- read-only analytical access;
- least-privilege permissions;
- controlled SQL execution;
- no destructive SQL operations through the Agent;
- explicit table and column access;
- auditability of Agent queries;
- protection of sensitive fields where applicable;
- Unity Catalog as the governance layer.

The Agent will not be given unrestricted database access.

---

# 19. Data Modeling Decisions

The following decisions are currently established:

1. Bronze preserves source data.
2. Silver contains standardized and quality-aware data.
3. Gold contains business-facing analytical structures.
4. `customer_id` and `customer_unique_id` remain distinct.
5. `review_id` is not assumed to be a standalone primary key.
6. Geolocation duplicates require deterministic Silver handling.
7. Order lifecycle anomalies are preserved and flagged.
8. Original timestamps are not overwritten.
9. Gold fact grain is initially defined as one row per order item.
10. Business metrics must have explicit definitions.
11. Grain must be considered before joins and aggregations.
12. MCP tools should expose governed analytical access rather than
    unrestricted database operations.

---

# 20. Implementation Sequence

The data-model implementation will follow this sequence:

```text
1. Source CSV validation
        |
        v
2. Bronze ingestion
        |
        v
3. Silver data types and standardization
        |
        v
4. Silver data-quality flags
        |
        v
5. Silver duplicate-handling rules
        |
        v
6. Gold star schema
        |
        v
7. Gold business metrics
        |
        v
8. Metric validation
        |
        v
9. MCP schema discovery
        |
        v
10. MCP SQL tools
        |
        v
11. Agent integration
```

---

# 21. Current Status

Completed:

- source dataset profiling
- key validation
- foreign-key validation
- cardinality analysis
- customer identity investigation
- review anomaly investigation
- data-quality profiling
- order lifecycle validation
- order lifecycle anomaly investigation
- source data model definition

Next:

- Bronze architecture implementation
- Databricks catalog/schema design
- Bronze ingestion
- Silver transformation design
- Silver quality flags
- Gold star-schema implementation
- business metric definitions
- MCP integration
- Agent integration