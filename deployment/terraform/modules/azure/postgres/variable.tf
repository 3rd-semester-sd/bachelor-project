variable "primary_server_name" {
  type        = string
  description = "The name of the primary PostgreSQL Server"
}

variable "rg_name" {
  type        = string
  description = "The name of the resource group"
}

variable "rg_location" {
  type        = string
  description = "The location of the resource group"
}

variable "admin_login" {
  type        = string
  description = "The administrator login for the PostgreSQL Server"
}

variable "admin_password" {
  type        = string
  description = "The administrator password for the PostgreSQL Server"
}

variable "sku_name" {
  type        = string
  description = "The SKU name for the PostgreSQL Server"
}

variable "create_replica" {
  type        = bool
  description = "Create a replica server"
}

variable "firewall_rule_name" {
  type        = string
  description = "The name of the firewall rule"
}

variable "create_database" {
  type        = bool
  description = "Create a database"
}

variable "database_name" {
  type        = string
  description = "The name of the database"
}
