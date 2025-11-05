# Unified Product Master List Proposal

This document outlines the proposed architecture and data schema for a unified product master list that will serve both the `tubbyai.com` online store and the `Alicia` Alexa skill.

## 1. Proposed Architecture: Static JSON on a Public Endpoint

To achieve seamless updates and high availability for both systems, the recommended architecture is a **static JSON file hosted on a public, highly-available endpoint**.

| Component | Description | Benefit |
| :--- | :--- | :--- |
| **Product Master List** | A single JSON file containing all product data. | Single source of truth. |
| **Hosting** | A public endpoint (e.g., AWS S3, GitHub Gist, or a simple web server). | High availability, low latency, and simple HTTP access for both the website and the Alexa Lambda function. |
| **Website (`cardy-showcase`)** | Fetches the JSON file on build or at runtime. | Instant product updates without code changes. |
| **Alexa Skill (`Alicia`)** | The AWS Lambda function fetches the JSON file at runtime. | Real-time product information for voice and visual responses. |

This approach is simple, highly scalable, and cost-effective, as it leverages existing infrastructure (AWS Lambda for the skill, and a simple fetch for the website).

## 2. Unified Product Data Schema

The following JSON schema is designed to accommodate the needs of both a visual web store and a voice-first Alexa skill, while focusing on the core requirement of using **AWS affiliate links**.

The master list will be an array of product objects.

| Field Name | Type | Description | Usage in Systems |
| :--- | :--- | :--- | :--- |
| `product_id` | `string` | A unique identifier (e.g., SKU or slug). | Key for internal lookups. |
| `name` | `string` | The full product name. | Website display, Alexa visual display. |
| `short_name` | `string` | A shorter, voice-friendly name (optional). | Alexa voice response (e.g., "the tubbyAI smart feeder"). |
| `description` | `string` | A detailed product description. | Website product page. |
| `voice_description` | `string` | A concise, natural-sounding description. | Alexa voice response (e.g., "a great gift for pet lovers"). |
| `price` | `number` | The product price. | Both systems. |
| `currency` | `string` | The currency code (e.g., "USD"). | Both systems. |
| `affiliate_url` | `string` | **The AWS affiliate link.** | The final link for purchase on both systems. |
| `image_url` | `string` | URL for the product image. | Website display, Alexa APL display. |
| `category` | `string` | The product category. | Filtering and search on both systems. |
| `is_available` | `boolean` | Flag for current availability. | Hide/show product on both systems. |

## 3. Example Product Entry

```json
{
  "product_id": "tubby-feeder-v2",
  "name": "TubbyAI Smart Pet Feeder (v2)",
  "short_name": "smart feeder",
  "description": "The TubbyAI Smart Pet Feeder v2 is the ultimate solution for automated pet feeding, featuring a built-in camera and portion control.",
  "voice_description": "The latest TubbyAI smart pet feeder, perfect for keeping your furry friend on a schedule.",
  "price": 99.99,
  "currency": "USD",
  "affiliate_url": "https://www.amazon.com/dp/B0XXXXXXXXX?tag=yourtag-20",
  "image_url": "https://your-s3-bucket.com/images/feeder-v2.jpg",
  "category": "Pet Supplies",
  "is_available": true
}
```

## Next Steps

1.  Create an initial JSON file with a few example products.
2.  Provide example code snippets for fetching and parsing this JSON in **Python** (for the Alexa Lambda) and **TypeScript** (for the website).
3.  Recommend a hosting solution (e.g., setting up a public S3 bucket or using a GitHub Gist).
