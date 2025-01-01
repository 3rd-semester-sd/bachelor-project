variable "elasticsearch_name" {
  type        = string
  description = "The name of the Elasticsearch cluster"
}

variable "rg_name" {
  type        = string
  description = "The name of the resource group"
}

variable "rg_location" {
  type        = string
  description = "The location of the resource group"
}

variable "sku_name" {
  type        = string
  description = "The SKU name for the Elasticsearch cluster"
}

variable "elastic_cloud_email_address" {
  type        = string
  description = "The email address for the Elastic Cloud account"
}
